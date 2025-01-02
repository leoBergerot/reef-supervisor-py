from datetime import datetime
from sqlalchemy import event
from sqlmodel import SQLModel
from app.schemas.timestampable import Timestampable


@event.listens_for(SQLModel, "before_insert")
def set_created_and_updated_timestamps(mapper, connection, target):
    if isinstance(target, Timestampable):
        target.created_at = datetime.utcnow()
        target.updated_at = datetime.utcnow()

# Hook avant une mise à jour
@event.listens_for(SQLModel, "before_update")
def set_updated_timestamp(mapper, connection, target):
    if isinstance(target, Timestampable):
        target.updated_at = datetime.utcnow()
