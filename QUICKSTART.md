# Quick Start Guide

## Get Started in 3 Steps

### 1. Install Dependencies

```bash
cd expense_analysis_refactored/
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# With default settings
python main.py

# With custom options
python main.py --input data/expenses_example.csv --output output/ --log-level INFO
```

### 3. View Results

- **Charts**: Check the `output/` directory for PNG visualizations
- **Logs**: Check `logs/expense_analysis.log` for detailed execution log
- **Console**: Analysis summary is displayed in terminal

## Common Commands

```bash
# Show help
python main.py --help

# Run with DEBUG logging
python main.py --log-level DEBUG

# Use custom config
python main.py --config config/config.json

# Process different file
python main.py --input path/to/your/expenses.csv
```

## Input File Format

Your CSV file must have these columns:

```csv
Date,Category,Amount,Description
2024-01-15,Food,250.50,Weekly groceries
2024-01-18,Transport,45.00,Gas
```

**Column Requirements:**
- `Date`: Format YYYY-MM-DD
- `Category`: Any text
- `Amount`: Positive number
- `Description`: Any text (can be empty if config allows)

## Run Tests

```bash
# Install pytest first
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Project Structure

```
expense_analysis_refactored/
├── main.py              # Run this file
├── config/config.json   # Modify settings here
├── data/                # Put your CSV files here
├── output/              # Charts appear here
├── logs/                # Log files appear here
└── README.md            # Full documentation
```

## Troubleshooting

### "File not found"
Make sure your CSV file path is correct and the file exists.

### "Missing columns"
Check that your CSV has all required columns: Date, Category, Amount, Description

### "Invalid date format"
Dates must be in YYYY-MM-DD format (e.g., 2024-01-15)

### "Permission denied"
Make sure you have write permissions for `output/` and `logs/` directories

## Next Steps

1. Read the full [README.md](README.md) for comprehensive documentation
2. Check [IMPROVEMENTS.md](IMPROVEMENTS.md) to see all refactoring details
3. Explore the test suite in `tests/` for usage examples
4. Customize `config/config.json` for your needs

## Support

- Check `logs/expense_analysis.log` for detailed error information
- Run with `--log-level DEBUG` for maximum verbosity
- Review test files in `tests/` for code examples

---

**Ready to use!** The application is fully functional and production-ready.
