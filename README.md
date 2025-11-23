# Quizlet Card Generator

A Python tool to automatically generate Quizlet flashcards from various input sources using Google Gemini AI. Perfect for creating study materials for algorithms, programming concepts, or any subject matter.

## Features

- **Multiple Input Sources**: Support for both local CSV files and Google Sheets
- **AI-Powered Content Generation**: Uses Google Gemini AI to generate definitions and explanations
- **Flexible Prompt Templates**: Different templates for general terms, algorithms, and LeetCode problems
- **Keyword Generation**: Can generate concise keywords from problem descriptions
- **Quizlet-Ready Output**: Generates CSV files in the exact format needed for Quizlet import

## Installation

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and set up the project**:
   ```bash
   git clone https://github.com/douggkim/quizlet-generation
   cd quizlet-auto-generation
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# Required: Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_MAX_TOKENS=4096
GEMINI_TEMPERATURE=0.3
GEMINI_BATCH_SIZE=5

# Optional: Google Sheets API (only needed if using Google Sheets)
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/your/credentials.json
GOOGLE_SHEETS_TOKEN_PATH=path/to/your/token.json
```

### Gemini API Setup

To get your Gemini API key:

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" and create a new key
4. Copy the API key and add it to your `.env` file

### Google Sheets Setup (Optional)

If you want to use Google Sheets as input:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create credentials (Desktop Application type)
5. Download the credentials JSON file
6. Set the path in your `.env` file

## Usage

### Basic Examples

```bash
# Generate from local CSV file
uv run main.py --csv data.csv --column "terms" --output quiz.csv

# Generate from Google Sheets
uv run main.py --sheets "https://docs.google.com/spreadsheets/d/ABC123" --column "words" --output quiz.csv

# Use algorithm-specific prompts
uv run main.py --csv algorithms.csv --column "problems" --prompt-type algorithm --output algo_quiz.csv

# Generate keywords from descriptions (LeetCode mode)
uv run main.py --csv descriptions.csv --column "problem_desc" --prompt-type leetcode --generate-keywords --output leetcode_quiz.csv

# Use batch processing for large datasets
uv run main.py --csv large_dataset.csv --column "terms" --batch-size 10 --output quiz.csv
```

### Command Line Options

- `--csv PATH`: Path to local CSV file
- `--sheets URL`: Google Sheets URL or ID
- `--column NAME`: Column name to extract keywords from (required)
- `--output PATH`: Output CSV file path (default: `quizlet_cards.csv`)
- `--prompt-type TYPE`: Prompt type (`general`, `algorithm`, `leetcode`)
- `--generate-keywords`: Generate keywords from descriptions
- `--sheet-name NAME`: Specific sheet name in Google Sheets
- `--test-api`: Test API connections
- `--info`: Show input source information
- `--batch-size N`: Number of items to process per batch (default: 5)

### Prompt Types

1. **General** (`--prompt-type general`): Basic definitions for any terms
2. **Algorithm** (`--prompt-type algorithm`): Detailed explanations with steps for algorithms
3. **LeetCode** (`--prompt-type leetcode`): Problem-focused explanations with solution approaches

### Utility Commands

```bash
# Test API connections
uv run main.py --test-api

# Show available columns in your data source
uv run main.py --csv data.csv --column dummy --info
uv run main.py --sheets "SHEET_URL" --column dummy --info
```

## Input File Formats

### CSV Files
Your CSV should have headers with one column containing the terms/descriptions you want to process:

```csv
term,category
Binary Search,Algorithm
Hash Table,Data Structure
Two Pointers,Technique
```

### Google Sheets
Same format as CSV - use the first row for headers and ensure your target column contains the data to process.

## Output Format

The tool generates a CSV file with two columns (no headers) ready for Quizlet import:

```csv
Binary Search - algorithm to find target in sorted array,"Divides array in half repeatedly; compares target with middle element; eliminates half each iteration. O(log n) time complexity."
Hash Table - data structure that maps keys to values,"Uses hash function to compute index; handles collisions with chaining or probing; provides O(1) average lookup time."
Two Sum - find two numbers that add up to target,"Array problem: Use hash map to store complements; check if current number's complement exists; return indices. O(n) time O(n) space."
```

