"""
Test analysis module.

This module contains unit tests for expense analysis functionality.
"""

import pytest
import pandas as pd
from datetime import datetime
from modules.analysis import (
    calculate_total_spent,
    calculate_monthly_average,
    find_max_min_expenses,
    calculate_expenses_by_category,
    generate_complete_summary
)


@pytest.fixture
def sample_expenses_df():
    """Create a sample DataFrame for testing."""
    data = {
        'Date': pd.to_datetime([
            '2024-01-15', '2024-01-18', '2024-01-20',
            '2024-02-01', '2024-02-05', '2024-02-10'
        ]),
        'Category': ['Food', 'Transport', 'Entertainment', 'Services', 'Transport', 'Food'],
        'Amount': [250.50, 45.00, 120.00, 850.00, 50.00, 320.00],
        'Description': ['Groceries', 'Gas', 'Movies', 'Rent', 'Uber', 'Restaurant']
    }
    return pd.DataFrame(data)


class TestCalculateTotalSpent:
    """Test suite for calculate_total_spent function."""
    
    def test_total_spent(self, sample_expenses_df):
        """Test calculation of total spent."""
        total = calculate_total_spent(sample_expenses_df)
        expected = 1635.50
        assert total == expected
    
    def test_empty_dataframe(self):
        """Test that empty DataFrame raises error."""
        from utils.validators import DataValidationError
        
        df = pd.DataFrame()
        with pytest.raises(DataValidationError):
            calculate_total_spent(df)
    
    def test_missing_amount_column(self):
        """Test that missing Amount column raises error."""
        from utils.validators import DataValidationError
        
        df = pd.DataFrame({'Date': ['2024-01-15'], 'Category': ['Food']})
        with pytest.raises(DataValidationError):
            calculate_total_spent(df)


class TestCalculateMonthlyAverage:
    """Test suite for calculate_monthly_average function."""
    
    def test_monthly_average_structure(self, sample_expenses_df):
        """Test structure of monthly average result."""
        result = calculate_monthly_average(sample_expenses_df)
        
        assert 'average_total' in result
        assert 'monthly_expenses' in result
        assert isinstance(result['monthly_expenses'], pd.DataFrame)
    
    def test_monthly_average_calculation(self, sample_expenses_df):
        """Test monthly average calculation."""
        result = calculate_monthly_average(sample_expenses_df)
        
        # Should have 2 months
        assert len(result['monthly_expenses']) == 2
        
        # Check average calculation
        expected_avg = (415.50 + 1220.00) / 2
        assert result['average_total'] == round(expected_avg, 2)
    
    def test_monthly_breakdown(self, sample_expenses_df):
        """Test monthly breakdown values."""
        result = calculate_monthly_average(sample_expenses_df)
        monthly_df = result['monthly_expenses']
        
        # January total
        jan_total = monthly_df[monthly_df['Month'] == '2024-01']['Total'].values[0]
        assert jan_total == 415.50
        
        # February total
        feb_total = monthly_df[monthly_df['Month'] == '2024-02']['Total'].values[0]
        assert feb_total == 1220.00


class TestFindMaxMinExpenses:
    """Test suite for find_max_min_expenses function."""
    
    def test_max_min_structure(self, sample_expenses_df):
        """Test structure of max/min result."""
        result = find_max_min_expenses(sample_expenses_df)
        
        assert 'maximum' in result
        assert 'minimum' in result
        assert 'amount' in result['maximum']
        assert 'date' in result['maximum']
        assert 'category' in result['maximum']
    
    def test_max_expense(self, sample_expenses_df):
        """Test maximum expense identification."""
        result = find_max_min_expenses(sample_expenses_df)
        
        assert result['maximum']['amount'] == 850.00
        assert result['maximum']['category'] == 'Services'
    
    def test_min_expense(self, sample_expenses_df):
        """Test minimum expense identification."""
        result = find_max_min_expenses(sample_expenses_df)
        
        assert result['minimum']['amount'] == 45.00
        assert result['minimum']['category'] == 'Transport'


class TestCalculateExpensesByCategory:
    """Test suite for calculate_expenses_by_category function."""
    
    def test_category_aggregation(self, sample_expenses_df):
        """Test category aggregation."""
        result = calculate_expenses_by_category(sample_expenses_df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4  # 4 unique categories
        assert list(result.columns) == ['Category', 'Total', 'Count', 'Percentage']
    
    def test_category_totals(self, sample_expenses_df):
        """Test category total calculations."""
        result = calculate_expenses_by_category(sample_expenses_df)
        
        # Food total
        food_row = result[result['Category'] == 'Food']
        assert food_row['Total'].values[0] == 570.50
        assert food_row['Count'].values[0] == 2
    
    def test_sorting(self, sample_expenses_df):
        """Test that categories are sorted by total (descending)."""
        result = calculate_expenses_by_category(sample_expenses_df)
        
        # First category should have highest total
        assert result.iloc[0]['Category'] == 'Services'
        assert result.iloc[0]['Total'] == 850.00
    
    def test_percentage_calculation(self, sample_expenses_df):
        """Test percentage calculations."""
        result = calculate_expenses_by_category(sample_expenses_df)
        
        # Sum of percentages should be 100
        total_percentage = result['Percentage'].sum()
        assert round(total_percentage, 0) == 100


class TestGenerateCompleteSummary:
    """Test suite for generate_complete_summary function."""
    
    def test_summary_structure(self, sample_expenses_df):
        """Test complete summary structure."""
        summary = generate_complete_summary(sample_expenses_df)
        
        assert 'total_spent' in summary
        assert 'monthly_average' in summary
        assert 'max_min' in summary
        assert 'by_category' in summary
        assert 'num_transactions' in summary
        assert 'period' in summary
    
    def test_summary_integration(self, sample_expenses_df):
        """Test that summary integrates all components."""
        summary = generate_complete_summary(sample_expenses_df)
        
        assert summary['num_transactions'] == 6
        assert summary['total_spent'] == 1635.50
        assert 'average_total' in summary['monthly_average']
        assert 'maximum' in summary['max_min']
        assert isinstance(summary['by_category'], pd.DataFrame)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
