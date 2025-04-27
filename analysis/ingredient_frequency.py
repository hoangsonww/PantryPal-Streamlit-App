#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# ─── Figure out where this script lives ─────────────────────
script_path = Path(__file__).resolve()
script_dir = script_path.parent  # e.g. …/PantryPal/analysis

# ─── Load recipe_history.json, which is one level up ────────
history_path = script_dir.parent / "recipe_history.json"
if not history_path.exists():
    print(f"Error: {history_path} not found.", file=sys.stderr)
    sys.exit(1)

with open(history_path) as f:
    history = json.load(f)

# ─── Build DataFrame ───────────────────────────────────────
rows = []
for entry in history:
    nutri = entry.get("recipe", {}).get("nutrition", {}) or {}
    parsed = {}
    for key, val in nutri.items():
        m = re.match(r"^\s*([\d\.]+)", val or "")
        if m:
            parsed[key] = float(m.group(1))
    if parsed:
        parsed["name"] = entry["recipe"].get("name", "Unknown")
        rows.append(parsed)

df = pd.DataFrame(rows).set_index("name")

# ─── Bail if there’s no data ───────────────────────────────
if df.empty or df.shape[1] == 0:
    print("No numeric nutrition data found — check your parsing!", file=sys.stderr)
    sys.exit(1)

# ─── Print summary ──────────────────────────────────────────
print("Nutrition summary (per recipe):")
print(df.describe())

# ─── Pick columns to plot ───────────────────────────────────
metrics = [
    c
    for c in df.columns
    if c.lower() in ("calories", "protein", "fat", "carbs", "fiber")
]
if not metrics:
    print("No matching metrics found for plotting.", file=sys.stderr)
    sys.exit(1)

# ─── Save the figure right next to this script ─────────────
output_path = script_dir / "nutrition_summary.png"

plt.figure(figsize=(8, 5))
df[metrics].boxplot()
plt.title("Nutrition Distribution Across Recipes")
plt.ylabel("Amount per serving")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(output_path)

print(f"\n▶️ Plot saved to {output_path}")
