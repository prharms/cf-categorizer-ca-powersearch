"""
Configuration management for the Campaign Finance Categorization Tool.
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class APIConfig:
    """Configuration for API settings."""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 100
    base_delay: float = 1.5  # Optimized for Claude 4 Sonnet rate limits (50 RPM)
    max_retries: int = 5
    timeout: int = 30


@dataclass
class ProcessingConfig:
    """Configuration for processing settings."""
    batch_size: int = 10
    progress_save_interval: int = 50
    fuzzy_match_threshold: int = 80


@dataclass
class LoggingConfig:
    """Configuration for logging settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/categorization.log"


@dataclass
class Categories:
    """Standard category definitions."""
    canonical_categories: List[str] = field(default_factory=lambda: [
        "Democratic Party Committees",
        "Other political action committees", 
        "State Legislative Candidates/Officeholders",
        "Local Government Candidates/Officeholders",
        "Labor Unions",
        "Environmental Groups",
        "Oil Industry",
        "Pharmaceutical Industry",
        "Real Estate Industry",
        "Indian Tribes",
        "Lobbyists and Political Consultants",
        "Lawyers",
        "Individual contributor (with no other information)",
        "Business contributor (with no other information)",
        "Other"
    ])
    
    prompt_template: str = """Please categorize this campaign contributor based on the available information.

Contributor Name: {name}
Employer: {employer}
Occupation: {occupation}

Example categories:
{categories}

Respond with only the most appropriate category from the list above. Base your decision on:
1. The contributor name (look for committee names, candidate names, organization names, unions)
2. The employer information (look for companies, government entities, law firms)
3. The occupation (look for specific professions like lawyers, consultants, etc.)

Apply these rules IN ORDER (more specific categories first):

If the contributor name appears to be a labor union (contains "Union", "Labor", "Workers", "Association" for employee groups, etc.) and has an ID number, choose "Labor Unions" - even if it also contains "PAC" or "Committee".
Note: "DRIVE Committee" is specifically a labor union committee (part of the Teamsters Union) and should be categorized as "Labor Unions".
Groups of employees referred to as "Administrators" or "Managers" should not be categorized as labor unions.
If the contributor name appears to be a tribal entity, choose "Indian Tribes".
If the contributor name or occupation appears to be a lobbyist or political consultant, choose "Lobbyists and Political Consultants".
If the contributor name or occupation appears to be a lawyer or legal firm, choose "Lawyers".
If the contributor name appears to be from the oil industry, choose "Oil Industry".
If the contributor name appears to be from the pharmaceutical industry, choose "Pharmaceutical Industry".
If the contributor name appears to be from the real estate industry, choose "Real Estate Industry". This includes but is not limited to construction companies, real estate developers, landlords, architects, engineering firms, and any entity with "YIMBY" in the name.
If the contributor name appears to be from environmental groups, choose "Environmental Groups".
If the contributor name appears to be a political committee or candidate committee and has an ID number, choose "Democratic Party Committees" or "Other political action committees" or "State Legislative Candidates/Officeholders" or "Local Government Candidates/Officeholders" as appropriate.
If the contributor name appears to be a business entity, choose "Business contributor with no other information".
If the contributor name appears to be an individual, labelled by first and last name, choose "Individual contributor with no other information". 
Otherwise, choose "Other"

Do not explain your reasoning. Do not include any other text in your response. 

No text that you provide for the category should be longer than 50 characters.

Category:"""


@dataclass
class AppConfig:
    """Main application configuration."""
    api: APIConfig = field(default_factory=APIConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    categories: Categories = field(default_factory=Categories)
    
    # Environment variables
    anthropic_api_key: str = ""
    
    def __post_init__(self):
        """Load environment variables after initialization."""
        load_dotenv()
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        
        # Override with environment variables if present
        if os.getenv('API_MODEL'):
            self.api.model = os.getenv('API_MODEL')
        if os.getenv('LOG_LEVEL'):
            self.logging.level = os.getenv('LOG_LEVEL')
    
    def validate(self) -> None:
        """Validate configuration."""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        if self.processing.batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        
        if not (0 <= self.processing.fuzzy_match_threshold <= 100):
            raise ValueError("fuzzy_match_threshold must be between 0 and 100")


def load_config() -> AppConfig:
    """Load and validate application configuration."""
    config = AppConfig()
    config.validate()
    return config 