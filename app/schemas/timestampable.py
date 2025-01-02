from datetime import datetime
from sqlmodel import Field
from typing import Optional


class Timestampable():
    """
    Classe de base abstraite pour les entités ayant des timestamps.
    """
    created_at: datetime | None = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime | None = Field(default_factory=datetime.utcnow, nullable=False)
