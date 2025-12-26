import json
import random
import re
import time
from datetime import datetime

from google import genai
from google.genai import types


_PRO_MODEL_RE = re.compile(r"(^|[-/])pro($|[-])", re.IGNORECASE)


class ModelParseError(ValueError):
    pass


class GenAIRecipeGenerator:
    """
    Class to interact with the Google GenAI API for recipe generation and ingredient substitution.
    """

    def __init__(self, api_key: str):
        """
        Initialize the GenAI client with the provided API key.

        :param api_key: API key for Google GenAI.
        """
        self.client = genai.Client(api_key=api_key)
        self._model_cache = []
        self._model_cache_at = 0.0
        self._model_index = 0

    def _get_model_attr(self, model, *names):
        for name in names:
            if isinstance(model, dict) and name in model:
                return model[name]
            if hasattr(model, name):
                return getattr(model, name)
        return None

    def _normalize_model_name(self, name: str) -> str:
        if name.startswith("models/"):
            return name.split("/", 1)[1]
        return name

    def _list_gemini_models(self) -> list[str]:
        raw = self.client.models.list()
        if isinstance(raw, dict):
            models = raw.get("models", [])
        elif hasattr(raw, "models"):
            models = raw.models
        else:
            models = raw
        candidates = []
        for model in list(models):
            name = self._get_model_attr(model, "name")
            if not name:
                continue
            if not name.startswith("models/gemini-") and not name.startswith("gemini-"):
                continue
            normalized = self._normalize_model_name(name)
            name_lower = normalized.lower()
            if "embedding" in name_lower:
                continue
            if _PRO_MODEL_RE.search(name_lower):
                continue
            supported = self._get_model_attr(
                model, "supported_generation_methods", "supportedGenerationMethods"
            )
            if supported:
                supported_lower = {str(method).lower() for method in supported}
                if (
                    "generatecontent" not in supported_lower
                    and "generate_content" not in supported_lower
                ):
                    continue
            candidates.append(normalized)
        seen = set()
        filtered = []
        for name in candidates:
            if name in seen:
                continue
            seen.add(name)
            filtered.append(name)
        return filtered

    def _get_available_models(self) -> list[str]:
        now = time.monotonic()
        if not self._model_cache or now - self._model_cache_at > 1800:
            try:
                models = self._list_gemini_models()
                if models:
                    self._model_cache = models
            except Exception:
                pass
            self._model_cache_at = now
        if self._model_cache:
            return list(self._model_cache)
        return ["gemini-1.5-flash", "gemini-2.0-flash-lite"]

    def _request_with_failover(self, request_fn, response_fn):
        models = self._get_available_models()
        if not models:
            raise RuntimeError("No Gemini models available for generation.")
        start = self._model_index % len(models)
        last_exc = None
        for offset in range(len(models)):
            model = models[(start + offset) % len(models)]
            try:
                response = request_fn(model)
                result = response_fn(response)
                self._model_index = (start + offset + 1) % len(models)
                return result
            except Exception as exc:
                last_exc = exc
        if last_exc:
            raise last_exc
        raise RuntimeError("Gemini request failed without a captured exception.")

    def generate(self, ings, restrs, serves):
        """
        Generate a recipe based on the provided ingredients, dietary restrictions, and number of servings.

        :param ings: The list of ingredients.
        :param restrs: The list of dietary restrictions.
        :param serves: The number of servings.
        :return: The generated recipe as a JSON object.
        """
        # Strict JSON‐only system prompt
        sys = (
            "You are a world-class chef AI.  "
            "Given ingredients, dietary restrictions, and number of servings, RESPOND WITH STRICTLY VALID JSON AND NOTHING ELSE.  "
            "Your output MUST be parseable by json.loads without error.  "
            "Use double quotes for all keys and string values.  "
            "Do NOT include single quotes, trailing commas, comments, code fences, markdown, or any extra text.  "
            "Output JSON must have exactly these keys:\n"
            '  "name": string,\n'
            '  "ingredients": [{"item": string, "amount": string}, ...],\n'
            '  "instructions": [string, ...],\n'
            '  "nutrition": {string: string, ...},\n'
            '  "shopping_list": [string, ...]\n'
            "If the user gives no ingredients, generate a completely random recipe with a unique never-before-seen name."
        )

        # Detect “Surprise me!” calls (no ingredients)
        is_random = len(ings) == 0
        if is_random:
            temp = 1.0
            top_p = 1.0
            top_k = 0

            # Pick a random cuisine & theme
            cuisines = [
                "Moroccan",
                "Korean",
                "Peruvian",
                "Nordic",
                "Caribbean",
                "Ethiopian",
                "Thai",
                "Middle Eastern",
                "Brazilian",
                "Japanese",
            ]
            themes = [
                "one-pot wonder",
                "street-food twist",
                "fusion of two cuisines",
                "deconstructed comfort food",
                "farm-to-table special",
                "seasonal harvest stew",
                "spiced-up breakfast",
                "vegan gourmet delight",
            ]
            cuisine = random.choice(cuisines)
            theme = random.choice(themes)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

            sys += (
                f"  For this random recipe, theme: {theme} from {cuisine} cuisine.  "
                f"Include the timestamp {timestamp} in your creative process.  "
                "Assign a never-before-seen name."
            )
        else:
            temp = 0.8
            top_p = 0.95
            top_k = 64

        prompt = (
            f"Ingredients: {', '.join(ings) if ings else 'None'}\n"
            f"Restrictions: {', '.join(restrs) or 'None'}\n"
            f"Servings: {serves}\n\n"
            "Output ONLY the JSON object."
        )

        def request(model):
            return self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=sys,
                    temperature=temp,
                    top_p=top_p,
                    top_k=top_k,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                ),
            )

        def parse_response(resp):
            return json.loads(resp.text)

        return self._request_with_failover(request, parse_response)

    def get_substitutions(self, missing: list[str]) -> dict[str, list[str]]:
        """
        Generate a mapping of missing ingredients to their substitutes.
        This method uses the GenAI API to find substitutes for missing ingredients.

        :param missing: The list of missing ingredients.
        :return: The mapping of missing ingredients to their substitutes as a JSON object.
        """
        sys = (
            "You are a culinary expert.  "
            "Given a list of missing ingredients, output ONLY a valid JSON object "
            "with double-quoted keys and string values.  "
            "Each key is a missing ingredient, each value is an array of exactly two substitute ingredient names.  "
            "Example:\n"
            '{ "Spaghetti": ["Linguine","Fettuccine"], "Tomato": ["Cherry tomatoes","Crushed tomatoes"] }\n'
            "Do not include any extra text or formatting."
        )
        prompt = (
            f"Missing ingredients: {', '.join(missing)}.\nOutput ONLY the JSON mapping."
        )

        def request(model):
            return self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=sys,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=32,
                    max_output_tokens=512,
                    response_mime_type="application/json",
                ),
            )

        def parse_response(resp):
            text = resp.text
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                m = re.search(r"(\{.*\})", text, re.DOTALL)
                if m:
                    try:
                        return json.loads(m.group(1))
                    except json.JSONDecodeError:
                        pass
                raise ModelParseError("Gemini substitutions response was not valid JSON.")

        try:
            return self._request_with_failover(request, parse_response)
        except ModelParseError:
            return {}
