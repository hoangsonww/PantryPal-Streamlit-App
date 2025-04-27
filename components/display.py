import json
import re

import altair as alt
import pandas as pd
import streamlit as st


def _parse_numeric(v: str) -> float:
    """
    Extracts the first numeric value from a string and converts it to a float.

    :param v: The input string to parse.
    :return: The first numeric value as a float, or 0.0 if no numeric value is found.
    """
    m = re.search(r"[\d]+(?:\.\d+)?", v)
    return float(m.group()) if m else 0.0


def display_recipe(
    recipe: dict,
    recipe_ings: list,
    image_url: str,
    user_ings: list,
    substitutions,
    key_prefix: str = "default",
):
    """
    Displays a recipe with its ingredients, instructions, nutrition information, and download options.

    :param recipe: The recipe dictionary containing details like name, ingredients, instructions, and nutrition.
    :param recipe_ings: The list of ingredients in the recipe.
    :param image_url: The URL of the hero image for the recipe.
    :param user_ings: The list of ingredients provided by the user.
    :param substitutions: The substitutions for ingredients, either as a list of dicts or a dict mapping.
    :param key_prefix: A prefix for the keys used in Streamlit components to avoid conflicts.
    :return: None
    """
    # — Hero Image
    if image_url:
        st.image(image_url, use_container_width=True)

    # — Ingredients
    st.subheader("📝 Ingredients")
    missing = []
    for idx, ing in enumerate(recipe_ings):
        label = (
            f"{ing['item']} — {ing['amount']}" if isinstance(ing, dict) else str(ing)
        )
        checked = st.checkbox(
            label,
            value=label.lower() in (u.lower() for u in user_ings),
            key=f"{key_prefix}_ing_{idx}",
        )
        if not checked:
            missing.append(label)

    # — Shopping List (below ingredients)
    if missing:
        st.subheader("🛒 Shopping List")
        for line in missing:
            st.write(f"• {line}")
        st.download_button(
            "📋 Download shopping list (TXT)",
            data="\n".join(missing),
            file_name="shopping_list.txt",
            mime="text/plain",
            key=f"{key_prefix}_dl_shop",
        )

    # — Nutrition Charts
    st.subheader("🔢 Nutrition per Serving")
    nutri = recipe.get("nutrition", {})
    names = list(nutri.keys())
    vals = [_parse_numeric(v) for v in nutri.values()]
    if names:
        df = pd.DataFrame({"Nutrient": names, "Amount": vals})
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Nutrient Amounts")
            st.altair_chart(
                alt.Chart(df)
                .mark_bar()
                .encode(x="Nutrient", y="Amount", tooltip=["Nutrient", "Amount"])
                .properties(height=200),
                use_container_width=True,
            )
        with c2:
            st.subheader("🍩 Nutrient Proportions")
            st.altair_chart(
                alt.Chart(df)
                .mark_arc(innerRadius=50)
                .encode(
                    theta="Amount", color="Nutrient", tooltip=["Nutrient", "Amount"]
                )
                .properties(height=200),
                use_container_width=True,
            )

    # — Difficulty
    steps = recipe.get("instructions", [])
    diff = "Easy" if len(steps) <= 5 else "Medium" if len(steps) <= 10 else "Hard"
    st.markdown(f"### 🎯 Estimated Difficulty: **{diff}**")

    # — Instructions
    st.subheader("👩‍🍳 Instructions")
    for i, step in enumerate(steps, 1):
        st.write(f"**{i}.** {step}")

    # — Substitutions
    if substitutions:
        st.subheader("🔄 Substitutions")
        if isinstance(substitutions, list):
            for entry in substitutions:
                ing_name = entry.get("ingredient") or entry.get("item") or "Unknown"
                subs_list = entry.get("substitutes") or entry.get("subs") or []
                subs_str = [s if isinstance(s, str) else str(s) for s in subs_list]
                st.write(f"• **{ing_name}**: {', '.join(subs_str)}")
        elif isinstance(substitutions, dict):
            for orig, subs_list in substitutions.items():
                subs_str = [s if isinstance(s, str) else str(s) for s in subs_list]
                st.write(f"• **{orig}**: {', '.join(subs_str)}")
        else:
            st.write(str(substitutions))

    # — Downloads (JSON, Markdown, TXT)
    json_str = json.dumps(recipe, indent=2)
    st.download_button(
        "📄Download JSON",
        data=json_str,
        file_name=f"{recipe['name'].replace(' ', '_')}.json",
        mime="application/json",
        key=f"{key_prefix}_dl_json",
    )

    # — Download Markdown
    md = [f"# {recipe['name']}", "", "## Ingredients"]
    for ing in recipe_ings:
        md.append(f"- {ing}")
    md += ["", "## Instructions"]
    for i, s in enumerate(steps, 1):
        md.append(f"{i}. {s}")
    md += ["", "## Nutrition"]
    for n, v in recipe.get("nutrition", {}).items():
        md.append(f"- **{n}**: {v}")
    if missing:
        md += ["", "## Shopping List"] + [f"- {l}" for l in missing]
    st.download_button(
        "🔖 Download Markdown",
        data="\n".join(md),
        file_name=f"{recipe['name'].replace(' ', '_')}.md",
        mime="text/markdown",
        key=f"{key_prefix}_dl_md",
    )

    # — Download Plain TXT
    txt = [recipe["name"], "", "Ingredients:"] + [f"- {l}" for l in recipe_ings]
    txt += ["", "Instructions:"] + [f"{i}. {s}" for i, s in enumerate(steps, 1)]
    txt += ["", "Nutrition:"] + [
        f"- {n}: {v}" for n, v in recipe.get("nutrition", {}).items()
    ]
    if missing:
        txt += ["", "## Shopping List"] + [f"- {l}" for l in missing]
    st.download_button(
        "🧾 Download Plain TXT",
        data="\n".join(txt),
        file_name=f"{recipe['name'].replace(' ', '_')}.txt",
        mime="text/plain",
        key=f"{key_prefix}_dl_txt",
    )

    # — Return Home button (only when viewing current recipe)
    if key_prefix == "current":
        st.markdown("---")

        def _return_home():
            st.session_state.pop("current", None)
            st.session_state.pop("temp", None)

        st.button(
            "🏠 Return Home",
            key=f"{key_prefix}_return_home",
            on_click=_return_home,
        )
