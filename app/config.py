import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


APP_NAME = os.getenv("APP_NAME", "PocketSmart AI")

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-me-in-development"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "60"
    )
)

DATABASE_PATH = (
    BASE_DIR /
    os.getenv(
        "DATABASE_PATH",
        "data/pocketsmart.db"
    )
)

UPLOAD_DIR = BASE_DIR / "uploads"

MAX_UPLOAD_MB = int(
    os.getenv(
        "MAX_UPLOAD_MB",
        "5"
    )
)


DATABASE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)