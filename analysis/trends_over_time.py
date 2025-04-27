#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# ─── Load history ────────────────────────────────
history_path = Path(__file__).parent.parent / "recipe_history.json"
with open(history_path) as f:
    history = json.load(f)

# ─── Parse dates ─────────────────────────────────
dates = [
    datetime.fromisoformat(entry["timestamp"].split("Z")[0]).date() for entry in history
]
df = pd.Series(dates).value_counts().sort_index()
df.index = pd.to_datetime(df.index)

print("Recipes generated per day:")
print(df)

# ─── Plot time series ────────────────────────────
plt.figure(figsize=(10, 4))
plt.plot(df.index, df.values, marker="o")
plt.title("Recipes Generated Over Time")
plt.xlabel("Date")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("analysis/trends_over_time.png")
print("\n▶️ Plot saved to analysis/trends_over_time.png")
