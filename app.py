import json
import os
import random
import re
import traceback
from datetime import datetime
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from components.display import display_recipe
from components.inputs import get_user_input
from utils.genai_client import GenAIRecipeGenerator
from utils.image_fetcher import UnsplashImageFetcher
from utils.storage import Storage


def normalize_ingredients(raw_ings):
    """
    Normalize the ingredients list to a consistent format.

    :param raw_ings: The raw ingredients list, which can contain strings or dictionaries.
    :return: A list of normalized ingredient strings.
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


def render_analysis():
    """
    Load the recipe history and render three interactive Altair charts:
      1) Nutrition boxplots
      2) Recipes generated over time (line)
      3) Top ingredients by frequency (bar)

    This function is called when the user clicks the "View Analytics" button in the sidebar.

    :return: None
    """
    history_path = Path("recipe_history.json")
    if not history_path.exists():
        st.error("📈 No recipe history found to analyze.")
        return

    with open(history_path) as f:
        history = json.load(f)

    # ─── Nutrition DataFrame ───────────────────────────────────
    nutri_rows = []
    for entry in history:
        nutri = entry.get("recipe", {}).get("nutrition", {}) or {}
        for key, val in nutri.items():
            m = re.match(r"^\s*([\d\.]+)", val or "")
            if m:
                nutri_rows.append(
                    {
                        "name": entry["recipe"].get("name", "Unknown"),
                        "metric": key,
                        "value": float(m.group(1)),
                    }
                )

    if nutri_rows:
        df_nutri = pd.DataFrame(nutri_rows)
        st.subheader("🍽️ Nutrition Distribution")
        box = (
            alt.Chart(df_nutri)
            .mark_boxplot(extent="min-max")
            .encode(
                x=alt.X("metric:N", title="Nutrient"),
                y=alt.Y("value:Q", title="Amount per serving"),
                color=alt.Color("metric:N", legend=None),
            )
            .interactive()
        )
        st.altair_chart(box, use_container_width=True)
    else:
        st.info("No numeric nutrition data available.")

    # ─── Recipes Over Time ─────────────────────────────────────
    dates = []
    for entry in history:
        ts = entry.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", ""))
            dates.append(dt.date())
        except Exception:
            pass

    if dates:
        df_time = (
            pd.Series(dates)
            .value_counts()
            .rename_axis("date")
            .reset_index(name="count")
        )
        df_time["date"] = pd.to_datetime(df_time["date"])
        st.subheader("🕒 Recipes Generated Over Time")
        line = (
            alt.Chart(df_time)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("count:Q", title="Recipes"),
                tooltip=["date:T", "count:Q"],
            )
            .interactive()
        )
        st.altair_chart(line, use_container_width=True)
    else:
        st.info("No timestamp data available for trends.")

    # ─── Top Ingredients ───────────────────────────────────────
    all_ings = []
    for entry in history:
        for ing in entry.get("recipe", {}).get("ingredients", []):
            if isinstance(ing, dict):
                all_ings.append(ing.get("item", ing.get("name", str(ing))))
            else:
                all_ings.append(str(ing))
    if all_ings:
        freq = (
            pd.Series([i.strip().lower() for i in all_ings])
            .value_counts()
            .reset_index(name="frequency")
            .rename(columns={"index": "ingredient"})
            .head(10)
        )
        st.subheader("🌶️ Top 10 Ingredients Used")
        bar = (
            alt.Chart(freq)
            .mark_bar()
            .encode(
                y=alt.Y("ingredient:N", sort="-x", title=None),
                x=alt.X("frequency:Q", title="Usage Count"),
                tooltip=["ingredient:N", "frequency:Q"],
            )
            .interactive()
        )
        st.altair_chart(bar, use_container_width=True)
    else:
        st.info("No ingredients data available.")


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
    unsafe_allow_html=True,
)

# ─── Load env & init clients ─────────────────────
load_dotenv()
GOOGLE_KEY = st.secrets["GOOGLE_AI_API_KEY"]
UNSPLASH_KEY = st.secrets["UNSPLASH_ACCESS_KEY"]

if not GOOGLE_KEY:
    st.sidebar.error("🔑 Missing GOOGLE_AI_API_KEY — AI disabled.")
if not UNSPLASH_KEY:
    st.sidebar.error("🖼️ Missing UNSPLASH_ACCESS_KEY — Images disabled.")

ai_gen = GenAIRecipeGenerator(GOOGLE_KEY) if GOOGLE_KEY else None
img_fetch = UnsplashImageFetcher(UNSPLASH_KEY) if UNSPLASH_KEY else None
storage = Storage(Path("recipe_history.json"))

# ─── Sidebar inputs ──────────────────────────────
ingredients, restrictions, servings, do_generate, do_clear, do_random = get_user_input()
st.sidebar.markdown("### Analytics")
st.sidebar.markdown("Track your recipe generation history and view trends over time.")
view_stats = st.sidebar.button("📊 View Analytics")

# ─── Load history once ────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = storage.load_history()

try:
    # If analytics requested, render and halt
    if view_stats:
        render_analysis()
        st.stop()

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
                recipe = ai_gen.generate([], restrictions, servings)
                recipe_ings = normalize_ingredients(recipe["ingredients"])
                recipe["ingredients"] = recipe_ings
                images = (
                    img_fetch.fetch_images(recipe["name"], n=5) if img_fetch else []
                )
                st.session_state.temp = {
                    "recipe": recipe,
                    "recipe_ings": recipe_ings,
                    "image_options": images,
                    "user_ings": [],
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
                images = (
                    img_fetch.fetch_images(recipe["name"], n=5) if img_fetch else []
                )
                st.session_state.temp = {
                    "recipe": recipe,
                    "recipe_ings": recipe_ings,
                    "image_options": images,
                    "user_ings": ingredients,
                }
                st.session_state.pop("current", None)

    # ── Display current recipe ──────────────────────
    if "current" in st.session_state:
        cur = st.session_state.current
        st.title(f"🍲 {cur['recipe']['name']}")
        display_recipe(
            cur["recipe"],
            cur["recipe"]["ingredients"],
            cur["image_url"],
            cur["user_ings"],
            cur["substitutions"],
            key_prefix="current",
        )

    # ── Image picker for new recipes ───────────────
    elif "temp" in st.session_state:
        temp = st.session_state.temp
        st.header("🖼️ Pick a Hero Image")
        opts = temp["image_options"]

        if not opts:
            # finalize immediately if no images
            image_url = ""
            recipe = temp["recipe"]
            recipe_ings = temp["recipe_ings"]
            user_ings = temp["user_ings"]
            missing = [
                ing
                for ing in recipe_ings
                if ing.lower() not in {u.lower() for u in user_ings}
            ]
            subs = ai_gen.get_substitutions(missing) if (ai_gen and missing) else {}
            storage.save_recipe(recipe, image_url, user_ings, subs)
            st.session_state.history = storage.load_history()
            st.session_state.current = st.session_state.history[-1]
            st.session_state.pop("temp")
            st.stop()
        else:
            cols = st.columns(min(len(opts), 3))
            for idx, url in enumerate(opts):
                with cols[idx % len(cols)]:
                    st.image(url, use_container_width=True)
                    st.caption(f"Option {idx + 1}")

            choice = st.radio(
                "Select an image (and click Confirm Image twice to confirm):",
                options=list(range(len(opts))),
                format_func=lambda i: f"Option {i+1}",
            )

            if st.button("Confirm Image (click twice)"):
                image_url = opts[choice]
                recipe = temp["recipe"]
                recipe_ings = temp["recipe_ings"]
                user_ings = temp["user_ings"]
                missing = [
                    ing
                    for ing in recipe_ings
                    if ing.lower() not in {u.lower() for u in user_ings}
                ]
                subs = ai_gen.get_substitutions(missing) if (ai_gen and missing) else {}
                storage.save_recipe(recipe, image_url, user_ings, subs)
                st.session_state.history = storage.load_history()
                st.session_state.current = st.session_state.history[-1]
                st.session_state.pop("temp")
                st.stop()

    # ── History or welcome ──────────────────────────
    else:
        if not st.session_state.history:
            st.markdown(
                """
                <div style="text-align:center; margin-top:4rem; color:#2c3e50;">
                  <h1 style="font-size:2.5rem; margin-bottom:0.5rem;">👋 Welcome to PantryPal!</h1>
                  <p style="font-size:1.2rem; max-width:600px; margin:0 auto 1.5rem;">
                    Get started by adding ingredients in the sidebar<br/>
                    and clicking <strong>🍴 Generate Recipe</strong>.
                  </p>
                  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb2JzZ2RnZDFoM2dnYnJyNnRiaTJhY3lxZ3VhNzc4MWVqZGpsN215OCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/vdLUkluR3DYcsDcKP1/giphy.gif"
                       alt="Cooking GIF"
                       style="max-width:300px; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.1);" />
                </div>
                """,
                unsafe_allow_html=True,
            )
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
                        key_prefix=f"hist_{rid}",
                    )
                    if st.button("🗑️ Delete Recipe", key=f"del_{rid}"):
                        storage.delete_recipe(rid)
                        st.session_state.history = storage.load_history()
                        st.stop()

except Exception as e:
    st.error("🚨 Unexpected error:")
    st.text(str(e))
    st.text(traceback.format_exc())
