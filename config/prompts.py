"""Prompt templates for different types of content generation."""

from typing import List


class PromptTemplates:
    """Contains prompt templates for various content generation scenarios."""

    def __init__(self):
        """Initialize prompt templates."""
        self.templates = {
            "general": self._general_definition_prompt,
            "algorithm": self._algorithm_definition_prompt,
            "leetcode": self._leetcode_definition_prompt,
        }

    def get_prompt(self, prompt_type: str, keyword: str) -> str:
        """
        Get a formatted prompt for the given type and keyword.

        Args:
            prompt_type: Type of prompt ("general", "algorithm", "leetcode")
            keyword: The keyword to generate content for

        Returns:
            Formatted prompt string
        """
        if prompt_type not in self.templates:
            raise ValueError(
                f"Unknown prompt type: {prompt_type}. Available types: {list(self.templates.keys())}"
            )

        return self.templates[prompt_type](keyword)

    def get_leetcode_prompt_with_description(
        self, keyword: str, description: str
    ) -> str:
        """
        Get LeetCode prompt that includes both keyword and original description.

        Args:
            keyword: Generated keyword for the problem
            description: Original problem description

        Returns:
            Formatted prompt string
        """
        return f"""Create a concise study guide for the algorithm problem "{keyword}" for a quiz flashcard.

Original Problem Description: "{description}"

Your response should be in this format:
Keyword: [problem name] - [brief description of what the problem asks]
Definition: [detailed study guide]

Include in the definition:
1. Problem category/type
2. Key solution approach (2-3 steps max)
3. Time/space complexity
4. Important edge cases

The keyword enhancement should briefly describe what the problem asks you to do based on the original description (5-8 words max).

IMPORTANT: This will be exported to a CSV file, so:
- Avoid commas in your study guide, or the CSV will break
- Use semicolons (;) or dashes (-) instead of commas
- Keep all text on a single line (no line breaks)
- Use simple punctuation only

This is for quick review before coding interviews - keep it focused and memorable.

Problem: {keyword}
Original Description: {description}

Keyword:
Definition:"""

    def get_keyword_generation_prompt(self, description: str) -> str:
        """
        Get prompt for generating algorithm problem keywords from descriptions.

        Args:
            description: Brief description of the algorithm problem

        Returns:
            Formatted prompt string
        """
        return f"""Generate a concise keyword/title for this algorithm problem that will work on a quiz flashcard:

Description: "{description}"

Create a short, memorable keyword or title (2-5 words max) that captures the core concept. The keyword should be:
- Easy to remember for quiz purposes
- Descriptive of the main technique or pattern
- Perfect as a flashcard front-side term

Respond with just the keyword/title, nothing else."""

    def _general_definition_prompt(self, keyword: str) -> str:
        """General definition prompt template."""
        return f"""Create a concise definition for the term "{keyword}" for a quiz flashcard.

Your response should be in this format:
Keyword: [original term] - [brief 3-5 word description]
Definition: [detailed explanation]

The definition should be:
- Clear and accurate
- 1-2 sentences maximum
- Perfect for quick study and review
- Easy to memorize for quiz purposes

The keyword enhancement should briefly describe what the term is (3-5 words max).

IMPORTANT: This will be exported to a CSV file, so:
- Avoid commas in your definition, or the CSV will break
- If you must use commas, use semicolons (;) or dashes (-) instead
- Keep text on a single line (no line breaks)
- Use simple punctuation only

Focus on the essential meaning that would help someone answer quiz questions about this term.

Term: {keyword}

Keyword:
Definition:"""

    def _algorithm_definition_prompt(self, keyword: str) -> str:
        """Algorithm-specific definition prompt template."""
        return f"""Create a study guide explanation for the algorithm/data structure "{keyword}" for a quiz flashcard.

Your response should be in this format:
Keyword: [original term] - [brief description of what it does]
Definition: [detailed explanation]

Include in the definition:
1. Brief definition
2. Key approach or steps (2-3 main points)
3. Time/space complexity if relevant
4. Primary use case

The keyword enhancement should briefly describe what the algorithm does (4-6 words max).

IMPORTANT: This will be exported to a CSV file, so:
- Avoid commas in your explanation, or the CSV will break
- Use semicolons (;) or dashes (-) instead of commas
- Keep all text on a single line (no line breaks)
- Use simple punctuation only

Keep it concise and focused - perfect for quick review before a coding interview or algorithm quiz.

Algorithm/Concept: {keyword}

Keyword:
Definition:"""

    def _leetcode_definition_prompt(self, keyword: str) -> str:
        """LeetCode-specific algorithm problem prompt template."""
        return f"""Create a concise study guide for the algorithm problem "{keyword}" for a quiz flashcard.

Your response should be in this format:
Keyword: [original problem given] - [brief description of what the problem asks]
Definition: [detailed study guide]

Include in the definition:
1. Problem category/type
2. Key solution approach (2-3 steps max)
3. Time/space complexity
4. Important edge cases

The keyword enhancement should briefly describe what the problem asks you to do (5-8 words max).

IMPORTANT: This will be exported to a CSV file, so:
- Avoid commas in your study guide, or the CSV will break
- Use semicolons (;) or dashes (-) instead of commas
- Keep all text on a single line (no line breaks)
- Use simple punctuation only

This is for quick review before coding interviews - keep it focused and memorable.

Problem: {keyword}

Keyword:
Definition:"""

    @classmethod
    def get_available_types(cls) -> list:
        """Get list of available prompt types."""
        return ["general", "algorithm", "leetcode"]

    def add_custom_template(self, template_name: str, template_function) -> None:
        """
        Add a custom prompt template.

        Args:
            template_name: Name for the new template
            template_function: Function that takes a keyword and returns a prompt string
        """
        self.templates[template_name] = template_function

    def get_batch_definition_prompt(self, keywords: List[str], prompt_type: str) -> str:
        """
        Get a batch prompt for generating multiple definitions at once.

        Args:
            keywords: List of keywords to define
            prompt_type: Type of prompt to use

        Returns:
            Formatted batch prompt string
        """
        if prompt_type == "general":
            prompt_description = "concise definitions for quiz flashcards"
            context = "These are for quick study and quiz review."
        elif prompt_type == "algorithm":
            prompt_description = (
                "algorithm/data structure explanations for coding interview flashcards"
            )
            context = "These are for coding interview preparation and algorithm review."
        elif prompt_type == "leetcode":
            prompt_description = (
                "LeetCode problem study guides for coding interview flashcards"
            )
            context = (
                "These are for coding interview preparation and problem pattern review."
            )
        else:
            prompt_description = "definitions for quiz flashcards"
            context = "These are for study and quiz review."

        keywords_list = "\n".join([f"- {keyword}" for keyword in keywords])

        return f"""Create {prompt_description} for the following terms. {context}

Terms to define:
{keywords_list}

Please respond with a valid JSON array containing objects with "keyword" and "definition" fields. Each definition should be:
- Concise and focused (1-2 sentences for general, 3-4 for algorithm/leetcode)
- Perfect for quiz/flashcard study
- Clear and memorable

IMPORTANT: This will be exported to a CSV file, so in each definition:
- Use the original keyword given for the first part ('term' from below)
- Avoid commas or the CSV will break
- Use semicolons (;) or dashes (-) instead of commas
- Keep all text on a single line (no line breaks)
- Use simple punctuation only

Format your response as:
[
  {{"keyword": "term1 - brief description of what it is", "definition": "detailed definition here"}},
  {{"keyword": "term2 - brief description of what it is", "definition": "detailed definition here"}}
]

Example:
{{"keyword": "Binary Search - algorithm to find target in sorted array", "definition": "Divides array in half repeatedly; compares target with middle element; eliminates half each iteration. O(log n) time complexity."}}"""

    def get_batch_keyword_generation_prompt(self, descriptions: List[str]) -> str:
        """
        Get a batch prompt for generating multiple keywords from descriptions.

        Args:
            descriptions: List of problem descriptions

        Returns:
            Formatted batch prompt string
        """
        descriptions_list = "\n".join([f"- {desc}" for desc in descriptions])

        return f"""Generate concise keywords/titles for these algorithm problems that will work on quiz flashcards:

Problem Descriptions:
{descriptions_list}

For each description, create a short, memorable keyword or title (2-5 words max) that captures the core concept.

Please respond with a valid JSON array containing objects with "description" and "keyword" fields:
[
  {{"description": "original description", "keyword": "generated keyword"}},
  {{"description": "original description", "keyword": "generated keyword"}}
]

Note: Keywords should be concise titles only (like "Two Sum" or "Binary Search") - they will be enhanced with descriptions later."""
