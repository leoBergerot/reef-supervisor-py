from sqlmodel import Session, select, and_
from app.db.session import engine
from app.models import PreferenceRequest
from app.schemas import Preference, Parameter, User


class PreferenceRepository:
    def get_by_id_and_user(self, id: int, user: User) -> Parameter:
        with Session(engine) as session:
            return session.exec(
                select(Preference).filter(and_(Preference.id == id, Preference.user_id == user.id))).first()

    def update_persist(self, preference_request: PreferenceRequest, preference: Preference) -> Preference:
        preference = preference.model_copy(update=preference_request.model_dump())
        with Session(engine) as session:
            preference = session.merge(preference)
            session.commit()
            session.refresh(preference)

        return preference
