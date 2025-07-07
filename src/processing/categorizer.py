"""
Core categorization logic for campaign finance contributors.
"""

import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from fuzzywuzzy import fuzz, process
import os
import pickle
from datetime import datetime

try:
    from ..api.client import APIClient
    from ..config.settings import AppConfig
    from ..utils.validation import validate_csv_file, validate_required_columns
except ImportError:
    # For when running tests or as standalone module
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from api.client import APIClient
    from config.settings import AppConfig
    from utils.validation import validate_csv_file, validate_required_columns


logger = logging.getLogger(__name__)


class ContributorCategorizer:
    """Main categorizer for campaign finance contributors."""
    
    def __init__(self, config: AppConfig):
        """Initialize the categorizer."""
        self.config = config
        self.api_client = APIClient(config)
        self.progress_file = "data/interim/progress.pkl"
    
    def process_csv_file(self, input_file: str, output_file: Optional[str] = None) -> Dict[str, str]:
        """
        Process the CSV file with proper two-stage pipeline.
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to final output CSV file (optional, auto-generated if not provided)
        
        Returns:
            Dictionary with paths to created files
        """
        # Validate input file
        validate_csv_file(input_file)
        
        # Read and validate CSV
        logger.info(f"Reading CSV file: {input_file}")
        df = pd.read_csv(input_file)
        validate_required_columns(df)
        
        logger.info(f"Found {len(df)} rows to process")
        
        # Stage 1: AI categorization
        interim_file = self._auto_generate_output_path(input_file, 'categorized')
        df_categorized = self._categorize_with_ai(df, interim_file)
        
        # Stage 2: Fuzzy matching standardization
        if output_file is None:
            output_file = self._auto_generate_output_path(input_file, 'standardized')
        
        df_final = self._standardize_categories(df_categorized, output_file)
        
        return {
            'interim': interim_file,
            'final': output_file
        }
    
    def _categorize_with_ai(self, df: pd.DataFrame, interim_file: str) -> pd.DataFrame:
        """Categorize contributors using AI with sequential processing."""
        logger.info("Starting AI categorization with sequential processing")
        
        # Check for existing progress
        processed_indices = self._load_progress()
        start_index = len(processed_indices)
        
        if start_index > 0:
            logger.info(f"Resuming from row {start_index + 1}")
        
        # Prepare data for processing
        contributors = []
        for index, row in df.iterrows():
            if index in processed_indices:
                continue
            
            contributors.append({
                'index': index,
                'name': self._clean_string(row.get('Contributor Name', '')),
                'employer': self._clean_string(row.get('Contributor Employer', '')),
                'occupation': self._clean_string(row.get('Contributor Occupation', ''))
            })
        
        # Process in parallel
        categories = [''] * len(df)
        
        # Load existing categories from progress
        for idx in processed_indices:
            categories[idx] = processed_indices[idx]
        
        if contributors:
            new_categories = self._process_contributors_sequential(contributors)
            
            # Update categories list
            for contributor, category in zip(contributors, new_categories):
                categories[contributor['index']] = category
        
        # Add categories to dataframe
        df['Contributor Category'] = categories
        
        # Save interim file
        logger.info(f"Saving interim results to: {interim_file}")
        df.to_csv(interim_file, index=False)
        
        # Clean up progress file
        self._cleanup_progress()
        
        # Print statistics
        self._print_category_statistics(categories, "Raw AI categorization")
        
        return df
    
    def _process_contributors_sequential(self, contributors: List[Dict[str, Any]]) -> List[str]:
        """Process contributors sequentially."""
        categories = []
        total = len(contributors)
        
        for i, contrib in enumerate(contributors):
            try:
                # Categorize the contributor
                category = self.api_client.categorize_contributor(
                    contrib['name'],
                    contrib['employer'],
                    contrib['occupation']
                )
                categories.append(category)
                
                # Save progress periodically
                if (i + 1) % self.config.processing.progress_save_interval == 0:
                    self._save_progress(contrib['index'], category)
                    logger.info(f"Completed {i + 1}/{total} contributors")
                
            except Exception as e:
                logger.error(f"Error processing contributor {contrib['name']}: {str(e)}")
                categories.append("Other")
        
        return categories
    
    def _standardize_categories(self, df: pd.DataFrame, output_file: str) -> pd.DataFrame:
        """Standardize categories using fuzzy matching."""
        logger.info("Applying fuzzy matching standardization")
        
        raw_categories = df['Contributor Category'].tolist()
        standardized_categories = [
            self._standardize_single_category(cat) for cat in raw_categories
        ]
        
        df['Contributor Category'] = standardized_categories
        
        # Save final file
        logger.info(f"Saving final results to: {output_file}")
        df.to_csv(output_file, index=False)
        
        # Print statistics
        self._print_category_statistics(standardized_categories, "Standardized category")
        
        return df
    
    def _standardize_single_category(self, category: str) -> str:
        """Standardize a single category using fuzzy matching."""
        if not category or category.strip() == "":
            return "Other"
        
        category = category.strip()
        
        # Try exact match first
        if category in self.config.categories.canonical_categories:
            return category
        
        # Use fuzzy matching
        best_match = process.extractOne(
            category,
            self.config.categories.canonical_categories,
            scorer=fuzz.ratio
        )
        
        if best_match and best_match[1] >= self.config.processing.fuzzy_match_threshold:
            return best_match[0]
        else:
            logger.warning(f"Could not standardize category '{category}', using 'Other'")
            return "Other"
    
    def _clean_string(self, value: Any) -> Optional[str]:
        """Clean and validate string values."""
        if pd.isna(value) or value == '':
            return None
        return str(value).strip()
    
    def _auto_generate_output_path(self, input_path: str, stage: str) -> str:
        """Auto-generate output file path based on input file and processing stage."""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        if stage == 'categorized':
            output_dir = os.path.join("data", "interim")
            suffix = "_categorized"
        elif stage == 'standardized':
            output_dir = os.path.join("data", "processed")
            suffix = "_standardized"
        else:
            raise ValueError(f"Unknown stage: {stage}")
        
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"{base_name}{suffix}.csv"
        return os.path.join(output_dir, output_filename)
    
    def _save_progress(self, index: int, category: str) -> None:
        """Save processing progress."""
        try:
            progress = self._load_progress()
            progress[index] = category
            
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            with open(self.progress_file, 'wb') as f:
                pickle.dump(progress, f)
        except Exception as e:
            logger.warning(f"Failed to save progress: {str(e)}")
    
    def _load_progress(self) -> Dict[int, str]:
        """Load processing progress."""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            logger.warning(f"Failed to load progress: {str(e)}")
        
        return {}
    
    def _cleanup_progress(self) -> None:
        """Clean up progress file after successful completion."""
        try:
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
        except Exception as e:
            logger.warning(f"Failed to cleanup progress file: {str(e)}")
    
    def _print_category_statistics(self, categories: List[str], title: str) -> None:
        """Print category distribution statistics."""
        category_counts = pd.Series(categories).value_counts()
        logger.info(f"\n{title} distribution:")
        for category, count in category_counts.items():
            logger.info(f"  {category}: {count}")
    
    def standardize_existing_csv(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        Standardize category names in an existing CSV file using fuzzy matching.
        
        Args:
            input_file: Path to CSV file with existing categories
            output_file: Path to save standardized CSV (optional, auto-generated if not provided)
        
        Returns:
            Path to the output file
        """
        # Validate input file
        validate_csv_file(input_file)
        
        # Read and validate CSV
        logger.info(f"Loading CSV file: {input_file}")
        df = pd.read_csv(input_file)
        
        try:
            from ..utils.validation import validate_categorized_csv
        except ImportError:
            from utils.validation import validate_categorized_csv
        validate_categorized_csv(df)
        
        # Generate output path if not provided
        if output_file is None:
            output_file = self._auto_generate_output_path(input_file, 'standardized')
        
        # Get existing categories
        existing_categories = df['Contributor Category'].tolist()
        
        logger.info(f"Found {len(existing_categories)} categories to standardize")
        
        # Print original category statistics
        self._print_category_statistics(existing_categories, "Original category")
        
        # Standardize categories using fuzzy matching
        logger.info("Standardizing category names using fuzzy matching...")
        standardized_categories = [
            self._standardize_single_category(cat) for cat in existing_categories
        ]
        
        # Update the dataframe
        df['Contributor Category'] = standardized_categories
        
        # Save the updated CSV
        logger.info(f"Saving standardized results to: {output_file}")
        df.to_csv(output_file, index=False)
        
        # Print standardized category statistics
        self._print_category_statistics(standardized_categories, "Standardized category")
        
        logger.info("Standardization complete!")
        return output_file 