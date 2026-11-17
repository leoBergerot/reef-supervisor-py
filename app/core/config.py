import os
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent.parent

load_dotenv(APP_DIR / ".env")
load_dotenv(APP_DIR / ".env.local", override=True)


def _env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DEBUG: bool = _env_bool("DEBUG", "False")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    TURNSTILE_SECRET_KEY: str | None = os.getenv("TURNSTILE_SECRET_KEY")
    TURNSTILE_ENABLED: bool = _env_bool("TURNSTILE_ENABLED", "false")

    # Outbound email: MAIL_DRIVER=mailjet|smtp|auto (auto → mailjet when keys set, else smtp)
    MAIL_DRIVER: str = os.getenv("MAIL_DRIVER", "auto")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "contact@reef-supervisor.fr")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Reef Supervisor")
    MAILJET_API_KEY: str | None = os.getenv("MAILJET_API_KEY")
    # Prefer MAILJET_API_SECRET; MAILJET_SECRET kept for Nest-era env compatibility
    MAILJET_API_SECRET: str | None = os.getenv("MAILJET_API_SECRET") or os.getenv(
        "MAILJET_SECRET"
    )
    SMTP_HOST: str = os.getenv("SMTP_HOST", "maildev")
    SMTP_PORT: int = _env_int("SMTP_PORT", 1025)
    SMTP_USERNAME: str | None = os.getenv("SMTP_USERNAME") or None
    SMTP_PASSWORD: str | None = os.getenv("SMTP_PASSWORD") or None
    SMTP_USE_TLS: bool = _env_bool("SMTP_USE_TLS", "false")
    # Prefer FRONTEND_BASE_URL; FRONTEND_URL kept for Nest-era env compatibility
    FRONTEND_BASE_URL: str = (
        os.getenv("FRONTEND_BASE_URL")
        or os.getenv("FRONTEND_URL")
        or "http://localhost:5173"
    )


settings = Settings()
