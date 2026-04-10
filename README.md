[Versión en español](README.es.md)

# expense-tracker

I originally built this because I kept exporting my bank transactions to CSV and then doing nothing with them. Opening them in Excel, scrolling around, closing the file. So at some point I just decided to write something that actually processes the data — categories, trends, anything that looks weird — and outputs something readable.

It's a CLI tool. Point it at a CSV or Excel file and it runs the full pipeline: reads and cleans the data, computes stats by category and month, flags transactions that look off, generates three charts, and writes a self-contained HTML report you can open without internet.

```
$ expense-tracker -i data/expenses.csv

  STEP 1 / 3  —  Data Ingestion
  Records: 21  |  Period: 01/05/2024 — 03/28/2024  |  Total: $7,679.00

  STEP 2 / 3  —  Analysis & Anomaly Detection
  [+] $2,400.00 is 2.2x above the Food mean of $579.83  (Catering event)

  STEP 3 / 3  —  Visualizations
  [bar]  bar_category_20240408.png
  [pie]  pie_category_20240408.png
  [line] line_monthly_20240408.png
  [html] expense_report_20240408.html
```

---

## Getting started

```bash
git clone https://github.com/Zraght/expense-tracker
cd expense-tracker
pip install -e .

# there's a sample file in data/ if you want to try it immediately
expense-tracker

# or point it at your own file
expense-tracker -i path/to/expenses.csv -o results/

# skip the HTML report if you just want the terminal output + charts
expense-tracker --no-report --log-level DEBUG
```

Requires Python 3.10+.

```bash
# dev dependencies (pytest, black, ruff, mypy) — optional
pip install -e ".[dev]"

python -m pytest tests/
# 73 passed
```

---

## How to use it

```
expense-tracker [-h] [-i INPUT] [-o OUTPUT] [-c CONFIG]
                [--log-level {DEBUG,INFO,WARNING,ERROR}]
                [--show-plots] [--no-report] [--version]
```

| Flag | What it does |
|---|---|
| `-i`, `--input` | path to your CSV or Excel file |
| `-o`, `--output` | output folder, defaults to `output/` |
| `-c`, `--config` | custom config file path |
| `--log-level` | set to `DEBUG` if something isn't parsing correctly |
| `--show-plots` | display charts in a window (needs a display, obviously) |
| `--no-report` | skip the HTML report, just save the charts |

---

## What your file needs to look like

Four columns, nothing more:

| Column | Type | Example |
|---|---|---|
| `Date` | string | `2024-03-15` |
| `Category` | string | `Food` |
| `Amount` | float | `85.50` |
| `Description` | string | `Weekly groceries` |

Default date format is `%Y-%m-%d`. If your dates are in a different format, that's configurable. The sample file at `data/expenses_example.csv` is probably the fastest way to understand what it expects.

---

## What it actually does

Reads `.csv`, `.xlsx`, or `.xls`. On load it coerces types, drops full duplicates, and warns about anything it had to skip (bad dates, non-numeric amounts, that kind of thing).

From there it computes:
- total and average spend per month
- totals, percentages, and transaction counts per category
- highest and lowest single transactions

Then it checks for anomalies — more on that below.

Finally: three charts (bar, pie, line), saved as 300 DPI PNGs. And if you haven't passed `--no-report`, it writes a self-contained HTML file with the charts embedded as base64. The reason I did it that way is so the file actually stays intact if you move it around or send it to someone — no broken image links.

Logs go to `logs/expense_tracker.log` with rotation so they don't pile up.

---

## The anomaly detection part

This turned out to be more useful than I expected when I first added it. Basically, for each category, it looks at all your transactions and flags the ones that are way outside the normal range for that category specifically — not overall, per category. So a $400 charge in a category where you normally spend $40 will get flagged, even if $400 is totally normal in another category.

The output is intentionally plain:

```
[+] $2,400.00 is 2.2x above the Food mean of $579.83
    Date: 03/28/2024  |  Catering event
```

In practice this catches three things: data entry mistakes (wrong amount), actual duplicate charges, and legitimate one-offs that you might want to review anyway. Categories with fewer than 3 transactions get skipped — not enough history to say what's "normal."

The threshold is configurable if the default flags too much or too little.

---

## Config

You don't need a config file to run it — there are defaults for everything. But if you want to tweak things, edit `config/config.json`:

```json
{
  "analysis": {
    "anomaly_z_threshold": 2.0
  },
  "visualization": {
    "dpi": 300,
    "show_plots": false
  },
  "output": {
    "export_html": true
  }
}
```

Any key you leave out just falls back to the default. The full set of defaults is in `utils/config_loader.py` if you want to see everything that's tunable. You can also override most things from the CLI directly without touching the file.

---

## Project structure

```
expense-tracker/
├── main.py                   # CLI entry point and pipeline orchestrator
├── pyproject.toml            # build config, dependencies, tool settings
├── config/
│   └── config.json           # user-editable config
├── data/
│   └── expenses_example.csv  # sample data
├── modules/
│   ├── reading.py            # CSV/Excel ingestion and cleaning
│   ├── analysis.py           # stats and anomaly detection
│   ├── visualization.py      # chart generation (matplotlib/seaborn)
│   └── reporter.py           # HTML report builder
├── utils/
│   ├── config_loader.py      # config loading with deep-merge defaults
│   ├── logger.py             # rotating file + console logging
│   └── validators.py         # DataFrame and path validation
├── tests/
│   ├── conftest.py           # shared fixtures
│   ├── test_analysis.py
│   ├── test_reading.py
│   ├── test_validators.py
│   └── test_config.py
├── logs/
└── output/
```

---

## Why I built this as a "real" project

Honestly, part of it was to have something to show. I wanted to build something end-to-end — not a notebook, not a script, but an actual installable CLI with tests, logging, config management, proper error handling. The kind of thing you'd hand off to someone else and they could run it.

The patterns in here are ones I'd use in a real data pipeline job:

| Pattern | Where |
|---|---|
| ETL pipeline | `reading.py` → `analysis.py` → `reporter.py` |
| Schema validation + data contracts | `utils/validators.py`, column checks before any processing |
| Statistical anomaly detection | `detect_anomalies()` — same approach used in fraud detection and log monitoring |
| Structured logging | rotating handler, consistent levels across all modules |
| Config-driven behavior | deep-merge JSON, no hardcoded values, overridable per environment |
| CLI with exit codes | argparse, non-zero on failure, works in scripts and CI |
| Proper packaging | `pyproject.toml`, installable with `pip install -e .` |
| Test coverage | 73 unit tests, shared fixtures, edge cases, validation paths |

---

## License

MIT — see [LICENSE](LICENSE).