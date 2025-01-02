from datetime import datetime
from sqlalchemy import event
from sqlmodel import SQLModel
from app.schemas.timestampable import Timestampable
from app.schemas.user import User


def attach_timestamps_events(cls):
    @event.listens_for(cls, "before_insert")
    def set_created_and_updated_timestamps(mapper, connection, target):
        if isinstance(target, Timestampable):
            target.created_at = datetime.utcnow()
            target.updated_at = datetime.utcnow()

    @event.listens_for(cls, "before_update")
    def set_updated_timestamp(mapper, connection, target):
        if isinstance(target, Timestampable):
            print(f"Hook triggered for: {target}")
            target.updated_at = datetime.utcnow()


# Attach for all subclass at sql model
for subclass in SQLModel.__subclasses__():
    attach_timestamps_events(subclass)
