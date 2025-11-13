import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_MODEL = "gpt-4o-mini"  # gpt-4o-mini , gpt-5-mini , gpt-5-nano
