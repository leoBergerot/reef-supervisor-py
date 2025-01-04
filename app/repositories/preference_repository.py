from typing import Annotated, Type
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import Parameter


class ParameterRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def get_all(self) -> list[Type[Parameter]]:
        return self.db.query(Parameter).all()

    def get_by_id(self, parameter_id: int) -> Parameter:
        return self.db.query(Parameter).filter(Parameter.id == parameter_id).first()
