#!/usr/bin/env python3
"""
Test script to process first 50 rows of data to verify categorization fix.
"""

import os
import sys
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.settings import load_config
from processing.categorizer import ContributorCategorizer
from utils.logging import setup_logging


def test_first_50_rows():
    """Test categorization on first 50 rows."""
    
    # Load configuration
    config = load_config()
    
    # Set up logging (verbose mode)
    config.logging.level = "DEBUG"
    logger = setup_logging(config.logging, __name__)
    
    # Read original data
    input_file = "data/raw/data-2025-07-02-19-01.csv"
    logger.info(f"Reading first 50 rows from {input_file}")
    
    df = pd.read_csv(input_file)
    df_test = df.head(50).copy()
    
    # Create test file
    test_file = "data/raw/test_first_50.csv"
    df_test.to_csv(test_file, index=False)
    
    logger.info(f"Created test file with {len(df_test)} rows")
    
    # Initialize categorizer
    categorizer = ContributorCategorizer(config)
    
    # Process the test file
    logger.info("Starting categorization of first 50 rows...")
    results = categorizer.process_csv_file(test_file)
    
    logger.info("Categorization complete!")
    logger.info(f"Results saved to:")
    logger.info(f"  Interim: {results['interim']}")
    logger.info(f"  Final: {results['final']}")
    
    # Show some sample results
    df_result = pd.read_csv(results['final'])
    
    print("\n" + "="*80)
    print("SAMPLE RESULTS FROM FIRST 50 ROWS:")
    print("="*80)
    
    # Show first 10 results with key contributors
    sample_results = df_result[['Contributor Name', 'Contributor Category']].head(10)
    
    for idx, row in sample_results.iterrows():
        print(f"{idx+1:2d}. {row['Contributor Name']:<40} -> {row['Contributor Category']}")
    
    # Check for specific test cases that were failing
    test_cases = [
        'Tim Grayson for Assembly 2024',
        'DRIVE Committee', 
        'American Federation of State, County & Municipal Employees'
    ]
    
    print("\n" + "="*80)
    print("CHECKING SPECIFIC TEST CASES:")
    print("="*80)
    
    for test_case in test_cases:
        matches = df_result[df_result['Contributor Name'].str.contains(test_case, na=False)]
        if not matches.empty:
            for idx, row in matches.iterrows():
                print(f"✓ {row['Contributor Name']:<50} -> {row['Contributor Category']}")
        else:
            print(f"✗ '{test_case}' not found in first 50 rows")
    
    print("\n" + "="*80)
    print("CATEGORY DISTRIBUTION:")
    print("="*80)
    
    category_counts = df_result['Contributor Category'].value_counts()
    for category, count in category_counts.items():
        print(f"{category:<50} : {count:2d}")
    
    # Cleanup test file
    try:
        os.remove(test_file)
    except FileNotFoundError:
        pass  # File was already removed or doesn't exist
    
    print(f"\nTest completed successfully! Check the files:")
    print(f"  {results['interim']}")
    print(f"  {results['final']}")


if __name__ == "__main__":
    test_first_50_rows() 