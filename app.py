import os
import json
import random
import traceback
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from components.inputs import get_user_input
from components.display import display_recipe
from utils.genai_client import GenAIRecipeGenerator
from utils.image_fetcher import UnsplashImageFetcher
from utils.storage import Storage


def normalize_ingredients(raw_ings):
    """
    Normalize the ingredients list to a consistent format.

    :param raw_ings: List of ingredients, which can be strings or dicts.
    :return: List of strings representing the normalized ingredients.
    """
    out = []
    for i in raw_ings:
        if isinstance(i, str):
            out.append(i)
        elif isinstance(i, dict):
            txt = i.get("item") or i.get("name") or i.get("text")
            out.append(txt if isinstance(txt, str) else json.dumps(i))
        else:
            out.append(str(i))
    return out


# ─── Page config ────────────────────────────────
st.set_page_config(
    page_title="PantryPal – AI Recipe Generator",
    page_icon="🍲",
    layout="wide",
)

# ─── Global CSS & FontAwesome ────────────────────
st.markdown(
    """
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
      crossorigin="anonymous"
    >
    <style>
      h1,h2,h3 { font-family:'Segoe UI',sans-serif; font-weight:600; }
      .stApp { padding:1rem 2rem; }
      .stSidebar { padding:1rem; }
      .stButton>button:hover { opacity:0.9; }
    </style>
    """,
    unsafe_allow_html=True
)

# ─── Load env & init clients ─────────────────────
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_AI_API_KEY")
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

if not GOOGLE_KEY:
    st.sidebar.error("🔑 Missing GOOGLE_AI_API_KEY — AI disabled.")
if not UNSPLASH_KEY:
    st.sidebar.error("🖼️ Missing UNSPLASH_ACCESS_KEY — Images disabled.")

ai_gen = GenAIRecipeGenerator(GOOGLE_KEY) if GOOGLE_KEY else None
img_fetch = UnsplashImageFetcher(UNSPLASH_KEY) if UNSPLASH_KEY else None
storage = Storage(Path("recipe_history.json"))

# ─── Sidebar inputs ──────────────────────────────
ingredients, restrictions, servings, do_generate, do_clear, do_random = get_user_input()

# ─── Load history once ────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = storage.load_history()

try:
    # ── Clear history ──────────────────────────────
    if do_clear:
        storage.clear_history()
        st.session_state.history = []
        st.session_state.pop("current", None)
        st.session_state.pop("temp", None)

    # ── Surprise Me! ───────────────────────────────
    if do_random:
        if not ai_gen:
            st.error("⚠️ Cannot surprise — AI key missing.")
        else:
            with st.spinner("🔀 Generating a surprise recipe…"):
                # Empty ingredients => AI invents them; still honor restrictions & servings
                recipe = ai_gen.generate([], restrictions, servings)
                recipe_ings = normalize_ingredients(recipe["ingredients"])
                recipe["ingredients"] = recipe_ings
                images = img_fetch.fetch_images(recipe["name"], n=5) if img_fetch else []
                st.session_state.temp = {
                    "recipe": recipe,
                    "recipe_ings": recipe_ings,
                    "image_options": images,
                    "user_ings": []  # no pantry constraint
                }
                st.session_state.pop("current", None)

    # ── Generate + stage images ────────────────────
    if do_generate:
        if not ingredients:
            st.warning("✏️ Please add at least one ingredient.")
        elif not ai_gen:
            st.error("⚠️ Cannot generate: missing AI key.")
        else:
            with st.spinner("👩‍🍳 Generating your recipe…"):
                recipe = ai_gen.generate(ingredients, restrictions, servings)
                recipe_ings = normalize_ingredients(recipe["ingredients"])
                recipe["ingredients"] = recipe_ings
                images = img_fetch.fetch_images(recipe["name"], n=5) if img_fetch else []
                st.session_state.temp = {
                    "recipe": recipe,
                    "recipe_ings": recipe_ings,
                    "image_options": images,
                    "user_ings": ingredients
                }
                st.session_state.pop("current", None)

    # ── If a recipe is current, show it ───────────
    if "current" in st.session_state:
        cur = st.session_state.current
        st.title(f"🍲 {cur['recipe']['name']}")
        display_recipe(
            cur["recipe"],
            cur["recipe"]["ingredients"],
            cur["image_url"],
            cur["user_ings"],
            cur["substitutions"],
            key_prefix="current"
        )

    # ── Else if staging exists, show image picker ──
    elif "temp" in st.session_state:
        temp = st.session_state.temp
        st.header("🖼️ Pick a Hero Image")
        opts = temp["image_options"]

        if not opts:
            st.info("⚠️ No images found—continuing without one.")
            choice, confirmed = None, True
        else:
            # Display all options side-by-side
            cols = st.columns(min(len(opts), 3))
            for idx, url in enumerate(opts):
                with cols[idx % len(cols)]:
                    st.image(url, use_container_width=True)
                    st.caption(f"Option {idx + 1}")

            # Single-click confirm UI
            choice = st.radio(
                "Select an image:",
                options=list(range(len(opts))),
                format_func=lambda i: f"Option {i + 1}",
                index=0
            )
            confirmed = st.button("Confirm Image")

        # If not confirmed yet, stop here
        if not confirmed:
            st.stop()

        # Finalize on the one click
        image_url = opts[choice] if (opts and choice is not None) else ""
        recipe = temp["recipe"]
        recipe_ings = temp["recipe_ings"]
        user_ings = temp["user_ings"]
        missing = [
            ing for ing in recipe_ings
            if ing.lower() not in {u.lower() for u in user_ings}
        ]
        subs = ai_gen.get_substitutions(missing) if (ai_gen and missing) else {}
        storage.save_recipe(recipe, image_url, user_ings, subs)
        st.session_state.history = storage.load_history()
        st.session_state.current = st.session_state.history[-1]
        st.session_state.pop("temp")

    # ── Else show history ───────────────────────────
    else:
        st.header("🗂️ Recipe History")
        for entry in reversed(st.session_state.history):
            rid = entry["id"]
            name = entry["recipe"]["name"]
            ts = entry["timestamp"][:19].replace("T", " ")
            with st.expander(f"{name} — {ts}", expanded=False):
                display_recipe(
                    entry["recipe"],
                    entry.get("recipe_ings", entry["recipe"]["ingredients"]),
                    entry["image_url"],
                    entry["user_ings"],
                    entry["substitutions"],
                    key_prefix=f"hist_{rid}"
                )
                if st.button("🗑️ Delete Recipe", key=f"del_{rid}"):
                    storage.delete_recipe(rid)
                    st.session_state.history = storage.load_history()
                    st.stop()

except Exception as e:
    st.error("🚨 Unexpected error:")
    st.text(str(e))
    st.text(traceback.format_exc())
