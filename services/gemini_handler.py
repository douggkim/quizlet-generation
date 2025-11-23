"""Gemini API handler for generating definitions and content."""

import json
import os
from typing import Dict, List, Optional

from google import genai
from google.genai import types

from config.prompts import PromptTemplates


class GeminiHandler:
    """Handles Gemini API operations for content generation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        batch_size: Optional[int] = None,
    ):
        """
        Initialize the Gemini handler.

        Args:
            api_key: Gemini API key (if not provided, will use GEMINI_API_KEY env var)
            model: Model name (default: gemini-2.0-flash-exp)
            max_tokens: Maximum tokens per request (default: 4096)
            temperature: Response creativity level (default: 0.3)
            batch_size: Number of items to process per batch (default: 5)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not provided. Set GEMINI_API_KEY environment variable."
            )

        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.max_tokens = max_tokens or int(os.getenv("GEMINI_MAX_TOKENS", "4096"))
        self.temperature = temperature or float(os.getenv("GEMINI_TEMPERATURE", "0.3"))
        self.batch_size = batch_size or int(os.getenv("GEMINI_BATCH_SIZE", "5"))

        self.client = genai.Client(api_key=self.api_key)
        self.prompt_templates = PromptTemplates()

    def generate_definitions(
        self, keywords: List[str], prompt_type: str = "general"
    ) -> List[Dict[str, str]]:
        """
        Generate definitions for a list of keywords using Gemini API with batch processing.

        Args:
            keywords: List of keywords to define
            prompt_type: Type of prompt to use ("general", "algorithm", "leetcode")

        Returns:
            List of dictionaries with 'keyword' and 'definition' keys
        """
        if not keywords:
            return []
            
        all_results = []
        total_batches = (len(keywords) + self.batch_size - 1) // self.batch_size
        
        # Process keywords in batches
        for i in range(0, len(keywords), self.batch_size):
            batch = keywords[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            
            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)...")
            
            try:
                batch_results = self._generate_batch_definitions(batch, prompt_type)
                all_results.extend(batch_results)
            except Exception as e:
                print(f"Batch {batch_num} failed, falling back to individual processing: {str(e)}")
                # Fallback to individual processing for this batch
                for keyword in batch:
                    try:
                        enhanced_keyword, definition = self._generate_single_definition(keyword, prompt_type)
                        all_results.append({"keyword": enhanced_keyword, "definition": definition})
                    except Exception as individual_e:
                        print(f"Error generating definition for '{keyword}': {str(individual_e)}")
                        all_results.append({
                            "keyword": keyword,
                            "definition": f"Error generating definition: {str(individual_e)}",
                        })
        
        return all_results

    def generate_algorithm_problems(
        self, descriptions: List[str]
    ) -> List[Dict[str, str]]:
        """
        Generate algorithm problem keywords from brief descriptions with batch processing.

        Args:
            descriptions: List of brief problem descriptions

        Returns:
            List of dictionaries with 'keyword' and 'definition' keys
        """
        if not descriptions:
            return []
        
        # Step 1: Generate keywords from descriptions in batches
        print("Generating keywords from descriptions...")
        keyword_mapping = self._generate_keywords_batch(descriptions)
        
        # Step 2: Generate definitions using both keywords and original descriptions
        print("Generating definitions with problem context...")
        results = []
        all_batches = []
        
        # Prepare data for batch processing
        for description, keyword in keyword_mapping.items():
            all_batches.append((keyword, description))
        
        # Process in batches
        total_batches = (len(all_batches) + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(all_batches), self.batch_size):
            batch = all_batches[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            
            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)...")
            
            try:
                batch_results = self._generate_leetcode_definitions_batch(batch)
                results.extend(batch_results)
            except Exception as e:
                print(f"Batch {batch_num} failed, falling back to individual processing: {str(e)}")
                # Fallback to individual processing
                for keyword, description in batch:
                    try:
                        prompt = self.prompt_templates.get_leetcode_prompt_with_description(keyword, description)
                        response = self.client.models.generate_content(
                            model=self.model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                max_output_tokens=self.max_tokens, 
                                temperature=self.temperature
                            )
                        )
                        response_text = response.text.strip()
                        enhanced_keyword, definition = self._parse_keyword_definition_response(response_text, keyword)
                        results.append({"keyword": enhanced_keyword, "definition": definition})
                    except Exception as individual_e:
                        print(f"Error processing '{keyword}': {str(individual_e)}")
                        results.append({
                            "keyword": keyword,
                            "definition": f"Error generating content: {str(individual_e)}",
                        })

        return results

    def _generate_single_definition(self, keyword: str, prompt_type: str) -> tuple:
        """
        Generate a single definition using Gemini API.

        Args:
            keyword: The keyword to define
            prompt_type: Type of prompt to use

        Returns:
            Tuple of (enhanced_keyword, definition)
        """
        prompt = self.prompt_templates.get_prompt(prompt_type, keyword)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=self.max_tokens, temperature=self.temperature
                ),
            )

            # Parse the response to extract enhanced keyword and definition
            response_text = response.text.strip()
            return self._parse_keyword_definition_response(response_text, keyword)

        except Exception as e:
            raise ValueError(f"Gemini API error: {str(e)}")

    def _parse_keyword_definition_response(self, response_text: str, fallback_keyword: str) -> tuple:
        """
        Parse response that contains both enhanced keyword and definition.
        
        Args:
            response_text: Raw response from AI
            fallback_keyword: Original keyword to use if parsing fails
            
        Returns:
            Tuple of (enhanced_keyword, definition)
        """
        try:
            lines = response_text.split('\n')
            enhanced_keyword = fallback_keyword
            definition = response_text
            
            for line in lines:
                line = line.strip()
                if line.startswith('Keyword:'):
                    enhanced_keyword = line[8:].strip()  # Remove "Keyword:" prefix
                elif line.startswith('Definition:'):
                    definition = line[11:].strip()  # Remove "Definition:" prefix
                    break
            
            # If we couldn't parse properly, use the whole response as definition
            if not definition or definition == response_text:
                # Try to find keyword/definition pattern in the text
                if 'Keyword:' in response_text and 'Definition:' in response_text:
                    keyword_start = response_text.find('Keyword:') + 8
                    definition_start = response_text.find('Definition:') + 11
                    
                    if keyword_start < definition_start:
                        enhanced_keyword = response_text[keyword_start:definition_start-11].strip()
                        definition = response_text[definition_start:].strip()
                
            return enhanced_keyword, definition
            
        except Exception:
            # If parsing fails completely, return original keyword and full response
            return fallback_keyword, response_text

    def _generate_algorithm_keyword(self, description: str) -> str:
        """
        Generate a concise algorithm problem keyword from a description.

        Args:
            description: Brief description of the algorithm problem

        Returns:
            Concise keyword/title for the problem
        """
        prompt = self.prompt_templates.get_keyword_generation_prompt(description)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=100, temperature=self.temperature
                ),
            )

            keyword = response.text.strip()
            # Remove quotes if present
            keyword = keyword.strip("\"'")
            return keyword

        except Exception as e:
            raise ValueError(f"Gemini API error generating keyword: {str(e)}")

    def test_api_connection(self) -> bool:
        """
        Test the Gemini API connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents="Say 'test' if you can hear me.",
                config=types.GenerateContentConfig(max_output_tokens=10),
            )
            return "test" in response.text.lower()
        except Exception:
            return False

    def _generate_batch_definitions(self, keywords: List[str], prompt_type: str) -> List[Dict[str, str]]:
        """
        Generate definitions for multiple keywords in a single API call.
        
        Args:
            keywords: List of keywords to define
            prompt_type: Type of prompt to use
            
        Returns:
            List of dictionaries with 'keyword' and 'definition' keys
        """
        prompt = self.prompt_templates.get_batch_definition_prompt(keywords, prompt_type)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature
            )
        )
        
        # Parse JSON response
        try:
            response_text = response.text.strip()
            # Clean up response text if it has markdown formatting
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            results = json.loads(response_text.strip())
            
            # Validate that we got results for all keywords
            if len(results) != len(keywords):
                print(f"Warning: Expected {len(keywords)} results, got {len(results)}")
            
            return results
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response.text}")

    def _generate_keywords_batch(self, descriptions: List[str]) -> Dict[str, str]:
        """
        Generate keywords for multiple descriptions in batches.
        
        Args:
            descriptions: List of problem descriptions
            
        Returns:
            Dictionary mapping description to keyword
        """
        all_mappings = {}
        total_batches = (len(descriptions) + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(descriptions), self.batch_size):
            batch = descriptions[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            
            print(f"Keyword generation batch {batch_num}/{total_batches} ({len(batch)} items)...")
            
            try:
                prompt = self.prompt_templates.get_batch_keyword_generation_prompt(batch)
                
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=self.max_tokens,
                        temperature=self.temperature
                    )
                )
                
                # Parse JSON response
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                results = json.loads(response_text.strip())
                
                for result in results:
                    description = result.get('description', '')
                    keyword = result.get('keyword', '')
                    if description and keyword:
                        all_mappings[description] = keyword
                
            except Exception as e:
                print(f"Keyword batch {batch_num} failed, falling back to individual processing: {str(e)}")
                # Fallback to individual processing
                for description in batch:
                    try:
                        keyword = self._generate_algorithm_keyword(description)
                        all_mappings[description] = keyword
                    except Exception as individual_e:
                        print(f"Error generating keyword for '{description}': {str(individual_e)}")
                        all_mappings[description] = description  # Fallback to original description
        
        return all_mappings

    def _generate_leetcode_definitions_batch(self, keyword_description_pairs: List[tuple]) -> List[Dict[str, str]]:
        """
        Generate LeetCode definitions for multiple keyword-description pairs.
        
        Args:
            keyword_description_pairs: List of (keyword, description) tuples
            
        Returns:
            List of dictionaries with 'keyword' and 'definition' keys
        """
        # Create a custom batch prompt for LeetCode problems with descriptions
        items = []
        for keyword, description in keyword_description_pairs:
            items.append(f"Problem: {keyword}\nOriginal Description: {description}")
        
        items_text = '\n\n'.join(items)
        
        prompt = f"""Create concise study guides for these algorithm problems for quiz flashcards.

