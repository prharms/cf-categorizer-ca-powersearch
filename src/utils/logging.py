"""
Logging configuration for the categorization tool.
"""

import logging
import os
from typing import Optional

try:
    from ..config.settings import LoggingConfig
except ImportError:
    # For when running tests or as standalone module
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from config.settings import LoggingConfig


def setup_logging(config: LoggingConfig, logger_name: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        config: Logging configuration
        logger_name: Name for the logger (defaults to root logger)
    
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, config.level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.level.upper()))
    
    # Create file handler
    os.makedirs(os.path.dirname(config.file_path), exist_ok=True)
    file_handler = logging.FileHandler(config.file_path)
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(config.format)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger by name."""
    return logging.getLogger(name) 