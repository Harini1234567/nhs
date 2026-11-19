"""
Count how many studies were published in each year and plot a bar chart.

Usage:
    python plot_publication_years.py Data_Extraction.xlsx
"""
import re
import sys

import matplotlib.pyplot as plt
import pandas as pd

# ---- Settings -------------------------------------------------------------
FILE = sys.argv[1] if len(sys.argv) > 1 else "Data_Extraction.xlsx"
SHEET = "Copy of Table cleaning"
YEAR_COL = "Year of Publication"
OUTPUT = "publications_per_year.png"


def extract_year(value):
    """Pull the first 4-digit year out of a cell, e.g.
    '2022 (online acceptance in 2021)' -> 2022."""
    match = re.search(r"(19|20)\d{2}", str(value))
    return int(match.group()) if match else None


# ---- Load and count -------------------------------------------------------
df = pd.read_excel(FILE, sheet_name=SHEET)
df = df[df["Title"].notna()]                     # keep rows that are real studies
years = df[YEAR_COL].apply(extract_year).dropna().astype(int)

counts = years.value_counts().sort_index()
# include any missing years in the range so gaps show as 0
counts = counts.reindex(range(counts.index.min(), counts.index.max() + 1), fill_value=0)

print("Number of studies per year of publication:")
print(counts.to_string())
print(f"Total: {counts.sum()}")

# ---- Plot -----------------------------------------------------------------
BAR = "#2a78d6"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"

fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
bars = ax.bar(counts.index.astype(str), counts.values, color=BAR, width=0.7, zorder=3)

# value label above each bar
for bar, n in zip(bars, counts.values):
    if n > 0:
        ax.text(bar.get_x() + bar.get_width() / 2, n + 0.2, str(n),
                ha="center", va="bottom", fontsize=10, color=INK)

ax.set_title(f"Number of studies by year of publication (n = {counts.sum()})",
             fontsize=13, color=INK, loc="left", pad=12)
ax.set_xlabel("Year of publication", color=INK_2)
ax.set_ylabel("Number of studies", color=INK_2)
ax.set_ylim(0, counts.max() + 2)
ax.yaxis.get_major_locator().set_params(integer=True)

ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(INK_2)
ax.tick_params(colors=INK_2, length=0)

plt.tight_layout()
plt.savefig(OUTPUT, bbox_inches="tight")
print(f"Saved chart to {OUTPUT}")
plt.show()
