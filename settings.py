import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application-wide settings
class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
    TEMPLATE_DIR = Path(os.getenv("TEMPLATE_DIR", "templates/"))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    @classmethod
    def validate(cls):
        """Validate critical settings."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in .env file")
        if not cls.TEMPLATE_DIR.exists():
            cls.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

# Initialize settings
settings = Settings()
settings.validate()