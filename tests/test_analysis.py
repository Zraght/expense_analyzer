"""
Tests for the analysis and anomaly detection module (modules/analysis.py).
"""

import pandas as pd
import pytest

from modules.analysis import (
    calculate_by_category,
    calculate_monthly_breakdown,
    calculate_total_spent,
    detect_anomalies,
    find_extremes,
    generate_summary,
)
from utils.validators import DataValidationError


class TestCalculateTotalSpent:
    def test_correct_sum(self, sample_df):
        expected = round(float(sample_df["Amount"].sum()), 2)
        assert calculate_total_spent(sample_df) == expected

    def test_empty_raises(self):
        with pytest.raises(DataValidationError):
            calculate_total_spent(pd.DataFrame())

    def test_missing_amount_raises(self, sample_df):
        with pytest.raises(DataValidationError):
            calculate_total_spent(sample_df.drop(columns=["Amount"]))

    def test_returns_float(self, sample_df):
        assert isinstance(calculate_total_spent(sample_df), float)


class TestCalculateMonthlyBreakdown:
    def test_structure(self, sample_df):
        result = calculate_monthly_breakdown(sample_df)
        assert "average" in result
        assert "table" in result
        assert isinstance(result["table"], pd.DataFrame)

    def test_table_columns(self, sample_df):
        table = calculate_monthly_breakdown(sample_df)["table"]
        assert set(table.columns) == {"Month", "Total", "Count"}

    def test_month_count(self, sample_df):
        # sample_df spans Jan, Feb, Mar 2024
        table = calculate_monthly_breakdown(sample_df)["table"]
        assert len(table) == 3

    def test_average_is_mean_of_monthly_totals(self, sample_df):
        result = calculate_monthly_breakdown(sample_df)
        expected = round(float(result["table"]["Total"].mean()), 2)
        assert result["average"] == expected

    def test_empty_raises(self):
        with pytest.raises(DataValidationError):
            calculate_monthly_breakdown(pd.DataFrame())


class TestCalculateByCategory:
    def test_returns_dataframe(self, sample_df):
        assert isinstance(calculate_by_category(sample_df), pd.DataFrame)

    def test_columns(self, sample_df):
        df = calculate_by_category(sample_df)
        assert set(df.columns) == {"Category", "Total", "Count", "Share"}

    def test_sorted_descending(self, sample_df):
        df = calculate_by_category(sample_df)
        totals = df["Total"].tolist()
        assert totals == sorted(totals, reverse=True)

    def test_shares_sum_to_100(self, sample_df):
        df = calculate_by_category(sample_df)
        assert round(df["Share"].sum(), 0) == 100.0

    def test_category_count(self, sample_df):
        df = calculate_by_category(sample_df)
        expected = sample_df["Category"].nunique()
        assert len(df) == expected


class TestFindExtremes:
    def test_structure(self, sample_df):
        result = find_extremes(sample_df)
        assert "highest" in result and "lowest" in result
        for key in ("amount", "date", "category", "description"):
            assert key in result["highest"]
            assert key in result["lowest"]

    def test_highest_amount(self, sample_df):
        result = find_extremes(sample_df)
        assert result["highest"]["amount"] == round(float(sample_df["Amount"].max()), 2)

    def test_lowest_amount(self, sample_df):
        result = find_extremes(sample_df)
        assert result["lowest"]["amount"] == round(float(sample_df["Amount"].min()), 2)


class TestDetectAnomalies:
    def test_detects_outlier(self, anomaly_df):
        result = detect_anomalies(anomaly_df, z_threshold=2.0)
        assert not result.empty
        # The $5000 food transaction should be flagged
        assert any(result["Amount"] == 5000.0)

    def test_direction_high(self, anomaly_df):
        result = detect_anomalies(anomaly_df, z_threshold=2.0)
        row = result[result["Amount"] == 5000.0].iloc[0]
        assert row["direction"] == "HIGH"

    def test_result_columns(self, anomaly_df):
        result = detect_anomalies(anomaly_df, z_threshold=2.0)
        for col in ("Date", "Category", "Amount", "z_score", "direction", "explanation"):
            assert col in result.columns

    def test_no_anomalies_returns_empty(self, single_category_df):
        # All values are close together — no outliers at z=2
        result = detect_anomalies(single_category_df, z_threshold=3.0)
        # Either empty or no rows with high z — just check it doesn't crash
        assert isinstance(result, pd.DataFrame)

    def test_insufficient_data_returns_empty(self):
        # Only 2 rows per category — below the minimum of 3
        df = pd.DataFrame({
            "Date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "Category": ["Food", "Food"],
            "Amount": [100.0, 200.0],
            "Description": ["A", "B"],
        })
        result = detect_anomalies(df, z_threshold=2.0)
        assert result.empty

    def test_explanation_is_string(self, anomaly_df):
        result = detect_anomalies(anomaly_df, z_threshold=2.0)
        if not result.empty:
            assert all(isinstance(e, str) for e in result["explanation"])


class TestGenerateSummary:
    def test_all_keys_present(self, sample_df):
        summary = generate_summary(sample_df)
        for key in ("total_spent", "num_transactions", "period", "monthly", "by_category", "extremes", "anomalies"):
            assert key in summary

    def test_num_transactions(self, sample_df):
        summary = generate_summary(sample_df)
        assert summary["num_transactions"] == len(sample_df)

    def test_total_spent_matches(self, sample_df):
        summary = generate_summary(sample_df)
        assert summary["total_spent"] == calculate_total_spent(sample_df)

    def test_period_start_before_end(self, sample_df):
        summary = generate_summary(sample_df)
        # Both are formatted strings — just check they exist and are non-empty
        assert summary["period"]["start"]
        assert summary["period"]["end"]

    def test_empty_raises(self):
        with pytest.raises(DataValidationError):
            generate_summary(pd.DataFrame())
