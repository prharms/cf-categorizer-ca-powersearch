"""
Command-line interface for the Campaign Finance Categorization Tool.
"""

import argparse
import sys
import os
from typing import Optional

try:
    from ..config.settings import load_config
    from ..processing.categorizer import ContributorCategorizer
    from ..utils.logging import setup_logging
    from ..utils.validation import ValidationError
except ImportError:
    # For when running tests or as standalone module
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from config.settings import load_config
    from processing.categorizer import ContributorCategorizer
    from utils.logging import setup_logging
    from utils.validation import ValidationError


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='Categorize campaign finance contributors using AI and fuzzy matching with two-stage pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default file (creates both interim/ and processed/ files)
  python run_categorization.py
  
  # Process custom file (two-stage pipeline)
  python run_categorization.py data/raw/my_campaign_data.csv
  
  # Standardize existing categories only
  python run_categorization.py --standardize
  
  # Custom final output location
  python run_categorization.py my_data.csv --output my_results.csv
        """
    )
    
    parser.add_argument(
        'input_file', 
        nargs='?',
        help='Input CSV file path'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Final output file path (default: auto-generated based on input filename)'
    )
    
    parser.add_argument(
        '--standardize', 
        action='store_true',
        help='Standardize existing categories instead of full processing'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--log-file',
        help='Path to log file (default: logs/categorization.log)'
    )
    
    return parser


def find_default_input_file() -> Optional[str]:
    """Find the default input file from the data/raw directory."""
    raw_dir = "data/raw"
    
    if not os.path.exists(raw_dir):
        return None
    
    # Look for CSV files in raw directory
    csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    
    if not csv_files:
        return None
    
    # Return the first CSV file found
    return os.path.join(raw_dir, csv_files[0])


def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config()
        
        # Override config with command line arguments
        if args.verbose:
            config.logging.level = "DEBUG"
        
        if args.log_file:
            config.logging.file_path = args.log_file
        
        # Set up logging
        logger = setup_logging(config.logging, __name__)
        
        # Determine input file
        input_file = args.input_file
        if not input_file:
            input_file = find_default_input_file()
            if not input_file:
                logger.error("No input file specified and no CSV files found in data/raw/")
                return 1
        
        # Initialize categorizer
        categorizer = ContributorCategorizer(config)
        
        if args.standardize:
            # Standardization mode
            logger.info("Running in standardization mode")
            
            # For standardization, look for interim file if no specific file provided
            if not args.input_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                input_file = os.path.join("data", "interim", f"{base_name}_categorized.csv")
            
            result = categorizer.standardize_existing_csv(input_file, args.output)
            
            logger.info(f"Standardization complete! Results saved to: {result}")
            
        else:
            # Normal categorization process
            logger.info("Running full categorization pipeline")
            
            results = categorizer.process_csv_file(input_file, args.output)
            
            logger.info("Processing complete! Two-stage pipeline:")
            logger.info(f"   📁 Interim (raw AI): {results['interim']}")
            logger.info(f"   📁 Processed (standardized): {results['final']}")
        
        return 0
        
    except ValidationError as e:
        print(f"Validation error: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 