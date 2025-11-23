"""Input validation utilities."""

import os
import re
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse


class InputValidator:
    """Validates various types of user input."""
    
    @staticmethod
    def validate_csv_file(file_path: str) -> bool:
        """
        Validate that a CSV file exists and is readable.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            True if valid
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a CSV or not readable
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        if not path.suffix.lower() == '.csv':
            raise ValueError(f"File is not a CSV: {file_path}")
        
        if not os.access(path, os.R_OK):
            raise ValueError(f"File is not readable: {file_path}")
        
        return True
    
    @staticmethod
    def validate_google_sheets_url(url: str) -> bool:
        """
        Validate Google Sheets URL format.
        
        Args:
            url: Google Sheets URL or ID
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If URL format is invalid
        """
        # If it's not a URL, assume it's a spreadsheet ID
        if not url.startswith('http'):
            # Validate spreadsheet ID format (alphanumeric, underscores, hyphens)
            if not re.match(r'^[a-zA-Z0-9_-]+$', url):
                raise ValueError(f"Invalid spreadsheet ID format: {url}")
            return True
        
        # Validate URL format
        parsed = urlparse(url)
        if parsed.netloc not in ['docs.google.com', 'sheets.google.com']:
            raise ValueError(f"Invalid Google Sheets domain: {parsed.netloc}")
        
        if '/spreadsheets/' not in url:
            raise ValueError("URL does not appear to be a Google Sheets URL")
        
        return True
    
    @staticmethod
    def validate_output_path(output_path: str) -> bool:
        """
        Validate output file path.
        
        Args:
            output_path: Path for output file
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If path is invalid
        """
        path = Path(output_path)
        
        # Check if parent directory exists or can be created
        parent_dir = path.parent
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Cannot create output directory: {str(e)}")
        
        # Check if we can write to the directory
        if not os.access(parent_dir, os.W_OK):
            raise ValueError(f"No write permission for directory: {parent_dir}")
        
        # If file exists, check if we can overwrite it
        if path.exists() and not os.access(path, os.W_OK):
            raise ValueError(f"No write permission for file: {output_path}")
        
        return True
    
    @staticmethod
    def validate_prompt_type(prompt_type: str, available_types: List[str]) -> bool:
        """
        Validate prompt type.
        
        Args:
            prompt_type: The prompt type to validate
            available_types: List of available prompt types
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If prompt type is invalid
        """
        if prompt_type not in available_types:
            raise ValueError(
                f"Invalid prompt type: {prompt_type}. "
                f"Available types: {', '.join(available_types)}"
            )
        
        return True
    
    @staticmethod
    def validate_column_name(column_name: str) -> bool:
        """
        Validate column name format.
        
        Args:
            column_name: Column name to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If column name is invalid
        """
        if not column_name:
            raise ValueError("Column name cannot be empty")
        
        if not column_name.strip():
            raise ValueError("Column name cannot be only whitespace")
        
        return True
    
    @staticmethod
    def validate_credentials_file(file_path: Optional[str]) -> bool:
        """
        Validate Google credentials file.
        
        Args:
            file_path: Path to credentials file
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If credentials file is invalid
        """
        if not file_path:
            return True  # Optional file
        
        path = Path(file_path)
        
        if not path.exists():
            raise ValueError(f"Credentials file not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Credentials path is not a file: {file_path}")
        
        if not path.suffix.lower() == '.json':
            raise ValueError(f"Credentials file must be JSON: {file_path}")
        
        return True