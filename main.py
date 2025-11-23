#!/usr/bin/env python3
"""
Quizlet Card Generator - Generate Quizlet cards from various input sources using Gemini AI.
"""

import argparse
import sys
from typing import Dict, List

from config.prompts import PromptTemplates
from config.settings import Settings
from services.csv_handler import CSVHandler
from services.gemini_handler import GeminiHandler
from services.sheets_handler import SheetsHandler
from utils.validators import InputValidator


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate Quizlet cards from various input sources using Gemini AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        # Generate from local CSV file
        python main.py --csv data.csv --column "terms" --output quiz.csv

        # Generate from Google Sheets
        python main.py --sheets "https://docs.google.com/spreadsheets/d/ABC123" --column "words" --output quiz.csv

        # Use algorithm-specific prompts
        python main.py --csv algorithms.csv --column "problems" --prompt-type algorithm --output algo_quiz.csv

        # Generate keywords from descriptions (LeetCode mode)
        python main.py --csv descriptions.csv --column "problem_desc" --prompt-type leetcode --generate-keywords --output leetcode_quiz.csv
        """,
    )

    # Input source (mutually exclusive)
    # input_group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument("--csv", type=str, help="Path to local CSV file")
    parser.add_argument("--sheets", type=str, help="Google Sheets URL or ID")

    # Required arguments
    parser.add_argument(
        "--column",
        type=str,
        required=False,
        help="Column name to extract keywords from",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="quizlet_cards.csv",
        help="Output CSV file path (default: quizlet_cards.csv)",
    )

    # Optional arguments
    parser.add_argument(
        "--prompt-type",
        type=str,
        choices=["general", "algorithm", "leetcode"],
        default="general",
        help="Type of prompt to use for content generation (default: general)",
    )

    parser.add_argument(
        "--generate-keywords",
        action="store_true",
        help="Generate keywords from descriptions (useful for LeetCode problems)",
    )

    parser.add_argument(
        "--sheet-name",
        type=str,
        help="Specific sheet name in Google Sheets (optional, uses first sheet if not provided)",
    )

    parser.add_argument(
        "--env-file",
        type=str,
        help="Path to .env file (default: .env in current directory)",
    )

    parser.add_argument(
        "--test-api", action="store_true", help="Test API connections and exit"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Show information about the input source (available columns, etc.)",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        help="Number of items to process per batch (default: from env or 5)",
    )

    return parser


def load_input_data(args, settings: Settings) -> List[str]:
    """Load data from the specified input source."""
    try:
        if args.csv:
            # Validate CSV file
            InputValidator.validate_csv_file(args.csv)

            # Read CSV data
            csv_handler = CSVHandler()
            return csv_handler.read_csv(args.csv, args.column)

        elif args.sheets:
            # Validate settings for Google Sheets
            settings.validate_required_settings(use_google_sheets=True)
            InputValidator.validate_google_sheets_url(args.sheets)

            # Read Google Sheets data
            sheets_config = settings.get_google_sheets_config()
            sheets_handler = SheetsHandler(
                credentials_path=sheets_config["credentials_path"],
                token_path=sheets_config["token_path"],
            )
            return sheets_handler.read_sheet_column(
                args.sheets, args.column, args.sheet_name
            )

    except Exception as e:
        print(f"Error loading input data: {str(e)}", file=sys.stderr)
        sys.exit(1)


def show_input_info(args, settings: Settings) -> None:
    """Show information about the input source."""
    try:
        if args.csv:
            csv_handler = CSVHandler()
            columns = csv_handler.validate_csv_structure(args.csv)
            print(f"CSV file: {args.csv}")
            print(f"Available columns: {', '.join(columns)}")

        elif args.sheets:
            settings.validate_required_settings(use_google_sheets=True)
            sheets_config = settings.get_google_sheets_config()
            sheets_handler = SheetsHandler(
                credentials_path=sheets_config["credentials_path"],
                token_path=sheets_config["token_path"],
            )

            info = sheets_handler.get_sheet_info(args.sheets)
            print(f"Spreadsheet: {info['spreadsheet_title']}")
            print("\nSheets and columns:")
            for sheet in info["sheets"]:
                print(f"  Sheet: {sheet['name']}")
                if sheet["headers"]:
                    print(f"    Columns: {', '.join(sheet['headers'])}")
                else:
                    print("    No headers found")

    except Exception as e:
        print(f"Error getting input info: {str(e)}", file=sys.stderr)
        sys.exit(1)


def test_api_connections(settings: Settings) -> None:
    """Test API connections."""
    print("Testing API connections...")

    # Test Gemini API
    try:
        gemini_config = settings.get_gemini_config()
        gemini_handler = GeminiHandler(
            api_key=gemini_config["api_key"],
            model=gemini_config["model"],
            max_tokens=gemini_config["max_tokens"],
            temperature=gemini_config["temperature"],
            batch_size=gemini_config["batch_size"],
        )
        if gemini_handler.test_api_connection():
            print("✓ Gemini API connection successful")
        else:
            print("✗ Gemini API connection failed")
            return
    except Exception as e:
        print(f"✗ Gemini API connection failed: {str(e)}")
        return

    # Test Google Sheets API (if credentials available)
    try:
        if settings.google_sheets_credentials_path:
            sheets_config = settings.get_google_sheets_config()
            sheets_handler = SheetsHandler(
                credentials_path=sheets_config["credentials_path"],
                token_path=sheets_config["token_path"],
            )
            sheets_handler.authenticate()
            print("✓ Google Sheets API connection successful")
        else:
            print("- Google Sheets API credentials not configured (optional)")
    except Exception as e:
        print(f"- Google Sheets API connection failed: {str(e)}")

    print("\nAPI connection tests completed.")


def generate_quizlet_cards(
    input_data: List[str], args, settings: Settings
) -> List[Dict[str, str]]:
    """Generate Quizlet cards using Gemini API."""
    try:
        # Initialize Gemini handler
        gemini_config = settings.get_gemini_config()
        batch_size = args.batch_size if args.batch_size else gemini_config["batch_size"]
        gemini_handler = GeminiHandler(
            api_key=gemini_config["api_key"],
            model=gemini_config["model"],
            max_tokens=gemini_config["max_tokens"],
            temperature=gemini_config["temperature"],
            batch_size=batch_size,
        )

        print(f"Generating content for {len(input_data)} items...")

        # Generate content based on mode
        if args.generate_keywords:
            # Generate keywords from descriptions, then definitions
            results = gemini_handler.generate_algorithm_problems(input_data)
        else:
            # Generate definitions for existing keywords
            results = gemini_handler.generate_definitions(input_data, args.prompt_type)

        print(f"Successfully generated {len(results)} cards")
        return results

    except Exception as e:
        print(f"Error generating content: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        # Load settings
        settings = Settings(env_file=args.env_file)

        # Validate basic requirements
        settings.validate_required_settings(use_google_sheets=bool(args.sheets))

        # Handle special modes
        if args.test_api:
            test_api_connections(settings)
            return

        if args.info:
            show_input_info(args, settings)
            return

        # Validate inputs
        InputValidator.validate_column_name(args.column)
        InputValidator.validate_output_path(args.output)
        InputValidator.validate_prompt_type(
            args.prompt_type, PromptTemplates.get_available_types()
        )

        # Load input data
        print(f"Loading data from {'CSV file' if args.csv else 'Google Sheets'}...")
        input_data = load_input_data(args, settings)

        if not input_data:
            print("No data found in the specified column.", file=sys.stderr)
            sys.exit(1)

        print(f"Loaded {len(input_data)} items from column '{args.column}'")

        # Generate Quizlet cards
        results = generate_quizlet_cards(input_data, args, settings)

        # Write output
        csv_handler = CSVHandler()
        csv_handler.write_quizlet_csv(args.output, results)

        print(f"✓ Successfully generated {len(results)} Quizlet cards")
        print(f"✓ Output written to: {args.output}")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
