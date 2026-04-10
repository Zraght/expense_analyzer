"""
Tests for the validation utilities (utils/validators.py).
"""

import pandas as pd
import pytest

from utils.validators import (
    DataValidationError,
    check_data_quality,
    validate_dataframe_not_empty,
    validate_input_path,
    validate_output_directory,
    validate_required_columns,
)


class TestValidateDataframeNotEmpty:
    def test_valid_dataframe_passes(self, sample_df):
        validate_dataframe_not_empty(sample_df)  # should not raise

    def test_empty_dataframe_raises(self):
        with pytest.raises(DataValidationError):
            validate_dataframe_not_empty(pd.DataFrame())

    def test_none_raises(self):
        with pytest.raises(DataValidationError):
            validate_dataframe_not_empty(None)


class TestValidateRequiredColumns:
    def test_all_present_passes(self, sample_df):
        validate_required_columns(sample_df, ["Date", "Category", "Amount"])

    def test_missing_column_raises(self, sample_df):
        with pytest.raises(DataValidationError, match="missing columns"):
            validate_required_columns(sample_df, ["Date", "Nonexistent"])

    def test_empty_required_list_passes(self, sample_df):
        validate_required_columns(sample_df, [])  # nothing required → should not raise


class TestValidateInputPath:
    def test_existing_csv(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("Date,Category,Amount,Description\n")
        result = validate_input_path(f)
        assert result == f

    def test_existing_xlsx(self, tmp_path):
        f = tmp_path / "data.xlsx"
        f.write_bytes(b"PK")  # not a real xlsx but exists
        # openpyxl would fail later — here we only test path validation
        result = validate_input_path(f)
        assert result == f

    def test_nonexistent_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            validate_input_path(tmp_path / "missing.csv")

    def test_unsupported_extension_raises(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text("{}")
        with pytest.raises(ValueError, match="Unsupported"):
            validate_input_path(f)


class TestValidateOutputDirectory:
    def test_creates_directory(self, tmp_path):
        new_dir = tmp_path / "new" / "nested"
        result = validate_output_directory(new_dir)
        assert result.exists()
        assert result.is_dir()

    def test_existing_directory_passes(self, tmp_path):
        result = validate_output_directory(tmp_path)
        assert result == tmp_path


class TestCheckDataQuality:
    def test_removes_duplicates(self):
        df = pd.DataFrame({
            "Date": ["2024-01-01", "2024-01-01"],
            "Category": ["Food", "Food"],
            "Amount": [100.0, 100.0],
            "Description": ["Groceries", "Groceries"],
        })
        cleaned, report = check_data_quality(df, remove_duplicates=True)
        assert len(cleaned) == 1
        assert report["duplicates_removed"] == 1

    def test_no_duplicates_unchanged(self, sample_df):
        cleaned, report = check_data_quality(sample_df, remove_duplicates=True)
        assert len(cleaned) == len(sample_df)
        assert report.get("duplicates_removed", 0) == 0

    def test_reports_null_counts(self):
        df = pd.DataFrame({
            "Date": ["2024-01-01", None],
            "Category": ["Food", "Food"],
            "Amount": [100.0, 200.0],
            "Description": ["A", "B"],
        })
        _, report = check_data_quality(df)
        assert "Date" in report.get("null_counts", {})

    def test_returns_dataframe_and_dict(self, sample_df):
        result = check_data_quality(sample_df)
        assert isinstance(result, tuple)
        cleaned, report = result
        assert isinstance(cleaned, pd.DataFrame)
        assert isinstance(report, dict)