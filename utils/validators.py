"""
Data validation utilities used across the pipeline.
"""

import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Raised when a DataFrame fails a structural or content check."""


def validate_dataframe_not_empty(df: pd.DataFrame, name: str = "DataFrame") -> None:
    if df is None or df.empty:
        msg = f"{name} is empty — no data to process"
        logger.error(msg)
        raise DataValidationError(msg)
    logger.debug("%s OK: %d rows", name, len(df))


def validate_required_columns(
    df: pd.DataFrame, required: list[str], name: str = "DataFrame"
) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        msg = (
            f"{name} is missing columns: {missing}\n"
            f"Found: {list(df.columns)}"
        )
        logger.error(msg)
        raise DataValidationError(msg)


def validate_input_path(path: Path) -> Path:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if path.suffix.lower() not in {".csv", ".xlsx", ".xls"}:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    return path


def validate_output_directory(path: Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def check_data_quality(
    df: pd.DataFrame,
    remove_duplicates: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Remove duplicate rows and report data quality metrics.

    Returns the cleaned DataFrame and a report dict for logging/display.
    """
    original = len(df)
    report: dict[str, Any] = {"original_rows": original}

    if remove_duplicates:
        dupes = df.duplicated().sum()
        df = df.drop_duplicates()
        report["duplicates_removed"] = int(dupes)

    null_counts = df.isnull().sum()
    report["null_counts"] = null_counts[null_counts > 0].to_dict()
    report["final_rows"] = len(df)

    if len(df) < original:
        logger.info(
            "Data quality: %d → %d rows (%d removed)",
            original,
            len(df),
            original - len(df),
        )

    return df, report
