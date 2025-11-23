# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# OpenAI model to use
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

# Default language & country for Google Maps / SerpAPI
DEFAULT_HL = "en"
