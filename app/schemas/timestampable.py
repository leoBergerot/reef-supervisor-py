from datetime import datetime, UTC
from typing import Annotated

from sqlmodel import Field


def now_utc():
    return datetime.now(UTC)


class Timestampable():
    """
    Abstract class timestampable
    """
    created_at: Annotated[datetime, Field(default_factory=now_utc, nullable=False)]
    updated_at: Annotated[datetime, Field(default_factory=now_utc, nullable=False)]
