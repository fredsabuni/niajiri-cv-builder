import os
from pathlib import Path
import streamlit as st

# Application-wide settings
class Settings:
    @classmethod
    def get_openai_api_key(cls):
        """Get OpenAI API key from Streamlit secrets or environment."""
        try:
            # Try to get API key from Streamlit secrets (for cloud deployment)
            return st.secrets["OPENAI_API_KEY"]
        except (KeyError, AttributeError):
            # Fallback to environment variable for local development
            return os.getenv("OPENAI_API_KEY")
    
    @property
    def OPENAI_API_KEY(self):
        return self.get_openai_api_key()
    
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
    TEMPLATE_DIR = Path(os.getenv("TEMPLATE_DIR", "templates/"))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    @classmethod
    def validate(cls):
        """Validate critical settings."""
        instance = cls()
        if not instance.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in Streamlit secrets or environment variables")
        if not cls.TEMPLATE_DIR.exists():
            cls.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

# Initialize settings
settings = Settings()
settings.validate()