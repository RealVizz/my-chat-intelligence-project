import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "storage.db"

DATA_DIR.mkdir(exist_ok=True)  # Ensure the data directory exists

load_dotenv(dotenv_path=BASE_DIR / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_API_MODEL = "gpt-4o-mini"  # gpt-4o-mini , gpt-5-mini , gpt-5-nano
