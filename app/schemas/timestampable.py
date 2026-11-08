from datetime import datetime, UTC
from typing import Annotated

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator
from sqlmodel import Field


def now_utc():
    return datetime.now(UTC)


class UTCNaiveDateTime(TypeDecorator):
    """Store aware UTC values in the existing timestamp-without-time-zone columns."""

    impl = DateTime(timezone=False)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None:
            return value.astimezone(UTC).replace(tzinfo=None)
        return value


class Timestampable():
    """
    Abstract class timestampable
    """
    created_at: Annotated[datetime, Field(
        default_factory=now_utc,
        nullable=False,
        sa_type=UTCNaiveDateTime(),
    )]
    updated_at: Annotated[datetime, Field(
        default_factory=now_utc,
        nullable=False,
        sa_type=UTCNaiveDateTime(),
    )]
