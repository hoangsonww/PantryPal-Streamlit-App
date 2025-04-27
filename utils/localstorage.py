import json
import uuid
from datetime import datetime

from streamlit_local_storage import LocalStorage

_local = LocalStorage()


class Storage:
    """
    Class to manage the local storage of recipe history.
    """

    def __init__(self):
        """
        Initialize the storage manager using browser localStorage.
        """
        # Nothing to initialize beyond the LocalStorage instance
        pass

    def load_history(self) -> list:
        """
        Load the recipe history from localStorage.

        :return: A list of recipe entries.
        """
        raw = _local.getItem("pantrypal_history") or "[]"
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []

    def save_recipe(self, recipe, image_url, user_ings, substitutions):
        """
        Save a recipe entry to the history.
        This includes the recipe details, image URL, user ingredients, and substitutions.
        The entry is appended to the existing history.
        Each entry is assigned a unique ID and timestamp.
        The history is saved back to localStorage.

        :param recipe: The recipe dictionary containing details like name, ingredients, instructions, and nutrition.
        :param image_url: The URL of the hero image for the recipe.
        :param user_ings: The list of ingredients provided by the user.
        :param substitutions: The substitutions for ingredients, either as a list of dicts or a dict mapping.
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
        _local.setItem("pantrypal_history", json.dumps(history, indent=2))

    def delete_recipe(self, entry_id: str):
        """
        Delete a recipe entry from the history.
        This method removes the entry with the specified ID from the history.
        The updated history is saved back to localStorage.
        If the entry ID is not found, no action is taken.
        The history is saved back to localStorage.

        :param entry_id: The ID of the recipe entry to delete.
        """
        history = self.load_history()
        history = [e for e in history if e["id"] != entry_id]
        _local.setItem("pantrypal_history", json.dumps(history, indent=2))

    def clear_history(self):
        """
        Clear the entire recipe history.
        This method removes all entries from the history.
        The history is saved back to localStorage as an empty list.

        :return: The updated recipe history (empty list).
        """
        _local.deleteAll()
