import requests
import streamlit as st


class UnsplashImageFetcher:
    """
    Fetches images from Unsplash based on a search query.
    """

    def __init__(self, access_key: str):
        """
        Initialize the Unsplash client with the provided access key.

        :param access_key: The access key for Unsplash API.
        """
        self.access_key = access_key

    @st.cache_data(ttl=3600)
    def fetch_images(_self, query: str, n: int = 5) -> list[str]:
        """
        Fetches images from Unsplash based on a search query.
        Uses caching to avoid repeated API calls.

        :param query: The search query for the images.
        :param n: The number of images to fetch.
        :return: The list of image URLs.
        """
        if not _self.access_key:
            return []
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": f"{query} recipe food",
            "per_page": n,
            "client_id": _self.access_key,
        }
        r = requests.get(url, params=params, timeout=5)
        if r.ok:
            return [res["urls"]["regular"] for res in r.json().get("results", [])]
        return []
