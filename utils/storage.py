import json
import uuid
from datetime import datetime
from pathlib import Path


class Storage:
    """
    Class to manage the local storage of recipe history.
    """

    def __init__(self, path="recipe_history.json"):
        """
        Initialize the storage with the given path.

        :param path: The path to the JSON file where recipe history is stored.
        """
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text("[]")

    def load_history(self) -> list:
        """
        Load the recipe history from the JSON file.

        :return: A list of recipe entries.
        """
        return json.loads(self.path.read_text())

    def save_recipe(self, recipe, image_url, user_ings, substitutions):
        """
        Save a recipe entry to the history.
        This includes the recipe details, image URL, user ingredients, and substitutions.
        The entry is appended to the existing history.
        Each entry is assigned a unique ID and timestamp.
        The history is saved back to the JSON file.

        :param recipe: The recipe dictionary containing details like name, ingredients, instructions, and nutrition.
        :param image_url: The URL of the hero image for the recipe.
        :param user_ings: The list of ingredients provided by the user.
        :param substitutions: The substitutions for ingredients, either as a list of dicts or a dict mapping.
        :return: The updated recipe history.
        """
        history = self.load_history()
        entry = {
            "id": uuid.uuid4().hex,
            # Local time instead of UTC
            "timestamp": datetime.now().isoformat(),
            "recipe": recipe,
            "recipe_ings": recipe.get("ingredients", []),
            "image_url": image_url,
            "user_ings": user_ings,
            "substitutions": substitutions,
        }
        history.append(entry)
        self.path.write_text(json.dumps(history, indent=2))

    def delete_recipe(self, entry_id: str):
        """
        Delete a recipe entry from the history.
        This method removes the entry with the specified ID from the history.
        The updated history is saved back to the JSON file.
        If the entry ID is not found, no action is taken.
        The history is saved back to the JSON file.

        :param entry_id: The ID of the recipe entry to delete.
        :return: The updated recipe history.
        """
        history = self.load_history()
        history = [e for e in history if e["id"] != entry_id]
        self.path.write_text(json.dumps(history, indent=2))

    def clear_history(self):
        """
        Clear the entire recipe history.
        This method removes all entries from the history.
        The history is saved back to the JSON file as an empty list.

        :return: The updated recipe history (empty list).
        """
        self.path.write_text("[]")
