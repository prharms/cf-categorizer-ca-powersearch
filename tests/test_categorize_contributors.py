"""
Tests for the campaign finance contributor categorization tool.
Legacy test file - updated to work with new modular architecture.
"""

import unittest
import pandas as pd
from unittest.mock import Mock, patch
import os
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.settings import load_config
from utils.validation import ValidationError


class TestLegacyCompatibility(unittest.TestCase):
    """Test cases for legacy compatibility."""

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_config_loading(self):
        """Test that configuration can be loaded successfully."""
        config = load_config()
        
        self.assertIsNotNone(config)
        self.assertEqual(config.anthropic_api_key, 'test-key')

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_canonical_categories_exist(self):
        """Test that canonical categories list is properly defined."""
        config = load_config()
        canonical_categories = config.categories.canonical_categories
        
        self.assertIsInstance(canonical_categories, list)
        self.assertGreater(len(canonical_categories), 0)
        self.assertIn("Individual contributor (with no other information)", canonical_categories)
        self.assertIn("Lawyers", canonical_categories)
        self.assertIn("Other", canonical_categories)


class TestOutputPathGeneration(unittest.TestCase):
    """Test cases for auto-generated output paths."""

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_auto_generate_categorized_path(self):
        """Test auto-generation of categorized output paths."""
        from processing.categorizer import ContributorCategorizer
        
        config = load_config()
        categorizer = ContributorCategorizer(config)
        
        input_path = "data/raw/test_file.csv"
        result = categorizer._auto_generate_output_path(input_path, 'categorized')
        expected = os.path.join("data", "interim", "test_file_categorized.csv")
        self.assertEqual(result, expected)

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_auto_generate_standardized_path(self):
        """Test auto-generation of standardized output paths."""
        from processing.categorizer import ContributorCategorizer
        
        config = load_config()
        categorizer = ContributorCategorizer(config)
        
        input_path = "data/interim/test_file_categorized.csv"
        result = categorizer._auto_generate_output_path(input_path, 'standardized')
        expected = os.path.join("data", "processed", "test_file_categorized_standardized.csv")
        self.assertEqual(result, expected)

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_auto_generate_path_with_different_extension(self):
        """Test path generation with non-csv files."""
        from processing.categorizer import ContributorCategorizer
        
        config = load_config()
        categorizer = ContributorCategorizer(config)
        
        input_path = "some/path/data.xlsx"
        result = categorizer._auto_generate_output_path(input_path, 'categorized')
        expected = os.path.join("data", "interim", "data_categorized.csv")
        self.assertEqual(result, expected)

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_auto_generate_path_invalid_stage(self):
        """Test that invalid stage raises error."""
        from processing.categorizer import ContributorCategorizer
        
        config = load_config()
        categorizer = ContributorCategorizer(config)
        
        with self.assertRaises(ValueError):
            categorizer._auto_generate_output_path("test.csv", "invalid_stage")

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_auto_generate_path_complex_filename(self):
        """Test path generation with complex filenames."""
        from processing.categorizer import ContributorCategorizer
        
        config = load_config()
        categorizer = ContributorCategorizer(config)
        
        input_path = "data/raw/campaign_finance_2025-01-01_final.csv"
        result = categorizer._auto_generate_output_path(input_path, 'categorized')
        expected = os.path.join("data", "interim", "campaign_finance_2025-01-01_final_categorized.csv")
        self.assertEqual(result, expected)


class TestDataStructure(unittest.TestCase):
    """Test cases for data file structure and paths."""

    def test_data_directory_structure(self):
        """Test that the proper data directory structure exists."""
        base_path = os.path.join(os.path.dirname(__file__), '..')
        
        # Check main directories exist
        self.assertTrue(os.path.exists(os.path.join(base_path, 'data')))
        self.assertTrue(os.path.exists(os.path.join(base_path, 'data', 'raw')))
        self.assertTrue(os.path.exists(os.path.join(base_path, 'data', 'interim')))
        self.assertTrue(os.path.exists(os.path.join(base_path, 'data', 'processed')))

    def test_source_directory_structure(self):
        """Test that the source directory structure exists."""
        base_path = os.path.join(os.path.dirname(__file__), '..')
        
        # Check src directory and files exist
        self.assertTrue(os.path.exists(os.path.join(base_path, 'src')))
        self.assertTrue(os.path.exists(os.path.join(base_path, 'src', '__init__.py')))
        
        # Check new modular structure
        self.assertTrue(os.path.exists(os.path.join(base_path, 'src', 'config')))
        self.assertTrue(os.path.exists(os.path.join(base_path, 'src', 'api')))
        self.assertTrue(os.path.exists(os.path.join(base_path, 'src', 'processing')))
        self.assertTrue(os.path.exists(os.path.join(base_path, 'src', 'utils')))
        self.assertTrue(os.path.exists(os.path.join(base_path, 'src', 'cli')))


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2) 