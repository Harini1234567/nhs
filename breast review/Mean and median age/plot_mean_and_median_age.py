"""
Breast review – mean age and median age of study participants.

Reads the "Copy of Table cleaning" sheet of Data_Extraction.xlsx and draws two
box plots on one chart: one for the studies that reported a mean age
(column "Mean age 2") and one for the studies that reported a median age
(column "Median age"). Each dot is one study.

Studies that reported no overall age (NR, or only subgroup ages) are blank in
both columns and so are left out.

Usage:
    python plot_mean_and_median_age.py Data_Extraction.xlsx
"""
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---- Settings -------------------------------------------------------------
FILE = sys.argv[1] if len(sys.argv) > 1 else "Data_Extraction.xlsx"
SHEET = "Copy of Table cleaning"
MEAN_COL = "Mean age 2"
MEDIAN_COL = "Median age"
OUTPUT = "mean_and_median_age.png"

# ---- Load -----------------------------------------------------------------
df = pd.read_excel(FILE, sheet_name=SHEET)
df = df[df["Title"].notna()]                     # keep rows that are real studies
n_studies = len(df)

mean_ages = pd.to_numeric(df[MEAN_COL], errors="coerce").dropna()
median_ages = pd.to_numeric(df[MEDIAN_COL], errors="coerce").dropna()


def summary(s):
    q1, med, q3 = np.percentile(s, [25, 50, 75])
    return (f"n = {len(s)}, median {med:.1f}, IQR {q1:.1f}–{q3:.1f}, "
            f"range {s.min():.1f}–{s.max():.1f}")


print(f"Studies in sheet: {n_studies}")
print(f"Mean age reported:   {summary(mean_ages)}")
print(f"Median age reported: {summary(median_ages)}")
print(f"No overall age reported: {n_studies - len(mean_ages) - len(median_ages)}")

# ---- Plot -----------------------------------------------------------------
COLOURS = ["#2a78d6", "#eb6834"]                 # blue = mean, orange = median
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"

data = [mean_ages.values, median_ages.values]
labels = [f"Mean age\n(n = {len(mean_ages)} studies)",
          f"Median age\n(n = {len(median_ages)} studies)"]

fig, ax = plt.subplots(figsize=(7.5, 6), dpi=150)
box = ax.boxplot(data, widths=0.5, patch_artist=True, showfliers=False, zorder=2,
                 medianprops=dict(color=INK, linewidth=2),
                 whiskerprops=dict(color=INK_2, linewidth=1.2),
                 capprops=dict(color=INK_2, linewidth=1.2),
                 boxprops=dict(linewidth=1.2))
for patch, colour in zip(box["boxes"], COLOURS):
    patch.set_facecolor(colour)
    patch.set_alpha(0.35)
    patch.set_edgecolor(colour)

# every study as a dot (fixed seed so the chart is the same each run)
rng = np.random.default_rng(1)
for i, (values, colour) in enumerate(zip(data, COLOURS), start=1):
    x = i + rng.uniform(-0.12, 0.12, size=len(values))
    ax.scatter(x, values, s=42, color=colour, edgecolor="white", linewidth=1.2, zorder=3)

ax.set_xticks([1, 2])
ax.set_xticklabels(labels, color=INK, fontsize=10.5)
ax.set_ylabel("Age (years)", color=INK_2)
low = min(v.min() for v in data)
high = max(v.max() for v in data)
ax.set_ylim(np.floor(low / 5) * 5 - 2, np.ceil(high / 5) * 5 + 2)

ax.set_title("Mean and median age of participants", fontsize=13, color=INK, loc="left", pad=22)
ax.annotate(f"Each dot is one study · {n_studies - len(mean_ages) - len(median_ages)} of "
            f"{n_studies} studies reported no overall age",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 6), textcoords="offset points",
            fontsize=9.5, color=INK_2, ha="left", va="bottom")

ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(INK_2)
ax.tick_params(colors=INK_2, length=0)

plt.tight_layout()
plt.savefig(OUTPUT, bbox_inches="tight")
print(f"Saved chart to {OUTPUT}")
plt.show()
