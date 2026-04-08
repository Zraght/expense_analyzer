"""
expense-tracker — Personal Expense Analysis Pipeline

CLI entry point. Orchestrates config loading, data ingestion,
statistical analysis, chart generation, and optional HTML reporting.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from utils import (
    ConfigurationError,
    load_config,
    setup_logging,
    get_logger,
    validate_input_path,
    validate_output_directory,
)
from modules.reading import read_expenses, print_data_summary
from modules.analysis import generate_summary, print_summary
from modules.visualization import generate_all_charts, configure_plot_style
from modules.reporter import generate_html_report

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="expense-tracker",
        description="Automated personal expense analysis with anomaly detection.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  expense-tracker
  expense-tracker -i data/expenses.xlsx -o results/
  expense-tracker -i data/expenses.csv --log-level DEBUG
  expense-tracker --no-report
        """,
    )
    parser.add_argument("-i", "--input", help="Path to CSV or Excel expense file")
    parser.add_argument("-o", "--output", help="Output directory for charts and reports")
    parser.add_argument("-c", "--config", help="Path to config JSON file")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Override logging level",
    )
    parser.add_argument(
        "--show-plots",
        action="store_true",
        help="Display charts interactively (requires a display)",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip HTML report generation",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    return parser


def _print_header() -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "=" * 65)
    print("  EXPENSE TRACKER  v1.0.0")
    print(f"  {ts}")
    print("=" * 65 + "\n")


def main() -> int:
    args = build_parser().parse_args()
    _print_header()

    # Configuration
    config_path = Path(args.config) if args.config else Path("config/config.json")
    try:
        config = load_config(config_path)
    except ConfigurationError as exc:
        print(f"[config] {exc} — falling back to defaults\n")
        config = load_config(None)

    if args.log_level:
        config.config["logging"]["level"] = args.log_level
    if args.show_plots:
        config.config["visualization"]["show_plots"] = True

    # Logging
    log_cfg = config.get("logging")
    setup_logging(
        log_level=log_cfg.get("level", "INFO"),
        log_format=log_cfg.get("format"),
        date_format=log_cfg.get("date_format"),
        log_dir=Path(config.get("paths", "logs", default="logs")),
        log_to_console=log_cfg.get("log_to_console", True),
        log_to_file=log_cfg.get("log_to_file", True),
        max_bytes=log_cfg.get("max_bytes", 10_485_760),
        backup_count=log_cfg.get("backup_count", 5),
    )
    logger.info("Pipeline started")

    # Path resolution
    input_path = Path(
        args.input or config.get("paths", "default_input", default="data/expenses_example.csv")
    )
    output_path = Path(
        args.output or config.get("paths", "default_output", default="output")
    )

    try:
        input_path = validate_input_path(input_path)
        output_path = validate_output_directory(output_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[path] {exc}")
        logger.error("Path validation failed: %s", exc)
        return 1

    logger.info("Input : %s", input_path)
    logger.info("Output: %s", output_path)

    # Step 1 — Data ingestion
    print("─" * 65)
    print("  STEP 1 / 3  —  Data Ingestion")
    print("─" * 65)

    required_cols = config.get("data_validation", "required_columns")
    date_fmt = config.get("analysis", "date_format", default="%Y-%m-%d")
    out_date_fmt = config.get("analysis", "output_date_format", default="%m/%d/%Y")

    df = read_expenses(input_path, required_columns=required_cols, date_format=date_fmt)
    print_data_summary(df, date_fmt=out_date_fmt)

    # Step 2 — Analysis
    print("─" * 65)
    print("  STEP 2 / 3  —  Analysis & Anomaly Detection")
    print("─" * 65)

    z_threshold = config.get("analysis", "anomaly_z_threshold", default=2.0)
    summary = generate_summary(df, date_fmt=out_date_fmt, z_threshold=z_threshold)
    print_summary(summary)

    # Step 3 — Visualizations
    print("─" * 65)
    print("  STEP 3 / 3  —  Visualizations")
    print("─" * 65)

    viz_cfg = config.get("visualization")
    configure_plot_style(
        style=viz_cfg.get("style", "seaborn-v0_8-darkgrid"),
        palette=viz_cfg.get("color_palette", "husl"),
    )

    chart_cfg = {
        "dpi": viz_cfg.get("dpi", 300),
        "figure_size_bar": viz_cfg.get("figure_size_bar", [12, 6]),
        "figure_size_pie": viz_cfg.get("figure_size_pie", [12, 8]),
        "figure_size_line": viz_cfg.get("figure_size_line", [14, 6]),
        "show_plots": viz_cfg.get("show_plots", False),
    }

    chart_paths = generate_all_charts(df, output_path, chart_cfg)
    for chart_type, path in chart_paths.items():
        print(f"  [{chart_type:<4}] {path.name}")
        logger.info("Chart saved: %s", path)

    # HTML report
    report_path = None
    if not args.no_report and config.get("output", "export_html", default=True):
        ts_fmt = config.get("output", "timestamp_format", default="%Y%m%d_%H%M%S")
        report_path = generate_html_report(summary, chart_paths, output_path, ts_fmt)
        print(f"\n  [html] {report_path.name}")

    print("\n" + "=" * 65)
    print(f"  Analysis complete — {len(df)} transactions processed")
    print(f"  Output: {output_path}/")
    print("=" * 65 + "\n")

    logger.info("Pipeline completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
