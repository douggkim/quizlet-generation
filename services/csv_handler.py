"""CSV file handling module for reading and writing CSV data."""

import pandas as pd
from typing import List, Dict, Any
import csv
from pathlib import Path


class CSVHandler:
    """Handles CSV file operations for input and output."""
    
    @staticmethod
    def read_csv(file_path: str, column_name: str) -> List[str]:
        """
        Read a CSV file and extract values from a specific column.
        
        Args:
            file_path: Path to the CSV file
            column_name: Name of the column to extract
            
        Returns:
            List of values from the specified column
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the column doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            
            if column_name not in df.columns:
                raise ValueError(f"Column '{column_name}' not found. Available columns: {list(df.columns)}")
            
            # Extract values and filter out NaN/null values
            values = df[column_name].dropna().tolist()
            return [str(value).strip() for value in values if str(value).strip()]
            
        except pd.errors.EmptyDataError:
            raise ValueError(f"CSV file is empty: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
    
    @staticmethod
    def write_quizlet_csv(output_file: str, keyword_definition_pairs: List[Dict[str, str]]) -> None:
        """
        Write keyword-definition pairs to a CSV file in Quizlet format.
        
        Args:
            output_file: Path to the output CSV file
            keyword_definition_pairs: List of dictionaries with 'keyword' and 'definition' keys
        """
        output_path = Path(output_file)
        
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write without headers as specified
                for pair in keyword_definition_pairs:
                    writer.writerow([pair['keyword'], pair['definition']])
                    
        except Exception as e:
            raise ValueError(f"Error writing CSV file: {str(e)}")
    
    @staticmethod
    def validate_csv_structure(file_path: str) -> List[str]:
        """
        Validate CSV file structure and return available column names.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of column names
        """
        try:
            df = pd.read_csv(file_path, nrows=0)  # Read only headers
            return list(df.columns)
        except Exception as e:
            raise ValueError(f"Error validating CSV structure: {str(e)}")