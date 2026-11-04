"""Validation Method: create counts.csv and chart.png.

ONE-TIME SETUP: python -m pip install openpyxl "Pillow>=10.1"
RUN: python validation_method.py "path/to/Data Extraction.xlsx"

This file works on its own; no other project scripts are needed.
Only the worksheet 'Copy of Table cleaning' is read. Source data is not changed.
Save your workbook changes and rerun this file to update its counts and picture.
Each nonempty titled row is treated as one study; no automatic deduplication.
Percentages use all study rows. Multiple-item totals may exceed the study count.
Blank values, Not reported and No remain distinct.

COUNTING RULE: Group by method using the rules in the script. Bootstrap confidence intervals are shown separately from bootstrap validation. Same-institution temporal validation is separate from validation explicitly labelled external.
"""
import csv
import re
import sys
import textwrap
from collections import Counter
from pathlib import Path
from openpyxl import load_workbook

# These settings belong to this chart only.
SHEET = "Copy of Table cleaning"
FIELD = 'Validation Method'
NUMBER = 12
MULTIPLE = True
MISSING = "Missing / blank"

def clean(value):
    """Remove extra whitespace; display whole numbers without an unnecessary .0."""
    if value is None or str(value).strip() == "":
        return MISSING
    if isinstance(value, (int, float)) and float(value).is_integer():
        return str(int(value))
    return re.sub(r"\s+", " ", str(value)).strip()


# Edit the labels/rules below if your coding changes.
def code_items(value):
    # A study may use several methods. Each matched method is counted once.
    text = value.casefold()
    rules = [
        ("Hold-out / train-test-validation split", "hold-out" in text or "split" in text),
        ("Cross-validation", bool(re.search(r"\bcv\b|cross.validation", text))),
        ("Bootstrap validation / optimism correction", "bootstrap" in text and "confidence intervals" not in text),
        ("Bootstrap confidence intervals", "bootstrap confidence intervals" in text),
        ("Out-of-bag validation", "out-of-bag" in text),
        ("External validation (as labelled)", "external:" in text),
        ("Temporal validation (same institution)", "temporal" in text and "external:" not in text),
        ("Not clearly reported", "not clearly reported" in text),
    ]
    return [label for label, matches in rules if matches] or [value]


def make_picture(rows, total, path):
    """Draw a PNG picture. Change the blue colour or text sizes here if needed."""
    from PIL import Image, ImageDraw, ImageFont

    # Use a familiar font where available; Pillow's built-in font is the fallback.
    def font(size):
        for name in ["arial.ttf", "DejaVuSans.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"]:
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                pass
        return ImageFont.load_default(size=size)

    scale = 2  # A larger picture stays sharp when placed in a document.
    regular, title_font = font(14 * scale), font(20 * scale)
    labels = [textwrap.wrap(row["Item"], 49) for row in rows]
    heights = [max(40, 19 * len(lines) + 14) for lines in labels]
    title_lines = textwrap.wrap(FIELD, 75)
    top = 60 + 25 * len(title_lines)
    height = top + sum(heights) + 55
    image = Image.new("RGB", (1000 * scale, height * scale), "white")
    draw = ImageDraw.Draw(image)
    for i, line in enumerate(title_lines):
        draw.text((20 * scale, (16 + i * 25) * scale), line, font=title_font, fill="#182b40")
    draw.text((20 * scale, (top - 28) * scale),
              f"Study rows (N={total}); each item counted once per study", font=regular, fill="#182b40")
    maximum = max(row["Count"] for row in rows)
    y = top
    for row, lines, row_height in zip(rows, labels, heights):
        middle = y + row_height / 2
        for j, line in enumerate(lines):
            draw.text((395 * scale, (middle - (len(lines) - 1) * 9.5 + j * 19) * scale),
                      line, anchor="rm", font=regular, fill="#182b40")
        width = 480 * row["Count"] / maximum
        draw.rectangle((410 * scale, (middle - 10) * scale,
                        (410 + width) * scale, (middle + 10) * scale), fill="#32689a")
        draw.text(((420 + width) * scale, middle * scale), str(row["Count"]),
                  anchor="lm", font=regular, fill="#182b40")
        y += row_height
    draw.line((410 * scale, top * scale, 410 * scale, y * scale), fill="#aebbc9", width=2)
    draw.text((410 * scale, (y + 16) * scale), "0", font=regular, fill="#182b40")
    draw.text((890 * scale, (y + 16) * scale), f"{maximum} study rows",
              anchor="rt", font=regular, fill="#182b40")
    image.save(path, dpi=(200, 200))


def main():
    # Pass a workbook path, or put Data Extraction.xlsx in your current folder.
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Data Extraction.xlsx")
    if not path.is_file():
        raise SystemExit('Workbook not found. Run this script followed by the workbook path in quotes.')
    book = load_workbook(path, read_only=True, data_only=True)
    try:
        if SHEET not in book.sheetnames:
            raise ValueError(f"Required worksheet missing: {SHEET}")
        source_rows = list(book[SHEET].values)
    finally:
        book.close()
    if not source_rows:
        raise ValueError("The worksheet is empty.")
    headers = [clean(value) for value in source_rows[0]]
    matching = [i for i, name in enumerate(headers) if name == FIELD or
                (FIELD == "Dataset Available" and name.startswith("Dataset Available ("))]
    if len(matching) != 1 or headers.count("Title") != 1:
        raise ValueError(f"Expected one {FIELD!r} column and one Title column.")
    column, title_column = matching[0], headers.index("Title")
    counter = Counter()
    total = 0
    for excel_row, row in enumerate(source_rows[1:], 2):
        # Ignore formatting-only rows, but flag incomplete study records.
        if not any(clean(value) != MISSING for value in row):
            continue
        if clean(row[title_column]) == MISSING:
            raise ValueError(f"Row {excel_row} contains data but has no study Title.")
        items = set(code_items(clean(row[column])))
        if not items:
            raise ValueError(f"No category assigned for row {excel_row}.")
        counter.update(items)  # A repeated item within one study counts once.
        total += 1
    if not total:
        raise ValueError("No study rows found.")
    if FIELD in ["Year of Publication", "Sample Size"]:
        order = sorted(counter, key=lambda item: (0, float(item)) if item.isdigit() else (1, item))
    else:
        order = sorted(counter, key=lambda item: (-counter[item], item.casefold()))
    rows = []
    for item in order:
        code = f"F{NUMBER:02d}_" + re.sub(r"[^a-z0-9]+", "_", item.casefold()).strip("_")
        rows.append({"Field": FIELD, "Code": code, "Item": item, "Count": counter[item],
                     "Total studies": total, "% of studies": round(100 * counter[item] / total, 2)})
    assert all(0 < row["Count"] <= total for row in rows)
    assert len({row["Code"] for row in rows}) == len(rows), "Category-code collision."
    if not MULTIPLE:
        assert sum(counter.values()) == total
    # Save beside this script. Running it again replaces these two output files.
    output = Path(__file__).resolve().parent
    with (output / "counts.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    make_picture(rows, total, output / "chart.png")
    print(f"Done: {FIELD}; {total} study rows. Saved counts.csv and chart.png beside this script.")


if __name__ == "__main__":
    main()
