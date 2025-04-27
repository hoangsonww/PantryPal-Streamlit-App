import streamlit as st


def get_user_input():
    """
    Get user input from the sidebar for ingredients, dietary restrictions, servings, and actions.
    Returns:
      - ingredients: list[str]
      - restrictions: list[str]
      - servings: int
      - do_generate: bool
      - do_clear: bool
      - do_random: bool
    """

    # ── Sidebar CSS for accent borders & spacing ──
    st.sidebar.markdown(
        """
        <style>
          .sidebar-section {
            border-left: 4px solid #2c3e50;
            padding-left: 0.75rem;
            margin-bottom: 1rem;
          }
          .sidebar-section .section-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
          }
          .sidebar-section .helper-text {
            font-size: 0.9rem;
            color: #555555;
            margin-top: 0;
            margin-bottom: 0.75rem;
          }
          /* tighten up margins between controls */
          .stTextInput, .stMultiselect, .stSlider, .stButton > button {
            margin-bottom: 0.75rem !important;
          }
          .stSidebar caption {
            color: #AA0000 !important;
            font-size: 0.85rem;
          }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # ── Top-level instructions ─────────────────────
    st.sidebar.markdown("## 🍲 PantryPal Settings")
    st.sidebar.markdown(
        "> Enter what’s in your pantry, any preferences, then hit **Generate**."
    )

    # ── Ingredients ────────────────────────────────
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="section-title">🥕 Ingredients</div>', unsafe_allow_html=True
    )
    st.sidebar.markdown(
        '<p class="helper-text">List your ingredients as a comma-separated list.</p>',
        unsafe_allow_html=True,
    )
    ingredients_text = st.sidebar.text_input(
        label="Ingredients",
        placeholder="e.g. chicken, rice, tomato, garlic",
        label_visibility="visible",
        key="ingredients_text",
    )
    ingredients = [item.strip() for item in ingredients_text.split(",") if item.strip()]
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # ── Dietary Restrictions ───────────────────────
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="section-title">⚠️ Dietary Restrictions</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<p class="helper-text">Select any allergies or dietary preferences.</p>',
        unsafe_allow_html=True,
    )
    restrictions = st.sidebar.multiselect(
        label="Restrictions",
        options=[
            "Vegetarian",
            "Vegan",
            "Gluten-Free",
            "Dairy-Free",
            "Nut-Free",
            "Halal",
            "Kosher",
        ],
        default=[],
        label_visibility="visible",
        key="restrictions",
    )
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # ── Servings ───────────────────────────────────
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="section-title">🍽️ Servings</div>', unsafe_allow_html=True
    )
    st.sidebar.markdown(
        '<p class="helper-text">How many portions do you need?</p>',
        unsafe_allow_html=True,
    )
    servings = st.sidebar.slider(
        label="Servings",
        min_value=1,
        max_value=12,
        value=2,
        format="%d servings",
        key="servings",
    )
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # ── Actions ────────────────────────────────────
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="section-title">▶️ Actions</div>', unsafe_allow_html=True
    )
    st.sidebar.markdown(
        '<p class="helper-text">Generate a recipe, surprise yourself, or clear history.</p>',
        unsafe_allow_html=True,
    )
    # disable Generate if no ingredients
    generate_disabled = len(ingredients) == 0
    do_generate = st.sidebar.button(
        "🍴 Generate Recipe",
        use_container_width=True,
        key="do_generate",
        disabled=generate_disabled,
    )
    if generate_disabled:
        st.sidebar.caption("Add at least one ingredient to enable this button.")
    do_random = st.sidebar.button(
        "🎲 Surprise Me!", use_container_width=True, key="do_random"
    )
    do_clear = st.sidebar.button(
        "🗑️ Clear All History", use_container_width=True, key="do_clear"
    )
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    return ingredients, restrictions, servings, do_generate, do_clear, do_random
