import json
from pathlib import Path

import pytest
from your_project import normalize_ingredients  # adjust import path

from components.display import _parse_numeric
from utils.storage import Storage


def test_normalize_ingredients_strings_and_dicts():
    raw = [
        "tomato",
        {"item": "onion", "amount": "1"},
        {"name": "garlic", "text": "2 cloves"},
        {"text": "pepper"},
        42,
    ]
    out = normalize_ingredients(raw)
    assert out == ["tomato", "onion", "garlic", "pepper", "42"]


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("12g", 12.0),
        ("Approximately 5.5 mg", 5.5),
        ("no number here", 0.0),
        ("100.01 units", 100.01),
    ],
)
def test_parse_numeric(input_str, expected):
    result = _parse_numeric(input_str)
    assert result == pytest.approx(expected)


def test_storage_save_load_clear(tmp_path):
    # Set up
    history_file = tmp_path / "history.json"
    storage = Storage(history_file)

    # Initially empty
    assert storage.load_history() == []

    # Save a dummy recipe
    recipe = {
        "name": "Test Dish",
        "ingredients": ["a", "b"],
        "nutrition": {},
        "instructions": [],
    }
    storage.save_recipe(recipe, "http://img", ["a"], {"b": ["c"]})

    # Load and verify
    hist = storage.load_history()
    assert len(hist) == 1
    entry = hist[0]
    assert entry["recipe"]["name"] == "Test Dish"
    assert entry["image_url"] == "http://img"
    assert entry["user_ings"] == ["a"]
    assert entry["substitutions"] == {"b": ["c"]}
    assert "timestamp" in entry

    # Clear and verify empty
    storage.clear_history()
    assert storage.load_history() == []


def test_storage_persists_file(tmp_path):
    history_file = tmp_path / "history2.json"
    storage = Storage(history_file)

    storage.save_recipe({"name": "X"}, "", [], {})
    # Direct file read
    raw = json.loads(history_file.read_text())
    assert isinstance(raw, list) and raw[0]["recipe"]["name"] == "X"
