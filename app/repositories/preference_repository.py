from sqlmodel import Session, select, and_, col
from sqlalchemy.orm import joinedload

from app.db.session import engine
from app.schemas import Preference, User

from app.core.models import PreferenceRequest as PreferenceRequestCore
from app.core.entities import Preference as PreferenceCore
from app.core.entities import User as UserCore
from app.core.repositories import PreferenceRepository as DomainPreferenceRepository


class PreferenceRepository(DomainPreferenceRepository):
    def get_by_user(self, user_core: UserCore) -> list[PreferenceCore]:
        with Session(engine) as session:
            preferences = session.exec(
                select(Preference)
                .options(joinedload(Preference.parameter))
                .filter(col(Preference.user_id) == user_core.id)
            ).all()

        return [preference.to_core() for preference in preferences]

    def get_by_id_and_user(self, id: int, user_core: UserCore) -> PreferenceCore:
        with (Session(engine) as session):
            preference = session.exec(
                select(Preference)
                .options(joinedload(Preference.parameter))
                .filter(and_(Preference.id == id, Preference.user_id == user_core.id))
            ).first()
            return preference.to_core()

    def update_persist(self, preference_request: PreferenceRequestCore,
                       preference_core: PreferenceCore) -> PreferenceCore:
        preference_core.update(preference_request)
        preference = Preference().from_core(preference_core)

        with Session(engine) as session:
            preference = session.merge(preference)
            session.commit()
            session.refresh(preference)
            return preference.to_core()
