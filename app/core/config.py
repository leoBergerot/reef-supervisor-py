import os
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent.parent

load_dotenv(APP_DIR / ".env")
load_dotenv(APP_DIR / ".env.local", override=True)


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    TURNSTILE_SECRET_KEY: str | None = os.getenv("TURNSTILE_SECRET_KEY")
    TURNSTILE_ENABLED: bool = os.getenv("TURNSTILE_ENABLED", "false").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


settings = Settings()
