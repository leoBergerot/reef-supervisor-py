import math
from typing import Sequence

from app.db.session import engine
from app.schemas import User, Measure, Parameter, Tank
from sqlmodel import Session, select, and_, col
from sqlalchemy import func


class MeasureRepository:
    def get_measure_by_id_and_user(self, measure_id: int, user: User) -> Measure | None:
        with Session(engine) as session:
            return session.exec(
                select(Measure)
                .join(Tank)
                .filter(
                    and_(
                        col(Measure.id) == measure_id,
                        col(Tank.user_id) == user.id
                    )
                )).first()

    def get_filter(self, user: User, parameter_id: int | None = None, tank_id: int | None = None, page: int = 1,
                   offset=10) -> Sequence[Measure]:
        with Session(engine) as session:
            conditions = [col(Tank.user_id) == user.id]
            if parameter_id:
                conditions.append(col(Measure.parameter_id) == parameter_id)
            if tank_id:
                conditions.append(col(Measure.tank_id) == tank_id)

            count = session.exec(
                select(func.count(col(Measure.id))).join(Tank).filter(and_(*conditions))
            ).one()

            total_page = max(1, math.ceil(count / offset))
            page = min(max(1, page), total_page)

            results_query = (
                select(Measure)
                .join(Tank)
                .filter(and_(*conditions))
                .order_by(col(Measure.id).desc())
                .offset((page - 1) * offset)
                .limit(offset)
            )
            results = session.exec(results_query).all()

            return {'results': results, 'total': count, 'total_page': total_page}
