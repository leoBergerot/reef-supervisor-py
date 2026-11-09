from sqlmodel import create_engine
from app.core.config import settings


def normalize_database_url(url: str | None) -> str:
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    if url.startswith(("postgresql+psycopg://", "postgresql+psycopg2://")):
        return url
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    return url


DATABASE_URL = normalize_database_url(settings.DATABASE_URL)
engine = create_engine(DATABASE_URL, echo=settings.DEBUG)
