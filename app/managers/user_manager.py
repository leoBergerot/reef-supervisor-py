from typing import Annotated

from app.core.security import hash_password
from app.db.session import engine
from app.models import UserRequest
from app.repositories import ParameterRepository
from app.schemas import User, Preference
from fastapi import Depends
from sqlmodel import Session


class UserManager:
    def __init__(self, parameter_repository: Annotated[ParameterRepository, Depends(ParameterRepository)],
                 ):
        self.parameter_repository = parameter_repository
        with Session(engine) as session:
            self.db = session

    def create_add_preferences_persist(self, user: User) -> User:
        parameters = self.parameter_repository.get_all()
        for parameter in parameters:
            user.preferences.append(Preference(parameter_id=parameter.id, enabled=True))

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def update_persist(self, user_request: UserRequest, user: User) -> User:
        user.password = hash_password(user_request.password)
        user.email = str(user_request.email)

        merge_user = self.db.merge(user)
        self.db.commit()
        self.db.refresh(merge_user)

        return merge_user
