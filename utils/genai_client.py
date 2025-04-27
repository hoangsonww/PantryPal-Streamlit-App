import json

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
        sys = (
            "You are a world-class chef AI.  "
            "Given ingredients, dietary restrictions, and number of servings,  "
            "respond with _ONLY_ JSON with these keys:\n"
            "  • name: string\n"
            "  • ingredients: array of {item: string, amount: string}\n"
            "  • instructions: array of strings\n"
            "  • nutrition: object mapping nutrient names to strings\n"
            "  • shopping_list: array of strings\n"
        )
        prompt = (
            f"Ingredients: {', '.join(ings)}\n"
            f"Restrictions: {', '.join(restrs) or 'None'}\n"
            f"Servings: {serves}\n\n"
            "Output _ONLY_ the JSON object."
        )
        resp = self.client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys,
                temperature=0.8,
                top_p=0.95,
                top_k=64,
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
        # Ask for a direct mapping from ingredient→[subs…]
        sys = (
            "You are a culinary expert.  "
            "Given a list of missing ingredients, output _ONLY_ a JSON object "
            "where each key is the missing ingredient (string) and its value is an "
            "array of exactly two substitute ingredient names (strings).  "
            "Example:\n"
            '{ "Spaghetti": ["Linguine","Fettuccine"], "Tomato": ["Cherry tomatoes","Crushed tomatoes"] }\n'
            "Do not wrap it in any other structure or text."
        )
        prompt = f"Missing ingredients: {', '.join(missing)}.\nOutput _ONLY_ the JSON mapping."
        resp = self.client.models.generate_content(
            model="gemini-1.5-flash",
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
        return json.loads(resp.text)
