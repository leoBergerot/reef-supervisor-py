from sqlmodel import create_engine
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, echo=settings.DEBUG)
