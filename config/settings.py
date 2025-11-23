"""Configuration settings and environment variable management."""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional


class Settings:
    """Application settings and configuration."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize settings and load environment variables.
        
        Args:
            env_file: Path to .env file (optional)
        """
        # Load environment variables from .env file if it exists
        env_path = env_file or Path('.env')
        if Path(env_path).exists():
            load_dotenv(env_path)
        
        # Gemini API settings
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        # Google Sheets API settings
        self.google_sheets_credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
        self.google_sheets_token_path = os.getenv('GOOGLE_SHEETS_TOKEN_PATH', 'token.json')
        
        # Default output settings
        self.default_output_file = 'quizlet_cards.csv'
        self.default_prompt_type = 'general'
        
        # API settings
        self.gemini_max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', '4096'))
        self.gemini_temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.3'))
        self.gemini_batch_size = int(os.getenv('GEMINI_BATCH_SIZE', '5'))
    
    def validate_required_settings(self, use_google_sheets: bool = False) -> bool:
        """
        Validate that required settings are present.
        
        Args:
            use_google_sheets: Whether Google Sheets functionality is needed
            
        Returns:
            True if all required settings are valid
            
        Raises:
            ValueError: If required settings are missing
        """
        missing_settings = []
        
        # Always require Gemini API key
        if not self.gemini_api_key:
            missing_settings.append("GEMINI_API_KEY")
        
        # Google Sheets settings only required if using Google Sheets
        if use_google_sheets and not self.google_sheets_credentials_path:
            missing_settings.append("GOOGLE_SHEETS_CREDENTIALS_PATH")
        
        if missing_settings:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_settings)}. "
                "Please set them in your .env file or environment."
            )
        
        return True
    
    def get_google_sheets_config(self) -> dict:
        """Get Google Sheets configuration."""
        return {
            'credentials_path': self.google_sheets_credentials_path,
            'token_path': self.google_sheets_token_path
        }
    
    def get_gemini_config(self) -> dict:
        """Get Gemini API configuration."""
        return {
            'api_key': self.gemini_api_key,
            'model': self.gemini_model,
            'max_tokens': self.gemini_max_tokens,
            'temperature': self.gemini_temperature,
            'batch_size': self.gemini_batch_size
        }