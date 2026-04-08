"""
Shared pytest fixtures for the expense-tracker test suite.
"""

import pandas as pd
import pytest


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Minimal well-formed expense DataFrame used across multiple test modules."""
    data = {
        "Date": pd.to_datetime([
            "2024-01-10", "2024-01-18", "2024-01-25",
            "2024-02-03", "2024-02-14", "2024-02-20",
            "2024-03-05", "2024-03-15", "2024-03-22",
        ]),
        "Category": [
            "Food", "Transport", "Food",
            "Services", "Transport", "Food",
            "Entertainment", "Food", "Services",
        ],
        "Amount": [250.50, 45.00, 180.75, 850.00, 50.00, 320.00, 120.00, 95.50, 850.00],
        "Description": [
            "Groceries", "Gas", "Restaurant",
            "Rent", "Uber", "Groceries",
            "Theater", "Coffee", "Rent",
        ],
    }
    return pd.DataFrame(data)


@pytest.fixture
def single_category_df() -> pd.DataFrame:
    """DataFrame with a single category — useful for edge-case tests."""
    data = {
        "Date": pd.to_datetime(["2024-01-01", "2024-01-15", "2024-02-01"]),
        "Category": ["Food", "Food", "Food"],
        "Amount": [100.0, 200.0, 150.0],
        "Description": ["Supermarket", "Restaurant", "Delivery"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def anomaly_df() -> pd.DataFrame:
    """
    DataFrame engineered to contain one clear outlier.

    Food transactions hover around $100 with low variance; the $5000 entry
    is a clear high-z outlier that should be flagged at z_threshold=2.0.
    """
    data = {
        "Date": pd.to_datetime([
            "2024-01-01", "2024-01-08", "2024-01-15",
            "2024-01-22", "2024-02-01", "2024-02-08",
            "2024-02-15", "2024-02-22", "2024-03-01",
        ]),
        "Category": ["Food"] * 5 + ["Transport"] * 4,
        "Amount": [100.0, 102.0, 98.0, 101.0, 5000.0, 50.0, 52.0, 48.0, 51.0],
        "Description": [
            "Groceries", "Restaurant", "Groceries", "Coffee", "Catering",
            "Gas", "Uber", "Bus", "Taxi",
        ],
    }
    return pd.DataFrame(data)
