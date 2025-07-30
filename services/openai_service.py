import os
from typing import Dict, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in .env file.")
            raise ValueError("OPENAI_API_KEY not set in environment.")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

    def parse_natural_language(self, input_text: str, section: str) -> Tuple[Optional[Dict], str]:
        """Parse natural language input into structured CV data for a given section."""
        try:
            prompt = self._build_parse_prompt(input_text, section)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an assistant that extracts structured CV data from natural language input. Return only a JSON object with the required fields for the specified section, or an empty object if parsing fails. Do not include explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            result = response.choices[0].message.content
            parsed_data = eval(result)  # Safely parse JSON-like string
            if not isinstance(parsed_data, dict) or not parsed_data:
                return None, "Failed to parse input. Please provide details in a clear format."
            return parsed_data, ""
        except Exception as e:
            logger.error(f"OpenAI parsing error for section {section}: {e}")
            return None, "Error processing input. Please try again or use the structured format."

    def enhance_summary(self, summary: str) -> str:
        """Enhance a professional summary with AI suggestions."""
        try:
            prompt = f"Rephrase the following professional summary to be more concise and impactful, maintaining its meaning: {summary}"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an assistant that improves CV professional summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI summary enhancement error: {e}")
            return summary  # Return original summary on error

    def _build_parse_prompt(self, input_text: str, section: str) -> str:
        """Build a prompt for parsing natural language input based on the CV section."""
        prompts = {
            "personal_info": f"Extract name, email, phone, and address from: '{input_text}'. Return a JSON object with keys: name, email, phone, address.",
            "education": f"Extract a single education entry with institution, degree, year, and details from: '{input_text}'. Return a JSON object with keys: institution, degree, year, details.",
            "experience": f"Extract a single experience entry with company, role, start_date, end_date, and description from: '{input_text}'. Return a JSON object with keys: company, role, start_date, end_date, description. Use MM/YYYY format for dates, or 'present' for end_date if ongoing.",
            "projects": f"Extract a single project entry with name, description, and technologies from: '{input_text}'. Return a JSON object with keys: name, description, technologies.",
            "skills": f"Extract a list of skills from: '{input_text}'. Return a JSON object with a single key 'skills' containing a list of skill strings.",
            "certifications": f"Extract a single certification entry with name, issuer, and year from: '{input_text}'. Return a JSON object with keys: name, issuer, year.",
            "references": f"Extract a single reference entry with name, contact, and relationship from: '{input_text}'. Return a JSON object with keys: name, contact, relationship."
        }
        return prompts.get(section, "Invalid section.")