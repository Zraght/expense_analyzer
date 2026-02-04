"""
Main CLI application for personal expense analysis.

This module provides a command-line interface for analyzing personal expenses
with support for configuration files, logging, and customizable outputs.

Author: Joseantonio Caleb Gonzales Chumbe
Date: 2026
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from utils import (
    load_config,
    setup_logging,
    get_logger,
    validate_input_path,
    validate_output_directory,
    ConfigurationError
)
from modules.reading import read_expenses_csv, show_data_summary
from modules.analysis import generate_complete_summary, display_analysis_summary
from modules.visualization import generate_all_charts, configure_plot_style

# Module logger
logger = get_logger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace.
        
    Example:
        >>> args = parse_arguments()
        >>> print(args.input)
    """
    parser = argparse.ArgumentParser(
        description='Personal Expense Analysis Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run with default settings
  python main.py
  
  # Specify input and output paths
  python main.py --input data/expenses.csv --output results/
  
  # Use custom configuration
  python main.py --config config/custom.json
  
  # Set logging level
  python main.py --log-level DEBUG
  
  # Show plots interactively
  python main.py --show-plots

For more information, see README.md
        '''
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        help='Path to input CSV file (default: from config or data/expenses_example.csv)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Path to output directory for charts (default: from config or output/)'
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to configuration JSON file (default: config/config.json)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: from config or INFO)'
    )
    
    parser.add_argument(
        '--show-plots',
        action='store_true',
        help='Display plots interactively (default: False)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )
    
    return parser.parse_args()


def print_header() -> None:
    """Print the application header."""
    print("\n" + "="*70)
    print("PERSONAL EXPENSE ANALYSIS SYSTEM v2.0")
    print("="*70)
    print(f"Execution date: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}")
    print("="*70 + "\n")


def print_separator(title: str = "") -> None:
    """
    Print a visual separator with an optional title.
    
    Args:
        title: Optional title to display in the separator.
    """
    if title:
        print("\n" + "="*70)
        print(f"{title.upper()}")
        print("="*70 + "\n")
    else:
        print("\n" + "-"*70 + "\n")


def main() -> int:
    """
    Execute the complete expense analysis workflow.
    
    This function orchestrates:
    1. Configuration loading
    2. Logging setup
    3. Data reading from CSV file
    4. Statistical analysis of expenses
    5. Visualization generation
    
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Print header
        print_header()
        
        # Load configuration
        print("Loading configuration...")
        try:
            config_path = Path(args.config) if args.config else Path('config/config.json')
            config = load_config(config_path)
            print(f"Configuration loaded: {config_path if config_path.exists() else 'using defaults'}\n")
        except ConfigurationError as e:
            print(f"Configuration error: {e}")
            print("Using default configuration.\n")
            config = load_config(None)
        
        # Override config with command-line arguments
        if args.log_level:
            config.config['logging']['level'] = args.log_level
        
        if args.show_plots:
            config.config['visualization']['show_plots'] = True
        
        # Setup logging
        log_config = config.get('logging')
        logger_instance = setup_logging(
            log_level=log_config.get('level', 'INFO'),
            log_format=log_config.get('format'),
            date_format=log_config.get('date_format'),
            log_dir=Path(config.get('paths', 'logs', default='logs')),
            log_to_console=log_config.get('log_to_console', True),
            log_to_file=log_config.get('log_to_file', True),
            max_bytes=log_config.get('max_bytes', 10485760),
            backup_count=log_config.get('backup_count', 5)
        )
        
        logger.info("="*70)
        logger.info("Expense Analysis Pipeline Started")
        logger.info("="*70)
        logger.info(f"Configuration: {config_path if args.config else 'defaults'}")
        logger.info(f"Log level: {log_config.get('level', 'INFO')}")
        
        # Determine input file path
        if args.input:
            input_path = Path(args.input)
        else:
            input_path = Path(config.get('paths', 'default_input', default='data/expenses_example.csv'))
        
        # Determine output directory
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path(config.get('paths', 'default_output', default='output'))
        
        # Validate paths
        print("Validating paths...")
        try:
            input_path = validate_input_path(input_path)
            output_path = validate_output_directory(output_path)
            logger.info(f"Input file: {input_path}")
            logger.info(f"Output directory: {output_path}")
            print(f"Input file: {input_path}")
            print(f"Output directory: {output_path}\n")
        except (FileNotFoundError, ValueError) as e:
            print(f"Path validation error: {e}")
            logger.error(f"Path validation failed: {e}")
            return 1
        
        # Configure visualization style
        viz_config = config.get('visualization')
        configure_plot_style(
            style=viz_config.get('style', 'seaborn-v0_8-darkgrid'),
            palette=viz_config.get('color_palette', 'husl')
        )
        
        # Step 1: Data Reading
        print_separator("Step 1: Data Reading")
        logger.info("Step 1: Reading expense data")
        
        expenses_df = read_expenses_csv(
            input_path,
            required_columns=config.get('data_validation', 'required_columns'),
            date_format=config.get('analysis', 'date_format', default='%Y-%m-%d')
        )
        
        show_data_summary(
            expenses_df,
            output_format=config.get('analysis', 'output_date_format', default='%m/%d/%Y')
        )
        
        # Step 2: Data Analysis
        print_separator("Step 2: Data Analysis")
        logger.info("Step 2: Performing statistical analysis")
        print("Calculating expense statistics and metrics...")
        
        summary = generate_complete_summary(
            expenses_df,
            date_format=config.get('analysis', 'output_date_format', default='%m/%d/%Y')
        )
        
        display_analysis_summary(summary)
        
        # Step 3: Data Visualization
        print_separator("Step 3: Chart Generation")
        logger.info("Step 3: Generating visualizations")
        print("Creating expense visualizations...")
        
        # Prepare visualization configuration
        viz_chart_config = {
            'dpi': viz_config.get('dpi', 300),
            'figure_size_bar': viz_config.get('figure_size_bar', [12, 6]),
            'figure_size_pie': viz_config.get('figure_size_pie', [12, 8]),
            'figure_size_line': viz_config.get('figure_size_line', [14, 6]),
            'timestamp_format': config.get('output', 'file_naming', 'timestamp_format', default='%Y%m%d_%H%M%S'),
            'show_plots': viz_config.get('show_plots', False)
        }
        
        chart_paths = generate_all_charts(expenses_df, output_path, viz_chart_config)
        
        # Display paths of generated files
        print("\nCharts generated successfully:")
        print("="*70)
        for chart_type, path in chart_paths.items():
            filename = path.name
            print(f"   {chart_type.capitalize():15s} -> {filename}")
            logger.info(f"Chart created: {chart_type} - {path}")
        print("="*70)
        
        # Final Summary
        print_separator("Final Summary")
        logger.info("Analysis completed successfully")
        
        print("Analysis completed successfully!")
        print("\nGenerated results:")
        print(f"   - Total transactions analyzed: {len(expenses_df)}")
        print(f"   - Period analyzed: {summary['period']['start']} - {summary['period']['end']}")
        print(f"   - Total spent: ${summary['total_spent']:,.2f}")
        print(f"   - Monthly average: ${summary['monthly_average']['average_total']:,.2f}")
        print(f"   - Number of charts generated: {len(chart_paths)}")
        print(f"\nFiles saved in folder: '{output_path}/'\n")
        
        print("="*70)
        print("Thank you for using the Personal Expense Analysis System")
        print("="*70 + "\n")
        
        logger.info("="*70)
        logger.info("Expense Analysis Pipeline Completed Successfully")
        logger.info("="*70)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\nFile Error: {e}")
        logger.error(f"File not found: {e}")
        print("Verify that the CSV file exists and the path is correct.")
        return 1
        
    except ValueError as e:
        print(f"\nValidation Error: {e}")
        logger.error(f"Validation error: {e}")
        print("Check that the CSV file has the correct format.")
        return 1
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        logger.warning("Operation cancelled by user (KeyboardInterrupt)")
        return 130
        
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print("\nPlease review the error details in the log file.")
        print("For support, check README.md or contact the administrator.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
