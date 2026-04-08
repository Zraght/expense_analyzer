"""
Data ingestion module — reads expense files (CSV and Excel) into a clean DataFrame.
"""

import logging
from pathlib import Path

import pandas as pd

from utils.validators import (
    DataValidationError,
    check_data_quality,
    validate_dataframe_not_empty,
    validate_required_columns,
)

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["Date", "Category", "Amount", "Description"]


def read_expenses(
    file_path: str | Path,
    required_columns: list[str] | None = None,
    date_format: str = "%Y-%m-%d",
) -> pd.DataFrame:
    """
    Load expense data from a CSV or Excel file.

    Handles type coercion, date parsing, and basic quality cleanup.
    Supports .csv, .xlsx, and .xls.

    Args:
        file_path: Path to the input file.
        required_columns: Columns that must be present. Defaults to the standard four.
        date_format: strftime format used to parse the Date column.

    Returns:
        Cleaned, date-sorted DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        DataValidationError: If required columns are missing or the file is empty.
        ValueError: If the file format is unsupported.
    """
    if required_columns is None:
        required_columns = REQUIRED_COLUMNS

    path = Path(file_path)
    logger.info("Reading expense file: %s", path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            df = pd.read_csv(path)
        elif suffix in {".xlsx", ".xlsm"}:
            df = pd.read_excel(path, engine="openpyxl")
        elif suffix == ".xls":
            df = pd.read_excel(path, engine="xlrd")
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    except Exception as exc:
        logger.error("Failed to read %s: %s", path, exc, exc_info=True)
        raise

    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, required_columns, "Expense data")

    df, quality_report = check_data_quality(df)
    if quality_report.get("null_counts"):
        logger.warning("Null values found: %s", quality_report["null_counts"])

    df["Date"] = pd.to_datetime(df["Date"], format=date_format, errors="coerce")
    invalid_dates = df["Date"].isna().sum()
    if invalid_dates:
        logger.warning("Dropping %d rows with unparseable dates", invalid_dates)
        df = df.dropna(subset=["Date"])

    if not pd.api.types.is_numeric_dtype(df["Amount"]):
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        invalid_amounts = df["Amount"].isna().sum()
        if invalid_amounts:
            logger.warning("Dropping %d rows with non-numeric amounts", invalid_amounts)
            df = df.dropna(subset=["Amount"])

    df = df.sort_values("Date").reset_index(drop=True)

    logger.info(
        "Loaded %d records from %s to %s",
        len(df),
        df["Date"].min().date(),
        df["Date"].max().date(),
    )
    return df


def get_data_summary(df: pd.DataFrame) -> dict:
    """Return basic descriptive statistics for the loaded dataset."""
    validate_dataframe_not_empty(df, "Expense data")
    return {
        "total_records": len(df),
        "date_range": {"start": df["Date"].min(), "end": df["Date"].max()},
        "unique_categories": df["Category"].nunique(),
        "categories": sorted(df["Category"].unique().tolist()),
        "total_amount": round(df["Amount"].sum(), 2),
        "mean_transaction": round(df["Amount"].mean(), 2),
        "min_transaction": round(df["Amount"].min(), 2),
        "max_transaction": round(df["Amount"].max(), 2),
    }


def print_data_summary(df: pd.DataFrame, date_fmt: str = "%m/%d/%Y") -> None:
    summary = get_data_summary(df)
    start = summary["date_range"]["start"].strftime(date_fmt)
    end = summary["date_range"]["end"].strftime(date_fmt)

    print("\n" + "=" * 65)
    print("LOADED DATA SUMMARY")
    print("=" * 65)
    print(f"  Records     : {summary['total_records']}")
    print(f"  Period      : {start} — {end}")
    print(f"  Categories  : {', '.join(summary['categories'])}")
    print(f"  Total spent : ${summary['total_amount']:,.2f}")
    print(f"  Avg / txn   : ${summary['mean_transaction']:,.2f}")
    print("=" * 65 + "\n")
