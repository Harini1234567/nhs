# NHS data extraction charts

The `charts/` folder contains 16 chart folders. Each has exactly three files:

- A standalone, commented Python script.
- `counts.csv`: the counts for that chart.
- `chart.png`: the chart picture.

Each script reads only **Copy of Table cleaning** from your Excel workbook.
The source workbook is supplied separately.

Install the two packages once:

```sh
python -m pip install openpyxl "Pillow>=10.1"
```

Run whichever chart you need, passing your workbook path in quotes:

```sh
python charts/01_year_of_publication/year_of_publication.py "path/to/Data Extraction.xlsx"
```

The script updates `counts.csv` and `chart.png` in its own folder. All 16 scripts
work independently. Instructions and field-specific counting rules are at the
top of each script. After changing the workbook, save it and rerun the script.

Each nonempty titled row counts as one study. Multi-item fields count each item
once per study, so their percentages can sum above 100%. The supplied results
use 32 study rows; all scripts detect the number of rows automatically.
