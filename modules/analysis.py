"""
Statistical analysis and anomaly detection for personal expense data.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

from utils.validators import validate_dataframe_not_empty, validate_required_columns

logger = logging.getLogger(__name__)


def calculate_total_spent(df: pd.DataFrame) -> float:
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ["Amount"], "Expense data")
    total = round(float(df["Amount"].sum()), 2)
    logger.debug("Total spent: $%.2f", total)
    return total


def calculate_monthly_breakdown(df: pd.DataFrame) -> dict[str, Any]:
    """
    Aggregate spending by calendar month.

    Returns a dict with:
        - ``average``: mean monthly spend
        - ``table``: DataFrame with columns Month, Total, Count
    """
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ["Date", "Amount"], "Expense data")

    tmp = df.copy()
    tmp["Month"] = tmp["Date"].dt.to_period("M")

    monthly = (
        tmp.groupby("Month")["Amount"]
        .agg(Total="sum", Count="count")
        .reset_index()
    )
    monthly["Month"] = monthly["Month"].astype(str)
    monthly["Total"] = monthly["Total"].round(2)

    avg = round(float(monthly["Total"].mean()), 2)
    logger.info("Monthly average: $%.2f across %d months", avg, len(monthly))
    return {"average": avg, "table": monthly}


def calculate_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return per-category totals, transaction counts, and share of total spend.

    Sorted descending by total.
    """
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ["Category", "Amount"], "Expense data")

    agg = (
        df.groupby("Category")["Amount"]
        .agg(Total="sum", Count="count")
        .reset_index()
    )
    agg["Total"] = agg["Total"].round(2)
    grand_total = agg["Total"].sum()
    agg["Share"] = (agg["Total"] / grand_total * 100).round(2)
    agg = agg.sort_values("Total", ascending=False).reset_index(drop=True)

    logger.debug("Category breakdown: %d categories, total $%.2f", len(agg), grand_total)
    return agg


def find_extremes(df: pd.DataFrame, date_fmt: str = "%m/%d/%Y") -> dict[str, Any]:
    """Return the single highest and lowest individual transactions."""
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ["Date", "Category", "Amount"], "Expense data")

    def _row_to_dict(row: pd.Series) -> dict[str, Any]:
        return {
            "amount": round(float(row["Amount"]), 2),
            "date": row["Date"].strftime(date_fmt),
            "category": row["Category"],
            "description": row.get("Description", "N/A"),
        }

    result = {
        "highest": _row_to_dict(df.loc[df["Amount"].idxmax()]),
        "lowest": _row_to_dict(df.loc[df["Amount"].idxmin()]),
    }
    logger.debug(
        "Extremes — high: $%.2f, low: $%.2f",
        result["highest"]["amount"],
        result["lowest"]["amount"],
    )
    return result


def detect_anomalies(df: pd.DataFrame, z_threshold: float = 2.0) -> pd.DataFrame:
    """
    Flag transactions that are statistically unusual relative to their spending category.

    Each transaction is compared against the mean and spread of its category.
    A transaction is flagged when it deviates beyond ``z_threshold``. Categories
    with fewer than 3 transactions are skipped — not enough history for a reliable baseline.

    Args:
        df: Expense DataFrame.
        z_threshold: Detection sensitivity. Lower values flag more transactions.

    Returns:
        DataFrame of flagged rows with additional columns:
            - ``z_score``: deviation from the category mean
            - ``direction``: "HIGH" or "LOW"
            - ``explanation``: human-readable description
    """
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ["Category", "Amount"], "Expense data")

    _empty = pd.DataFrame(
        columns=["Date", "Category", "Amount", "Description", "z_score", "direction", "explanation"]
    )

    cat_stats = (
        df.groupby("Category")["Amount"]
        .agg(cat_mean="mean", cat_std="std", cat_count="count")
        .reset_index()
    )

    enriched = df.merge(cat_stats, on="Category", how="left")
    enriched = enriched[enriched["cat_count"] >= 3].copy()

    if enriched.empty:
        logger.info("Not enough data per category for anomaly detection (need >=3 txns)")
        return _empty

    enriched["z_score"] = (
        (enriched["Amount"] - enriched["cat_mean"]) / enriched["cat_std"]
    ).round(2)

    anomalies = enriched[enriched["z_score"].abs() >= z_threshold].copy()

    if anomalies.empty:
        logger.info("No anomalies detected at z=%.1f", z_threshold)
        return _empty

    anomalies["direction"] = np.where(anomalies["z_score"] > 0, "HIGH", "LOW")
    anomalies["explanation"] = anomalies.apply(
        lambda r: (
            f"${r['Amount']:.2f} is {abs(r['z_score']):.1f}\u03c3 "
            f"{'above' if r['z_score'] > 0 else 'below'} "
            f"the {r['Category']} mean of ${r['cat_mean']:.2f}"
        ),
        axis=1,
    )

    logger.info("Detected %d anomalous transaction(s) at z=%.1f", len(anomalies), z_threshold)
    return anomalies[
        ["Date", "Category", "Amount", "Description", "z_score", "direction", "explanation"]
    ].reset_index(drop=True)


