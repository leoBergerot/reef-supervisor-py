from typing import Annotated
from sqlmodel import Session
from fastapi import Depends, status, HTTPException
from app.db.session import get_db
from app.models import ParameterRequest
from app.repositories import UserRepository, ParameterRepository
from app.util.util import mapped_model_to_schema
from app.schemas import Parameter, Preference


class ParameterManager:
    def __init__(self, db: Annotated[Session, Depends(get_db)],
                 user_repository: Annotated[UserRepository, Depends(UserRepository)]):
        self.db = db
        self.user_repository = user_repository

    def create_persist(self, parameter_request: ParameterRequest) -> Parameter:
        parameter = Parameter()
        parameter = mapped_model_to_schema(parameter_request, parameter)

        self.db.add(parameter)
        self.db.commit()
        self.db.refresh(parameter)

        try:
            self._update_user_preferences(parameter)
        except:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Could not update user preference")

        return parameter

    def update_persist(self, parameter: Parameter, parameter_request: ParameterRequest) -> Parameter:
        parameter = mapped_model_to_schema(parameter_request, parameter)

        parameter = self.db.merge(parameter)
        self.db.commit()
        self.db.refresh(parameter)

        return parameter

    def _update_user_preferences(self, parameter: Parameter):
        users = self.user_repository.get_all()
        for user in users:
            user.preferences.append(Preference(parameter_id=parameter.id, enabled=True))
            self.db.add(user)
        self.db.commit()
