"""
Input validation utilities for the categorization tool.
"""

import os
import pandas as pd
from typing import List, Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_csv_file(file_path: str) -> None:
    """
    Validate that a CSV file exists and is readable.
    
    Args:
        file_path: Path to the CSV file
    
    Raises:
        ValidationError: If file doesn't exist or isn't readable
    """
    if not os.path.exists(file_path):
        raise ValidationError(f"Input file '{file_path}' not found")
    
    if not os.path.isfile(file_path):
        raise ValidationError(f"'{file_path}' is not a file")
    
    if not file_path.lower().endswith('.csv'):
        raise ValidationError(f"'{file_path}' is not a CSV file")
    
    try:
        # Try to read the first few rows to validate format
        pd.read_csv(file_path, nrows=1)
    except Exception as e:
        raise ValidationError(f"Error reading CSV file '{file_path}': {str(e)}")


def validate_required_columns(df: pd.DataFrame, required_columns: Optional[List[str]] = None) -> None:
    """
    Validate that required columns exist in the dataframe.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
    
    Raises:
        ValidationError: If required columns are missing
    """
    if required_columns is None:
        required_columns = ['Contributor Name']
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValidationError(f"Missing required columns: {missing_columns}")
    
    # Check for empty dataframe
    if len(df) == 0:
        raise ValidationError("CSV file is empty")
    
    # Check for columns with all null values
    null_columns = [col for col in required_columns if df[col].isnull().all()]
    if null_columns:
        raise ValidationError(f"Required columns contain no data: {null_columns}")


def validate_output_directory(output_path: str) -> None:
    """
    Validate that the output directory exists or can be created.
    
    Args:
        output_path: Path to the output file
    
    Raises:
        ValidationError: If output directory cannot be created
    """
    output_dir = os.path.dirname(output_path)
    
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            raise ValidationError(f"Cannot create output directory '{output_dir}': {str(e)}")


def validate_file_permissions(file_path: str) -> None:
    """
    Validate that a file can be written to.
    
    Args:
        file_path: Path to the file
    
    Raises:
        ValidationError: If file cannot be written to
    """
    directory = os.path.dirname(file_path)
    
    # Check if directory is writable
    if not os.access(directory, os.W_OK):
        raise ValidationError(f"No write permission for directory '{directory}'")
    
    # Check if file exists and is writable
    if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
        raise ValidationError(f"No write permission for file '{file_path}'")


def validate_categorized_csv(df: pd.DataFrame) -> None:
    """
    Validate that a CSV file contains the expected category column.
    
    Args:
        df: DataFrame to validate
    
    Raises:
        ValidationError: If category column is missing
    """
    if 'Contributor Category' not in df.columns:
        raise ValidationError("CSV file must contain 'Contributor Category' column")
    
    # Check if category column has any non-null values
    if df['Contributor Category'].isnull().all():
        raise ValidationError("'Contributor Category' column contains no data") 