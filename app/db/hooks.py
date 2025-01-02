from datetime import datetime
from sqlalchemy import event
from sqlmodel import SQLModel
from app.schemas.timestampable import Timestampable

@event.listens_for(SQLModel, "before_update")
def update_timestamp(mapper, connection, target):
    if isinstance(target, Timestampable):
        target.updated_at = datetime.utcnow()