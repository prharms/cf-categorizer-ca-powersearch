"""
Tests for the processing module.
"""

import unittest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import tempfile

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from processing.categorizer import ContributorCategorizer
from config.settings import AppConfig
from utils.validation import ValidationError


class TestContributorCategorizer(unittest.TestCase):
    """Test cases for the ContributorCategorizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = AppConfig()
        self.config.anthropic_api_key = "test-key"
        
        # Create temp directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_csv = os.path.join(self.temp_dir, "test.csv")
        
        # Create test CSV data
        self.test_data = pd.DataFrame({
            'Contributor Name': ['John Doe', 'Jane Smith', 'ACME Corp'],
            'Contributor Employer': ['Law Firm LLC', 'Tech Corp', 'N/A'],
            'Contributor Occupation': ['Attorney', 'Engineer', 'Business']
        })
        self.test_data.to_csv(self.test_csv, index=False)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('processing.categorizer.APIClient')
    def test_init(self, mock_api_client):
        """Test ContributorCategorizer initialization."""
        categorizer = ContributorCategorizer(self.config)
        
        self.assertEqual(categorizer.config, self.config)
        mock_api_client.assert_called_once_with(self.config)
    
    @patch('processing.categorizer.APIClient')
    def test_process_csv_file_success(self, mock_api_client):
        """Test successful CSV file processing."""
        # Mock API client
        mock_client = Mock()
        mock_client.categorize_contributor.return_value = "Lawyers"
        mock_api_client.return_value = mock_client
        
        categorizer = ContributorCategorizer(self.config)
        
        # Mock internal methods
        categorizer._save_progress = Mock()
        categorizer._load_progress = Mock(return_value={})
        categorizer._cleanup_progress = Mock()
        
        results = categorizer.process_csv_file(self.test_csv)
        
        self.assertIn('interim', results)
        self.assertIn('final', results)
        self.assertTrue(os.path.exists(results['interim']))
        self.assertTrue(os.path.exists(results['final']))
    
    @patch('processing.categorizer.APIClient')
    def test_process_csv_file_invalid_file(self, mock_api_client):
        """Test processing with invalid CSV file."""
        categorizer = ContributorCategorizer(self.config)
        
        with self.assertRaises(ValidationError):
            categorizer.process_csv_file("nonexistent.csv")
    
    @patch('processing.categorizer.APIClient')
    def test_standardize_single_category_exact_match(self, mock_api_client):
        """Test exact match standardization."""
        categorizer = ContributorCategorizer(self.config)
        
        result = categorizer._standardize_single_category("Lawyers")
        self.assertEqual(result, "Lawyers")
    
    @patch('processing.categorizer.APIClient')
    def test_standardize_single_category_fuzzy_match(self, mock_api_client):
        """Test fuzzy match standardization."""
        categorizer = ContributorCategorizer(self.config)
        
        result = categorizer._standardize_single_category("LAWYERS")
        self.assertEqual(result, "Lawyers")
    
    @patch('processing.categorizer.APIClient')
    def test_standardize_single_category_no_match(self, mock_api_client):
        """Test no match standardization."""
        categorizer = ContributorCategorizer(self.config)
        
        result = categorizer._standardize_single_category("Unknown Category")
        self.assertEqual(result, "Other")
    
    @patch('processing.categorizer.APIClient')
    def test_standardize_existing_csv(self, mock_api_client):
        """Test standardizing existing CSV file."""
        # Create CSV with categories
        categorized_data = self.test_data.copy()
        categorized_data['Contributor Category'] = ['Lawyers', 'Other', 'Business contributor (with no other information)']
        
        categorized_csv = os.path.join(self.temp_dir, "categorized.csv")
        categorized_data.to_csv(categorized_csv, index=False)
        
        categorizer = ContributorCategorizer(self.config)
        result = categorizer.standardize_existing_csv(categorized_csv)
        
        self.assertTrue(os.path.exists(result))
        
        # Verify the standardized data
        df = pd.read_csv(result)
        self.assertIn('Contributor Category', df.columns)
    
    @patch('processing.categorizer.APIClient')
    def test_clean_string(self, mock_api_client):
        """Test string cleaning functionality."""
        categorizer = ContributorCategorizer(self.config)
        
        # Test valid string
        result = categorizer._clean_string("  John Doe  ")
        self.assertEqual(result, "John Doe")
        
        # Test empty string
        result = categorizer._clean_string("")
        self.assertIsNone(result)
        
        # Test NaN
        result = categorizer._clean_string(pd.NA)
        self.assertIsNone(result)
    
    @patch('processing.categorizer.APIClient')
    def test_auto_generate_output_path(self, mock_api_client):
        """Test automatic output path generation."""
        categorizer = ContributorCategorizer(self.config)
        
        # Test categorized stage
        result = categorizer._auto_generate_output_path("/path/to/input.csv", "categorized")
        expected = os.path.join("data", "interim", "input_categorized.csv")
        self.assertEqual(result, expected)
        
        # Test standardized stage
        result = categorizer._auto_generate_output_path("/path/to/input.csv", "standardized")
        expected = os.path.join("data", "processed", "input_standardized.csv")
        self.assertEqual(result, expected)
        
        # Test invalid stage
        with self.assertRaises(ValueError):
            categorizer._auto_generate_output_path("/path/to/input.csv", "invalid")


if __name__ == '__main__':
    unittest.main(verbosity=2) 