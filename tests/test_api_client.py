"""
Tests for the API client module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.client import APIClient, RateLimiter
from config.settings import AppConfig, APIConfig


class TestAPIClient(unittest.TestCase):
    """Test cases for the APIClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = AppConfig()
        self.config.anthropic_api_key = "test-key"
        
    @patch('api.client.anthropic.Anthropic')
    def test_init(self, mock_anthropic):
        """Test APIClient initialization."""
        client = APIClient(self.config)
        
        self.assertEqual(client.config, self.config)
        mock_anthropic.assert_called_once_with(api_key="test-key")
        self.assertIsInstance(client.rate_limiter, RateLimiter)
    
    @patch('api.client.anthropic.Anthropic')
    def test_categorize_contributor_success(self, mock_anthropic):
        """Test successful categorization."""
        # Mock API response
        mock_response = Mock()
        mock_response.content = [Mock(text="Lawyers")]
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        client = APIClient(self.config)
        
        # Mock rate limiter
        client.rate_limiter = Mock()
        
        result = client.categorize_contributor("John Doe", "Law Firm LLC", "Attorney")
        
        self.assertEqual(result, "Lawyers")
        mock_client.messages.create.assert_called_once()
        client.rate_limiter.wait_if_needed.assert_called_once()
    
    @patch('api.client.anthropic.Anthropic')
    def test_categorize_contributor_rate_limit_error(self, mock_anthropic):
        """Test handling of rate limit errors."""
        # Mock API to raise rate limit error
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("Rate limit exceeded")
        mock_anthropic.return_value = mock_client
        
        client = APIClient(self.config)
        client.rate_limiter = Mock()
        
        result = client.categorize_contributor("John Doe", "Law Firm LLC", "Attorney")
        
        self.assertEqual(result, "Other")
    
    @patch('api.client.anthropic.Anthropic')
    def test_categorize_contributor_other_error(self, mock_anthropic):
        """Test handling of other errors."""
        # Mock API to raise other error
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API error")
        mock_anthropic.return_value = mock_client
        
        client = APIClient(self.config)
        client.rate_limiter = Mock()
        
        result = client.categorize_contributor("John Doe", "Law Firm LLC", "Attorney")
        
        self.assertEqual(result, "Other")
    
    @patch('api.client.anthropic.Anthropic')
    def test_categorize_contributor_category_cleaning(self, mock_anthropic):
        """Test category response cleaning."""
        # Mock API response with "Category:" prefix
        mock_response = Mock()
        mock_response.content = [Mock(text="Category: Lawyers")]
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        client = APIClient(self.config)
        client.rate_limiter = Mock()
        
        result = client.categorize_contributor("John Doe", "Law Firm LLC", "Attorney")
        
        self.assertEqual(result, "Lawyers")


class TestRateLimiter(unittest.TestCase):
    """Test cases for the RateLimiter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_config = APIConfig()
        self.rate_limiter = RateLimiter(self.api_config)
    
    @patch('api.client.time.sleep')
    @patch('api.client.time.time')
    def test_wait_if_needed_no_wait(self, mock_time, mock_sleep):
        """Test when wait is needed due to rate limiting."""
        mock_time.return_value = 1000.0
        self.rate_limiter.last_request_time = 999.9  # Very recent request
        
        self.rate_limiter.wait_if_needed()
        
        # Sleep should be called due to rate limiting
        mock_sleep.assert_called_once()
    
    @patch('api.client.time.sleep')
    @patch('api.client.time.time')
    def test_wait_if_needed_retry(self, mock_time, mock_sleep):
        """Test exponential backoff for retries."""
        mock_time.return_value = 1000.0
        
        self.rate_limiter.wait_if_needed(attempt=1)
        
        mock_sleep.assert_called_once()
        # Should use exponential backoff
        args = mock_sleep.call_args[0]
        self.assertGreater(args[0], self.api_config.base_delay)


if __name__ == '__main__':
    unittest.main(verbosity=2) 