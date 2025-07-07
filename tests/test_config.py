"""
Tests for the configuration module.
"""

import unittest
import os
from unittest.mock import patch
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.settings import AppConfig, APIConfig, ProcessingConfig, LoggingConfig, Categories, load_config


class TestAppConfig(unittest.TestCase):
    """Test cases for the AppConfig class."""

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        config = AppConfig()
        
        self.assertEqual(config.anthropic_api_key, 'test-key')
        self.assertIsInstance(config.api, APIConfig)
        self.assertIsInstance(config.processing, ProcessingConfig)
        self.assertIsInstance(config.logging, LoggingConfig)
        self.assertIsInstance(config.categories, Categories)
    
    @patch.dict(os.environ, {
        'ANTHROPIC_API_KEY': 'test-key',
        'API_MODEL': 'claude-3-opus-20240229',
        'LOG_LEVEL': 'DEBUG'
    })
    def test_init_with_env_overrides(self):
        """Test initialization with environment variable overrides."""
        config = AppConfig()
        
        self.assertEqual(config.anthropic_api_key, 'test-key')
        self.assertEqual(config.api.model, 'claude-3-opus-20240229')
        self.assertEqual(config.logging.level, 'DEBUG')
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_validate_success(self):
        """Test successful validation."""
        config = AppConfig()
        
        # Should not raise exception
        config.validate()
    
    def test_validate_missing_api_key(self):
        """Test validation with missing API key."""
        config = AppConfig()
        config.anthropic_api_key = ""  # Set empty key directly
        
        with self.assertRaises(ValueError) as context:
            config.validate()
        
        self.assertIn("ANTHROPIC_API_KEY not found", str(context.exception))
    

    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_validate_invalid_batch_size(self):
        """Test validation with invalid batch_size."""
        config = AppConfig()
        config.processing.batch_size = 0
        
        with self.assertRaises(ValueError) as context:
            config.validate()
        
        self.assertIn("batch_size must be at least 1", str(context.exception))
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_validate_invalid_fuzzy_threshold(self):
        """Test validation with invalid fuzzy_match_threshold."""
        config = AppConfig()
        config.processing.fuzzy_match_threshold = 150
        
        with self.assertRaises(ValueError) as context:
            config.validate()
        
        self.assertIn("fuzzy_match_threshold must be between 0 and 100", str(context.exception))


class TestAPIConfig(unittest.TestCase):
    """Test cases for the APIConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = APIConfig()
        
        self.assertEqual(config.model, "claude-sonnet-4-20250514")
        self.assertEqual(config.max_tokens, 100)
        self.assertEqual(config.base_delay, 1.5)
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.timeout, 30)


class TestProcessingConfig(unittest.TestCase):
    """Test cases for the ProcessingConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ProcessingConfig()
        
        self.assertEqual(config.batch_size, 10)
        self.assertEqual(config.progress_save_interval, 50)
        self.assertEqual(config.fuzzy_match_threshold, 80)


class TestLoggingConfig(unittest.TestCase):
    """Test cases for the LoggingConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = LoggingConfig()
        
        self.assertEqual(config.level, "INFO")
        self.assertEqual(config.file_path, "logs/categorization.log")
        self.assertIn("%(asctime)s", config.format)


class TestCategories(unittest.TestCase):
    """Test cases for the Categories class."""

    def test_canonical_categories(self):
        """Test canonical categories list."""
        categories = Categories()
        
        self.assertIsInstance(categories.canonical_categories, list)
        self.assertGreater(len(categories.canonical_categories), 0)
        self.assertIn("Lawyers", categories.canonical_categories)
        self.assertIn("Other", categories.canonical_categories)
    
    def test_prompt_template(self):
        """Test prompt template format."""
        categories = Categories()
        
        self.assertIn("{name}", categories.prompt_template)
        self.assertIn("{employer}", categories.prompt_template)
        self.assertIn("{occupation}", categories.prompt_template)
        self.assertIn("{categories}", categories.prompt_template)


class TestLoadConfig(unittest.TestCase):
    """Test cases for the load_config function."""

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_load_config_success(self):
        """Test successful configuration loading."""
        config = load_config()
        
        self.assertIsInstance(config, AppConfig)
        self.assertEqual(config.anthropic_api_key, 'test-key')
    
    def test_load_config_missing_key(self):
        """Test configuration loading with missing API key."""
        # Remove any existing API key and ensure dotenv doesn't load it
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''}, clear=False):
            with patch('config.settings.load_dotenv'):  # Mock dotenv to not load from file
                with self.assertRaises(ValueError):
                    load_config()


if __name__ == '__main__':
    unittest.main(verbosity=2) 