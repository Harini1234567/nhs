"""
Breast review – bar chart for the column:
    Country (first author)

Reads the "Copy of Table cleaning" sheet of Data_Extraction.xlsx, counts the
number of studies in each category of this column and plots a bar chart.

One answer per study.

Usage:
    python plot_country_first_author.py Data_Extraction.xlsx
"""
import re
import sys

import matplotlib.pyplot as plt
import pandas as pd

# ---- Settings -------------------------------------------------------------
FILE = sys.argv[1] if len(sys.argv) > 1 else "Data_Extraction.xlsx"
SHEET = "Copy of Table cleaning"
COLUMN = 'Country (first author)'
CHART_TITLE = 'Country (first author)'
OUTPUT = 'country_first_author.png'

MULTI = False          # True = cell holds several values separated by ";"
# Labels recorded in slightly different ways that mean the same thing
RENAME = {}
# Free-text answers grouped into short categories (only used for free-text columns)
GROUPS = {}
# For numeric columns: (lower bound inclusive, upper bound exclusive, label)
BINS = None


def clean(label):
    label = re.sub(r"\s+", " ", str(label)).strip()
    label = RENAME.get(label, label)
    label = GROUPS.get(label, label)
    if label == "NR":
        label = "Not reported (NR)"
    return label


def categories_for_study(value):
    """Return the set of categories one study falls into."""
    if pd.isna(value) or str(value).strip() == "":
        return {"Blank"}
    if BINS:
        number = float(value)
        for low, high, label in BINS:
            if low <= number < high:
                return {label}
        raise ValueError(f"No bin for value {value}")
    if MULTI:
        parts = [p for p in str(value).split(";") if p.strip()]
        return {clean(p) for p in parts}
    return {clean(value)}


# ---- Load and count -------------------------------------------------------
df = pd.read_excel(FILE, sheet_name=SHEET)
df = df[df["Title"].notna()]                     # keep rows that are real studies
n_studies = len(df)

counts = {}
for value in df[COLUMN]:
    for cat in categories_for_study(value):
        counts[cat] = counts.get(cat, 0) + 1
counts = pd.Series(counts, dtype=int)

if BINS:                                         # keep size order for bins
    counts = counts.reindex([b[2] for b in BINS], fill_value=0)
else:                                            # most common first, NR / Blank last
    tail = [c for c in ("Not reported (NR)", "Blank") if c in counts.index]
    head = counts.drop(tail).sort_values(ascending=False, kind="stable")
    head = head.loc[sorted(head.index, key=lambda c: (-head[c], c))]
    counts = pd.concat([head, counts[tail]])

print(f"{COLUMN}  (n = {n_studies} studies)")
print(counts.to_string())
if MULTI:
    print("Note: a study can be counted in more than one category.")

# ---- Plot -----------------------------------------------------------------
BAR = "#2a78d6"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"


def wrap(text, width):
    words, lines, line = str(text).split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 > width and line:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    lines.append(line)
    return "\n".join(lines)


labels = list(counts.index)
values = counts.values
value_text = [f"{v} ({v / n_studies:.0%})" for v in values]
subtitle = f"n = {n_studies} studies"
if MULTI:
    subtitle += " · a study can appear in more than one bar"

vertical = len(labels) <= 6 and max(len(str(l)) for l in labels) <= 22

if vertical:
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150)
    bars = ax.bar([wrap(l, 16) for l in labels], values, color=BAR, width=0.6, zorder=3)
    for bar, txt in zip(bars, value_text):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.015,
                txt, ha="center", va="bottom", fontsize=10, color=INK)
    ax.set_ylabel("Number of studies", color=INK_2)
    ax.set_ylim(0, max(values) * 1.15)
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK_2)
else:
    wrapped = [wrap(l, 45) for l in labels]
    lines = sum(w.count("\n") + 1 for w in wrapped)
    height = max(3.5, 0.32 * lines + 0.18 * len(labels) + 1.6)
    fig, ax = plt.subplots(figsize=(10, height), dpi=150)
    y = range(len(labels))
    bars = ax.barh(list(y), values, color=BAR, height=0.65, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels(wrapped, fontsize=9.5)
    ax.invert_yaxis()
    for bar, txt in zip(bars, value_text):
        ax.text(bar.get_width() + max(values) * 0.01, bar.get_y() + bar.get_height() / 2,
                txt, ha="left", va="center", fontsize=9.5, color=INK)
    ax.set_xlabel("Number of studies", color=INK_2)
    ax.set_xlim(0, max(values) * 1.18)
    ax.xaxis.get_major_locator().set_params(integer=True)
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(INK_2)

ax.set_title(wrap(CHART_TITLE, 70), fontsize=13, color=INK, loc="left", pad=22)
ax.annotate(subtitle, xy=(0, 1), xycoords="axes fraction", xytext=(0, 6),
            textcoords="offset points", fontsize=9.5, color=INK_2, ha="left", va="bottom")
ax.tick_params(colors=INK_2, length=0)

plt.tight_layout()
plt.savefig(OUTPUT, bbox_inches="tight")
print(f"Saved chart to {OUTPUT}")
plt.show()