def generate_summary(
    df: pd.DataFrame, date_fmt: str = "%m/%d/%Y", z_threshold: float = 2.0
) -> dict[str, Any]:
    """
    Run the full analysis suite and return a single results dictionary.

    Keys: ``total_spent``, ``num_transactions``, ``period``, ``monthly``,
    ``by_category``, ``extremes``, ``anomalies``.
    """
    validate_dataframe_not_empty(df, "Expense data")

    logger.info("Generating full expense summary")
    summary: dict[str, Any] = {
        "total_spent": calculate_total_spent(df),
        "num_transactions": len(df),
        "period": {
            "start": df["Date"].min().strftime(date_fmt),
            "end": df["Date"].max().strftime(date_fmt),
        },
        "monthly": calculate_monthly_breakdown(df),
        "by_category": calculate_by_category(df),
        "extremes": find_extremes(df, date_fmt),
        "anomalies": detect_anomalies(df, z_threshold),
    }
    logger.info(
        "Summary ready: %d transactions, $%.2f total",
        summary["num_transactions"],
        summary["total_spent"],
    )
    return summary


def print_summary(summary: dict[str, Any]) -> None:
    """Pretty-print the analysis summary to stdout."""
    sep = "=" * 65
    thin = "-" * 65

    print(f"\n{sep}")
    print("EXPENSE ANALYSIS REPORT")
    print(sep)
    print(f"  Period       : {summary['period']['start']} — {summary['period']['end']}")
    print(f"  Transactions : {summary['num_transactions']}")
    print(f"  Total spent  : ${summary['total_spent']:,.2f}")
    print(f"  Monthly avg  : ${summary['monthly']['average']:,.2f}")

    print("\n  Highest single transaction:")
    h = summary["extremes"]["highest"]
    print(f"    ${h['amount']:,.2f}  |  {h['date']}  |  {h['category']}  |  {h['description']}")

    print("\n  Lowest single transaction:")
    lo = summary["extremes"]["lowest"]
    print(f"    ${lo['amount']:,.2f}  |  {lo['date']}  |  {lo['category']}  |  {lo['description']}")

    print(f"\n{thin}")
    print(f"  {'Category':<20} {'Total':>10}  {'Share':>7}  {'Txns':>5}")
    print(thin)
    for _, row in summary["by_category"].iterrows():
        print(
            f"  {row['Category']:<20} ${row['Total']:>9,.2f}  {row['Share']:>6.1f}%  {row['Count']:>5}"
        )

    anomalies = summary.get("anomalies")
    if anomalies is not None and not anomalies.empty:
        print(f"\n{thin}")
        print(f"  ANOMALIES DETECTED ({len(anomalies)} transaction(s))")
        print(thin)
        for _, row in anomalies.iterrows():
            flag = "+" if row["direction"] == "HIGH" else "-"
            print(f"  [{flag}] {row['explanation']}")
            print(f"    Date: {row['Date'].strftime('%m/%d/%Y')}  |  {row['Description']}")
    else:
        print("\n  No anomalies detected.")

    print(sep + "\n")
