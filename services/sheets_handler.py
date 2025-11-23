"""Google Sheets API handler for reading sheet data."""

import os
from typing import List, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SheetsHandler:
    """Handles Google Sheets API operations."""
    
    # Scopes for Google Sheets API (read-only)
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize the Sheets handler.
        
        Args:
            credentials_path: Path to credentials.json file
            token_path: Path to token.json file for storing access tokens
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
        self.token_path = token_path or os.getenv('GOOGLE_SHEETS_TOKEN_PATH', 'token.json')
        self.service = None
    
    def authenticate(self) -> None:
        """Authenticate with Google Sheets API."""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    # If refresh fails, re-authenticate
                    creds = None
            
            if not creds:
                if not self.credentials_path or not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Google credentials file not found: {self.credentials_path}. "
                        "Please provide a valid credentials.json file."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        # Build the service
        self.service = build('sheets', 'v4', credentials=creds)
    
    def read_sheet_column(self, spreadsheet_url: str, column_name: str, 
                         sheet_name: Optional[str] = None) -> List[str]:
        """
        Read values from a specific column in a Google Sheet.
        
        Args:
            spreadsheet_url: URL or ID of the Google Sheet
            column_name: Name of the column to extract (e.g., 'A', 'B', or header name)
            sheet_name: Name of the specific sheet tab (optional, uses first sheet if not provided)
            
        Returns:
            List of values from the specified column
            
        Raises:
            ValueError: If the sheet cannot be accessed or column not found
        """
        if not self.service:
            self.authenticate()
        
        try:
            # Extract spreadsheet ID from URL if needed
            spreadsheet_id = self._extract_spreadsheet_id(spreadsheet_url)
            
            # Get sheet metadata to find the correct sheet name and column
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets = sheet_metadata.get('sheets', [])
            if not sheets:
                raise ValueError("No sheets found in the spreadsheet")
            
            # Use provided sheet name or default to first sheet
            if sheet_name:
                target_sheet = next((s for s in sheets if s['properties']['title'] == sheet_name), None)
                if not target_sheet:
                    available_sheets = [s['properties']['title'] for s in sheets]
                    raise ValueError(f"Sheet '{sheet_name}' not found. Available sheets: {available_sheets}")
            else:
                target_sheet = sheets[0]
            
            sheet_title = target_sheet['properties']['title']
            
            # First, try to get headers to check if column_name is a header
            header_range = f"'{sheet_title}'!1:1"
            header_result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=header_range
            ).execute()
            
            headers = header_result.get('values', [[]])[0] if header_result.get('values') else []
            
            # Determine the column letter/range
            if column_name in headers:
                # Column name is a header, find its position
                col_index = headers.index(column_name)
                col_letter = self._index_to_column_letter(col_index)
            else:
                # Assume column_name is already a column letter (A, B, C, etc.)
                col_letter = column_name.upper()
            
            # Read the entire column
            range_name = f"'{sheet_title}'!{col_letter}:{col_letter}"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # Flatten the values and filter out empty ones
            column_values = []
            for row in values[1:] if headers else values:  # Skip header if present
                if row:  # Skip empty rows
                    value = str(row[0]).strip()
                    if value:
                        column_values.append(value)
            
            return column_values
            
        except HttpError as e:
            raise ValueError(f"Error accessing Google Sheet: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error reading sheet: {str(e)}")
    
    def get_sheet_info(self, spreadsheet_url: str) -> dict:
        """
        Get information about the spreadsheet including sheet names and headers.
        
        Args:
            spreadsheet_url: URL or ID of the Google Sheet
            
        Returns:
            Dictionary with sheet information
        """
        if not self.service:
            self.authenticate()
        
        try:
            spreadsheet_id = self._extract_spreadsheet_id(spreadsheet_url)
            
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheets_info = []
            for sheet in sheet_metadata.get('sheets', []):
                sheet_title = sheet['properties']['title']
                
                # Get headers for this sheet
                header_range = f"'{sheet_title}'!1:1"
                header_result = self.service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=header_range
                ).execute()
                
                headers = header_result.get('values', [[]])[0] if header_result.get('values') else []
                
                sheets_info.append({
                    'name': sheet_title,
                    'headers': headers
                })
            
            return {
                'spreadsheet_title': sheet_metadata.get('properties', {}).get('title', 'Unknown'),
                'sheets': sheets_info
            }
            
        except Exception as e:
            raise ValueError(f"Error getting sheet info: {str(e)}")
    
    @staticmethod
    def _extract_spreadsheet_id(url_or_id: str) -> str:
        """Extract spreadsheet ID from URL or return ID if already provided."""
        if url_or_id.startswith('http'):
            # Extract ID from URL
            if '/spreadsheets/d/' in url_or_id:
                start = url_or_id.find('/spreadsheets/d/') + len('/spreadsheets/d/')
                end = url_or_id.find('/', start)
                if end == -1:
                    end = url_or_id.find('#', start)
                if end == -1:
                    end = len(url_or_id)
                return url_or_id[start:end]
            else:
                raise ValueError("Invalid Google Sheets URL format")
        else:
            # Assume it's already an ID
            return url_or_id
    
    @staticmethod
    def _index_to_column_letter(index: int) -> str:
        """Convert column index to letter (0 -> A, 1 -> B, etc.)."""
        result = ""
        while index >= 0:
            result = chr(65 + (index % 26)) + result
            index = index // 26 - 1
        return result