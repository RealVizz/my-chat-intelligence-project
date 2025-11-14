import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "storage.db"

DATA_DIR.mkdir(exist_ok=True)  # Ensure the data directory exists

load_dotenv(dotenv_path=BASE_DIR / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

OPENAI_API_MODEL = "gpt-4o-mini"  # gpt-4o-mini , gpt-5-mini , gpt-5-nano
GEMINI_API_MODEL = "gemini-2.5-flash-lite-preview-09-2025" # "gemini-2.5-flash-lite"  # "gemini-2.5-flash"

EXTERNAL_API_BASE_URL = "https://november7-730026606190.europe-west1.run.app"
EXTERNAL_API_MESSAGES_ENDPOINT = "/messages/"
EXTERNAL_API_PAGE_LIMIT = 100


BACKGROUND_SYNC_INTERVAL_SECONDS = 300  # 5 minutes
