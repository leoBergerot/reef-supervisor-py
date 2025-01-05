from typing import Annotated
from sqlmodel import Session
from fastapi import Depends, status, HTTPException

from app.db.session import engine
from app.models import ParameterRequest
from app.repositories import UserRepository
from app.util.util import mapped_model_to_schema
from app.schemas import Parameter, Preference


class ParameterManager:
    def __init__(self,
                 user_repository: Annotated[UserRepository, Depends(UserRepository)]):
        self.user_repository = user_repository

    def create_persist(self, parameter_request: ParameterRequest) -> Parameter:
        parameter = Parameter(**parameter_request.model_dump())
        with Session(engine) as session:
            session.add(parameter)
            session.commit()
            session.refresh(parameter)

            try:
                self._update_user_preferences(parameter, session)
            except:
                session.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Could not update user preference")

        return parameter

    def update_persist(self, parameter: Parameter, parameter_request: ParameterRequest) -> Parameter:
        parameter = mapped_model_to_schema(parameter_request, parameter)
        with Session(engine) as session:
            parameter = session.merge(parameter)
            session.commit()
            session.refresh(parameter)

        return parameter

    def _update_user_preferences(self, parameter: Parameter, session: Session):
        users = self.user_repository.get_all()
        for user in users:
            user.preferences.append(Preference(parameter_id=parameter.id, enabled=True))
            session.add(user)
        session.commit()
