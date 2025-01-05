from datetime import datetime, UTC
from sqlalchemy import event
from sqlmodel import SQLModel
from app.schemas.timestampable import Timestampable


def attach_timestamps_events(cls):
    @event.listens_for(cls, "before_insert")
    def set_created_and_updated_timestamps(mapper, connection, target):
        if isinstance(target, Timestampable):
            target.created_at = datetime.now(UTC)
            target.updated_at = datetime.now(UTC)

    @event.listens_for(cls, "before_update")
    def set_updated_timestamp(mapper, connection, target):
        if isinstance(target, Timestampable):
            print(f"Hook triggered for: {target}")
            target.updated_at = datetime.now(UTC)


# Attach for all subclass at sql model
for subclass in SQLModel.__subclasses__():
    attach_timestamps_events(subclass)
