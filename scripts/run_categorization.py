#!/usr/bin/env python3
"""
Main entry point for the campaign finance contributor categorization tool.

This script provides a flexible CLI interface for categorizing campaign finance
contributors using AI and fuzzy matching standardization.

Examples:
    # Use default file
    python run_categorization.py
    
    # Process custom file
    python run_categorization.py data/raw/my_campaign_data.csv
    
    # Standardize existing categories
    python run_categorization.py --standardize
    
    # Custom input and output paths
    python run_categorization.py my_data.csv --output my_results.csv
    
    # Use more parallel workers
    python run_categorization.py --workers 8
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cli.main import main

if __name__ == "__main__":
    exit(main()) 