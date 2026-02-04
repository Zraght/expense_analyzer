# Installation and Verification Guide

## Quick Start (30 seconds)

After extracting the ZIP archive, execute these commands:

```bash
# Navigate to the project directory
cd expense_analyzer_final

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

**Expected Result**: The application will analyze the example dataset and generate three charts in the `output/` directory.

---

## Detailed Verification Steps

### 1. Extract the Archive

```bash
unzip expense_analyzer_final.zip
cd expense_analyzer_final
```

### 2. Verify Project Structure

Ensure all files are present:

```bash
# Check directory structure
ls -la

# Expected directories:
# - config/     (configuration files)
# - data/       (sample dataset)
# - logs/       (will contain logs after execution)
# - modules/    (core business logic)
# - output/     (will contain generated charts)
# - tests/      (unit tests)
# - utils/      (utility modules)
```

### 3. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected Output**:
```
Successfully installed pandas-2.x.x numpy-1.x.x matplotlib-3.x.x seaborn-0.x.x ...
```

### 5. Verify Installation

#### A. Check CLI Help

```bash
python main.py --help
```

**Expected**: Help text displaying all available command-line options.

#### B. Run Default Analysis

```bash
python main.py
```

**Expected Output**:
```
======================================================================
PERSONAL EXPENSE ANALYSIS SYSTEM v2.0
======================================================================
Execution date: MM/DD/YYYY HH:MM:SS
======================================================================

Loading configuration...
Configuration loaded: config/config.json

...

Successfully generated 3 charts in: output/
```

#### C. Verify Generated Files

```bash
ls -l output/
```

**Expected Files** (with timestamps):
- `bar_chart_category_YYYYMMDD_HHMMSS.png`
- `pie_chart_category_YYYYMMDD_HHMMSS.png`
- `line_chart_monthly_YYYYMMDD_HHMMSS.png`

#### D. Check Log Files

```bash
ls -l logs/
cat logs/expense_analysis.log
```

**Expected**: Log file containing INFO-level execution details.

### 6. Run Unit Tests

```bash
pytest
```

**Expected Output**:
```
================================ test session starts =================================
collected 18 items

tests/test_analysis.py ........                                             [ 44%]
tests/test_config.py ...                                                    [ 61%]
tests/test_reading.py ....                                                  [ 83%]
tests/test_validators.py ...                                                [100%]

================================ 18 passed in 2.34s ==================================
```

#### With Coverage Report

```bash
pytest --cov=. --cov-report=term
```

**Expected**: Coverage report showing >80% code coverage.

---

## Advanced Verification

### Test Custom Input File

1. Create a custom CSV file:

```csv
Date,Category,Amount,Description
2024-01-01,Food,50.00,Lunch
2024-01-02,Transport,30.00,Gas
2024-01-03,Entertainment,100.00,Concert
```

2. Save as `data/my_expenses.csv`

3. Run analysis:

```bash
python main.py --input data/my_expenses.csv --output output/custom/
```

### Test Configuration Modification

1. Copy default config:

```bash
cp config/config.json config/test.json
```

2. Modify logging level in `config/test.json`:

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

3. Run with custom config:

```bash
python main.py --config config/test.json --log-level DEBUG
```

**Expected**: More detailed DEBUG-level logs.

### Test CLI Options

```bash
# Show version
python main.py --version

# Interactive plot display
python main.py --show-plots

# Custom log level
python main.py --log-level WARNING
```

---

## Package Installation (Optional)

Test the project as an installable package:

```bash
# Install in development mode
pip install -e .

# Run using console script entry point
expense-analyzer --help
```

**Note**: The `expense-analyzer` command is defined in `pyproject.toml` and provides an alternative way to run the application.

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'pandas'`

**Solution**: Dependencies not installed. Run `pip install -r requirements.txt`

### Issue: `FileNotFoundError: config/config.json`

**Solution**: You're not in the project root directory. Run `cd expense_analyzer_final`

### Issue: Charts not generated

**Solution**: 
1. Check `output/` directory exists: `ls -la output/`
2. Check logs: `cat logs/expense_analysis.log`
3. Run with DEBUG logging: `python main.py --log-level DEBUG`

### Issue: Permission denied when creating files

**Solution**: Ensure write permissions:
```bash
chmod -R u+w output/ logs/
```

### Issue: Tests fail with import errors

**Solution**: Install test dependencies:
```bash
pip install pytest pytest-cov
```

---

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Linux, macOS, or Windows
- **RAM**: 512 MB minimum (2 GB recommended for large datasets)
- **Disk**: 50 MB for dependencies, 100 MB for large datasets

---

## Verification Checklist

- [ ] Project extracted successfully
- [ ] Virtual environment created and activated
- [ ] Dependencies installed without errors
- [ ] `python main.py --help` displays help text
- [ ] Default execution completes successfully
- [ ] Three chart files generated in `output/`
- [ ] Log file created in `logs/`
- [ ] All unit tests pass (`pytest`)
- [ ] Custom input file processed correctly
- [ ] Configuration file modification works
- [ ] All CLI options functional

---

## Next Steps

After successful verification:

1. **Explore the Code**: Review `modules/`, `utils/`, and `tests/` directories
2. **Read Documentation**: See `README.md` for comprehensive documentation
3. **Customize Configuration**: Modify `config/config.json` for your needs
4. **Process Your Data**: Replace `data/expenses_example.csv` with your own data
5. **Extend Functionality**: Add new modules or modify existing analysis logic

---

## Support

If you encounter issues not covered in this guide:

1. Check `README.md` for detailed documentation
2. Review `QUICKSTART.md` for quick reference
3. Examine `logs/expense_analysis.log` for error details
4. Run with `--log-level DEBUG` for verbose output
5. Review test files in `tests/` for usage examples

---

**Project Status**: ✅ Production-Ready  
**Last Updated**: February 2026  
**Python Version**: 3.8+
