"""
Chart generation for the expense tracker pipeline.

All charts are saved as PNG files. Pass ``show_plots=True`` in config
only during interactive sessions — the default is headless (Agg backend).
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from utils.validators import validate_dataframe_not_empty, validate_required_columns

logger = logging.getLogger(__name__)

_COLORS = plt.cm.Set3


def configure_plot_style(style: str = "seaborn-v0_8-darkgrid", palette: str = "husl") -> None:
    try:
        plt.style.use(style)
        sns.set_palette(palette)
    except Exception as exc:
        logger.warning("Could not apply plot style '%s': %s — using defaults", style, exc)


def _save_and_close(fig: plt.Figure, path: Path, dpi: int, show: bool) -> None:
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def _timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    return datetime.now().strftime(fmt)


def bar_chart_by_category(
    df: pd.DataFrame,
    output_dir: Path,
    config: dict[str, Any] | None = None,
) -> Path:
    """Bar chart of total spending per category, sorted descending."""
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ["Category", "Amount"], "Expense data")

    cfg = config or {}
    dpi = cfg.get("dpi", 300)
    figsize = tuple(cfg.get("figure_size_bar", [12, 6]))
    show = cfg.get("show_plots", False)

    by_cat = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=figsize)
    colors = _COLORS(range(len(by_cat)))
    bars = ax.bar(by_cat.index, by_cat.values, color=colors, edgecolor="black", linewidth=0.8)

    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h * 1.01,
            f"${h:,.0f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    ax.set_xlabel("Category", fontsize=11, fontweight="bold")
    ax.set_ylabel("Total Amount ($)", fontsize=11, fontweight="bold")
    ax.set_title("Total Spending by Category", fontsize=14, fontweight="bold", pad=16)
    ax.tick_params(axis="x", rotation=30)
    ax.yaxis.grid(True, alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    fig.tight_layout()

    path = output_dir / f"bar_category_{_timestamp()}.png"
    _save_and_close(fig, path, dpi, show)
    logger.info("Bar chart saved: %s", path)
    return path


def pie_chart_by_category(
    df: pd.DataFrame,
    output_dir: Path,
    config: dict[str, Any] | None = None,
) -> Path:
    """Pie chart of spending distribution across categories."""
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ["Category", "Amount"], "Expense data")

    cfg = config or {}
    dpi = cfg.get("dpi", 300)
    figsize = tuple(cfg.get("figure_size_pie", [12, 8]))
    show = cfg.get("show_plots", False)

    by_cat = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    colors = _COLORS(range(len(by_cat)))

    fig, ax = plt.subplots(figsize=figsize)
    wedges, texts, autotexts = ax.pie(
        by_cat.values,
        labels=by_cat.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        explode=[0.04] * len(by_cat),
        textprops={"fontsize": 10},
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontweight("bold")

    ax.set_title("Expense Distribution by Category", fontsize=14, fontweight="bold", pad=16)
    legend_labels = [f"{cat}: ${val:,.2f}" for cat, val in by_cat.items()]
    ax.legend(legend_labels, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)
    fig.tight_layout()

    path = output_dir / f"pie_category_{_timestamp()}.png"
    _save_and_close(fig, path, dpi, show)
    logger.info("Pie chart saved: %s", path)
    return path


def line_chart_monthly(
    df: pd.DataFrame,
    output_dir: Path,
    config: dict[str, Any] | None = None,
) -> Path:
    """Line chart of monthly spending with an average reference line."""
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ["Date", "Amount"], "Expense data")

    cfg = config or {}
    dpi = cfg.get("dpi", 300)
    figsize = tuple(cfg.get("figure_size_line", [14, 6]))
    show = cfg.get("show_plots", False)

    tmp = df.copy()
    tmp["Month"] = tmp["Date"].dt.to_period("M")
    monthly = tmp.groupby("Month")["Amount"].sum().reset_index()
    monthly["Month"] = monthly["Month"].astype(str)

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(
        monthly["Month"],
        monthly["Amount"],
        marker="o",
        linewidth=2.5,
        markersize=9,
        color="#2E86AB",
        markerfacecolor="#A23B72",
        markeredgecolor="white",
        markeredgewidth=1.5,
    )

    for _, row in monthly.iterrows():
        ax.text(
            row["Month"],
            row["Amount"] * 1.01,
            f"${row['Amount']:,.0f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    avg = monthly["Amount"].mean()
    ax.axhline(avg, color="red", linestyle="--", linewidth=1.5, alpha=0.7, label=f"Avg: ${avg:,.2f}")

    ax.set_xlabel("Month", fontsize=11, fontweight="bold")
    ax.set_ylabel("Total Spending ($)", fontsize=11, fontweight="bold")
    ax.set_title("Monthly Spending Trend", fontsize=14, fontweight="bold", pad=16)
    ax.tick_params(axis="x", rotation=30)
    ax.yaxis.grid(True, alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    ax.legend(fontsize=10)
    fig.tight_layout()

    path = output_dir / f"line_monthly_{_timestamp()}.png"
    _save_and_close(fig, path, dpi, show)
    logger.info("Line chart saved: %s", path)
    return path


def generate_all_charts(
    df: pd.DataFrame,
    output_dir: str | Path,
    config: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """
    Generate all three standard charts and return a map of ``{chart_type: path}``.

    Chart types: ``bar``, ``pie``, ``line``.
    """
    validate_dataframe_not_empty(df, "Expense data")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Generating charts in %s", output_dir)
    paths = {
        "bar": bar_chart_by_category(df, output_dir, config),
        "pie": pie_chart_by_category(df, output_dir, config),
        "line": line_chart_monthly(df, output_dir, config),
    }
    logger.info("All charts generated")
    return paths
