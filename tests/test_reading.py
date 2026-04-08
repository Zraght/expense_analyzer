"""
Tests for the data ingestion module (modules/reading.py).
"""

import textwrap
from pathlib import Path

import pandas as pd
import pytest

from modules.reading import get_data_summary, read_expenses
from utils.validators import DataValidationError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def write_csv(tmp_path: Path, content: str, filename: str = "expenses.csv") -> Path:
    p = tmp_path / filename
    p.write_text(textwrap.dedent(content).strip())
    return p


VALID_CSV = """\
    Date,Category,Amount,Description
    2024-01-10,Food,250.50,Groceries
    2024-01-18,Transport,45.00,Gas
    2024-02-05,Services,850.00,Rent
"""


# ---------------------------------------------------------------------------
# CSV reading
# ---------------------------------------------------------------------------


class TestReadExpensesCSV:
    def test_returns_dataframe(self, tmp_path):
        path = write_csv(tmp_path, VALID_CSV)
        df = read_expenses(path)
        assert isinstance(df, pd.DataFrame)

    def test_row_count(self, tmp_path):
        path = write_csv(tmp_path, VALID_CSV)
        df = read_expenses(path)
        assert len(df) == 3

    def test_date_column_is_datetime(self, tmp_path):
        path = write_csv(tmp_path, VALID_CSV)
        df = read_expenses(path)
        assert pd.api.types.is_datetime64_any_dtype(df["Date"])

    def test_amount_column_is_numeric(self, tmp_path):
        path = write_csv(tmp_path, VALID_CSV)
        df = read_expenses(path)
        assert pd.api.types.is_numeric_dtype(df["Amount"])

    def test_sorted_by_date(self, tmp_path):
        csv = """\
            Date,Category,Amount,Description
            2024-03-01,Food,100,A
            2024-01-01,Food,200,B
            2024-02-01,Food,150,C
        """
        path = write_csv(tmp_path, csv)
        df = read_expenses(path)
        dates = df["Date"].tolist()
        assert dates == sorted(dates)

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            read_expenses("nonexistent_file.csv")

    def test_empty_file_raises(self, tmp_path):
        path = write_csv(tmp_path, "Date,Category,Amount,Description\n")
        with pytest.raises(DataValidationError):
            read_expenses(path)

    def test_missing_required_column_raises(self, tmp_path):
        csv = "Date,Category,Description\n2024-01-01,Food,Groceries"
        path = write_csv(tmp_path, csv)
        with pytest.raises(DataValidationError):
            read_expenses(path)

    def test_invalid_dates_are_dropped(self, tmp_path):
        csv = """\
            Date,Category,Amount,Description
            2024-01-01,Food,100,Valid
            not-a-date,Food,200,Invalid
        """
        path = write_csv(tmp_path, csv)
        df = read_expenses(path)
        assert len(df) == 1

    def test_non_numeric_amounts_are_dropped(self, tmp_path):
        csv = """\
            Date,Category,Amount,Description
            2024-01-01,Food,100,Valid
            2024-01-02,Food,bad,Invalid
        """
        path = write_csv(tmp_path, csv)
        df = read_expenses(path)
        assert len(df) == 1


# ---------------------------------------------------------------------------
# Excel reading
# ---------------------------------------------------------------------------


class TestReadExpensesExcel:
    def test_reads_xlsx(self, tmp_path):
        df_in = pd.DataFrame({
            "Date": ["2024-01-10", "2024-02-05"],
            "Category": ["Food", "Services"],
            "Amount": [100.0, 850.0],
            "Description": ["Groceries", "Rent"],
        })
        path = tmp_path / "expenses.xlsx"
        df_in.to_excel(path, index=False)

        df_out = read_expenses(path)
        assert len(df_out) == 2
        assert pd.api.types.is_datetime64_any_dtype(df_out["Date"])

    def test_unsupported_extension_raises(self, tmp_path):
        path = tmp_path / "data.json"
        path.write_text("{}")
        with pytest.raises(ValueError, match="Unsupported file format"):
            read_expenses(path)


# ---------------------------------------------------------------------------
# Data summary
# ---------------------------------------------------------------------------


class TestGetDataSummary:
    def test_summary_keys(self, sample_df):
        summary = get_data_summary(sample_df)
        for key in ("total_records", "date_range", "unique_categories", "categories",
                    "total_amount", "mean_transaction"):
            assert key in summary

    def test_total_records(self, sample_df):
        summary = get_data_summary(sample_df)
        assert summary["total_records"] == len(sample_df)

    def test_categories_sorted(self, sample_df):
        summary = get_data_summary(sample_df)
        cats = summary["categories"]
        assert cats == sorted(cats)

    def test_total_amount(self, sample_df):
        summary = get_data_summary(sample_df)
        expected = round(float(sample_df["Amount"].sum()), 2)
        assert summary["total_amount"] == expected
