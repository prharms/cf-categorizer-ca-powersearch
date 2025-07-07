"""
API client for the Anthropic Claude service.
"""

import time
import random
import logging
from typing import Optional
import anthropic

try:
    from ..config.settings import AppConfig
except ImportError:
    # For when running tests or as standalone module
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from config.settings import AppConfig


logger = logging.getLogger(__name__)


class APIClient:
    """Client for interacting with the Anthropic Claude API."""
    
    def __init__(self, config: AppConfig):
        """Initialize the API client."""
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.rate_limiter = RateLimiter(config.api)
    
    def categorize_contributor(self, name: str, employer: Optional[str], occupation: Optional[str]) -> str:
        """
        Categorize a contributor using Claude API.
        
        Args:
            name: Contributor name
            employer: Contributor employer (can be None)
            occupation: Contributor occupation (can be None)
        
        Returns:
            Category string
        """
        prompt = self.config.categories.prompt_template.format(
            name=name,
            employer=employer if employer else 'Not provided',
            occupation=occupation if occupation else 'Not provided',
            categories='\n'.join(f"- {cat}" for cat in self.config.categories.canonical_categories)
        )
        
        for attempt in range(self.config.api.max_retries + 1):
            try:
                # Apply rate limiting
                self.rate_limiter.wait_if_needed(attempt)
                
                response = self.client.messages.create(
                    model=self.config.api.model,
                    max_tokens=self.config.api.max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Extract the category from the response
                category = response.content[0].text.strip()
                
                # Clean up the response to get just the category
                if "Category:" in category:
                    category = category.split("Category:")[-1].strip()
                
                logger.debug(f"Categorized {name} as: {category}")
                return category
                
            except Exception as e:
                error_str = str(e)
                if "529" in error_str or "rate" in error_str.lower() or "limit" in error_str.lower():
                    # Rate limit error - can retry
                    if attempt < self.config.api.max_retries:
                        logger.warning(f"Rate limit hit for {name}, retrying... (attempt {attempt + 1})")
                        continue
                    else:
                        logger.error(f"Rate limit exceeded for {name} after {self.config.api.max_retries} retries")
                        return "Other"
                else:
                    # Other error - log and return Other
                    logger.error(f"Error categorizing contributor {name}: {error_str}")
                    return "Other"
        
        # If we get here, all retries failed
        logger.error(f"Failed to categorize {name} after {self.config.api.max_retries} retries")
        return "Other"


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, api_config):
        """Initialize the rate limiter."""
        self.api_config = api_config
        self.last_request_time = 0
    
    def wait_if_needed(self, attempt: int = 0) -> None:
        """Wait if needed to respect rate limits."""
        current_time = time.time()
        
        if attempt > 0:
            # Exponential backoff for retries
            wait_time = self.api_config.base_delay * (2 ** attempt) + random.uniform(0, 1)
            logger.info(f"Retrying in {wait_time:.1f} seconds (attempt {attempt + 1})")
            time.sleep(wait_time)
        else:
            # Normal rate limiting
            time_since_last = current_time - self.last_request_time
            min_delay = self.api_config.base_delay + random.uniform(0, 0.2)
            
            if time_since_last < min_delay:
                sleep_time = min_delay - time_since_last
                time.sleep(sleep_time)
        
        self.last_request_time = time.time() 