{items_text}

For each problem, include:
1. Problem category/type
2. Key solution approach (2-3 steps max)
3. Time/space complexity
4. Important edge cases

IMPORTANT: This will be exported to a CSV file, so in each study guide:
- Avoid commas or the CSV will break
- Use semicolons (;) or dashes (-) instead of commas
- Keep all text on a single line (no line breaks)
- Use simple punctuation only

These are for coding interview preparation - keep each guide focused and memorable.

Please respond with a valid JSON array containing objects with "keyword" and "definition" fields. 
The keyword should be enhanced with a brief description: "Problem Name - brief description of what it asks"

Example format:
[
  {{"keyword": "Two Sum - find two numbers that add up to target", "definition": "Array problem: Use hash map to store complements; check if current number's complement exists; return indices. O(n) time O(n) space."}},
  {{"keyword": "Binary Search - find target in sorted array", "definition": "Search algorithm: Compare target with middle element; eliminate half each iteration; continue until found. O(log n) time O(1) space."}}
]"""
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature
            )
        )
        
        # Parse JSON response
        try:
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            results = json.loads(response_text.strip())
            
            if len(results) != len(keyword_description_pairs):
                print(f"Warning: Expected {len(keyword_description_pairs)} results, got {len(results)}")
            
            return results
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response.text}")
