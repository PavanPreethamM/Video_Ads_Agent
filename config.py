from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")