import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "storage.db"

DATA_DIR.mkdir(exist_ok=True)

load_dotenv(dotenv_path=BASE_DIR / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

OPENAI_API_MODEL = "gpt-4o-mini"
GEMINI_API_MODEL = "gemini-2.5-flash-lite-preview-09-2025"

EXTERNAL_API_BASE_URL = "https://november7-730026606190.europe-west1.run.app"
EXTERNAL_API_MESSAGES_ENDPOINT = "/messages/"
EXTERNAL_API_PAGE_LIMIT = 1000

BACKGROUND_SYNC_INTERVAL_SECONDS = 300

ENTITY_RESOLUTION_HISTORY_LENGTH = 10
ANSWER_GENERATION_HISTORY_LENGTH = 30

# --- RAG & Search Configuration ---
FUZZY_SEARCH_SCORE_CUTOFF = 45.0
RAG_TOP_K = 50