**Enhanced Keywords**: The AI enhances keywords with brief descriptions to make flashcard fronts more informative:
- **Algorithm problems**: Include what the problem asks (e.g., "Two Sum - find two numbers that add up to target")
- **General terms**: Include what the concept is (e.g., "Hash Table - data structure that maps keys to values")
- **Concise format**: 3-8 word descriptions that fit well on flashcards

**CSV Formatting**: The AI automatically formats definitions to be CSV-safe by:
- Using semicolons (;) or dashes (-) instead of commas
- Keeping content on single lines
- Using simple punctuation to prevent CSV parsing issues

## Use Cases

### 1. Algorithm Study Cards
Create flashcards for algorithm concepts:
```bash
uv run main.py --csv algorithms.csv --column "algorithm_name" --prompt-type algorithm --output algo_study.csv
```

### 2. LeetCode Problem Cards
Generate cards from problem descriptions:
```bash
uv run main.py --csv leetcode_problems.csv --column "description" --prompt-type leetcode --generate-keywords --output leetcode_cards.csv
```

### 3. General Vocabulary
Create definition cards for any subject:
```bash
uv run main.py --sheets "YOUR_SHEET_URL" --column "vocabulary" --prompt-type general --output vocab_cards.csv
```

### 4. Batch Processing for Large Datasets
Process hundreds of terms efficiently:
```bash
uv run main.py --csv large_terms.csv --column "terms" --batch-size 10 --output quiz.csv
```

## Performance & Batch Processing

The application now supports **batch processing** for improved performance:

- **Default batch size**: 5 items per API call
- **Configurable**: Use `--batch-size` or set `GEMINI_BATCH_SIZE` in your `.env`
- **Automatic fallback**: If batch fails, falls back to individual processing
- **Progress tracking**: Shows batch progress for large datasets

### Batch Size Guidelines:
- **Small datasets (< 20 items)**: Use default (5)
- **Medium datasets (20-100 items)**: Use 8-10 for optimal speed
- **Large datasets (100+ items)**: Use 10-15 but monitor API limits
- **Very large datasets (500+ items)**: Use 5-8 to avoid timeouts

## Project Structure

```
quizlet-auto-generation/
 main.py                 # Main CLI application
 config/
    settings.py         # Configuration management
   prompts.py          # Prompt templates
 services/
   csv_handler.py      # Local CSV operations
   sheets_handler.py   # Google Sheets API
   gemini_handler.py   # Gemini API integration
 utils/
   validators.py       # Input validation
   pyproject.toml          # uv project configuration
  .python-version         # Python version specification
  .env.example           # Environment variables template
```

## Development

The project uses `uv` for dependency management and Python version control:

```bash
# Install dependencies
uv sync

# Add new dependencies
uv add package-name

# Run the application
uv run main.py [options]

# Run with specific Python version
uv run python main.py [options]
```

## Troubleshooting

### Common Issues

1. **"Gemini API key not provided"**
   - Ensure `GEMINI_API_KEY` is set in your `.env` file

2. **"Google credentials file not found"**
   - Download credentials from Google Cloud Console
   - Set correct path in `GOOGLE_SHEETS_CREDENTIALS_PATH`

3. **"Column not found"**
   - Use `--info` flag to see available columns
   - Check spelling and case sensitivity

4. **"Permission denied" for Google Sheets**
   - Ensure the sheet is shared with your Google account
   - Check that credentials have proper permissions

5. **Batch processing fails**
   - Try reducing batch size with `--batch-size 3`
   - Check API rate limits in your Gemini console
   - Application will automatically fall back to individual processing

### Testing API Connections

```bash
uv run main.py --test-api
```

This will verify your Gemini API key and Google Sheets credentials (if configured).

## License

This project is licensed under the MIT License.