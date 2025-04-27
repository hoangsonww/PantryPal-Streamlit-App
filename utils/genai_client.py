import json
import random
import re
from datetime import datetime

from google import genai
from google.genai import types


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

        resp = self.client.models.generate_content(
            model="gemini-1.5-flash",
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
        return json.loads(resp.text)

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
        resp = self.client.models.generate_content(
            model="gemini-2.0-flash-lite",
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

        text = resp.text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # attempt to extract the first {...} block
            m = re.search(r"(\{.*\})", text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(1))
                except json.JSONDecodeError:
                    pass
            # fallback to empty map
            return {}
