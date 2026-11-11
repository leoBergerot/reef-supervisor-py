from sqlmodel import Session, select, col, and_, func

from app.db.session import engine
from app.schemas import TankParameter, Parameter


class TankParameterRepository:
    def list_for_tank(self, tank_id: int) -> list[tuple[TankParameter, Parameter]]:
        with Session(engine) as session:
            rows = session.exec(
                select(TankParameter, Parameter)
                .join(Parameter, col(Parameter.id) == col(TankParameter.parameter_id))
                .where(col(TankParameter.tank_id) == tank_id)
                .order_by(col(TankParameter.sort_order), col(TankParameter.id))
            ).all()
            return list(rows)

    def get_for_tank_parameter(self, tank_id: int, parameter_id: int) -> TankParameter | None:
        with Session(engine) as session:
            return session.exec(
                select(TankParameter).where(
                    and_(
                        col(TankParameter.tank_id) == tank_id,
                        col(TankParameter.parameter_id) == parameter_id,
                    )
                )
            ).first()

    def is_enabled(self, tank_id: int, parameter_id: int) -> bool:
        row = self.get_for_tank_parameter(tank_id, parameter_id)
        return bool(row and row.enabled)

    def _next_sort_order(self, session: Session, tank_id: int) -> int:
        current = session.exec(
            select(func.max(TankParameter.sort_order)).where(col(TankParameter.tank_id) == tank_id)
        ).one()
        return 0 if current is None else int(current) + 1

    def seed_for_tank(self, tank_id: int, parameter_ids: list[int], enabled: bool = True) -> None:
        if not parameter_ids:
            return
        with Session(engine) as session:
            existing = {
                row.parameter_id: row
                for row in session.exec(
                    select(TankParameter).where(col(TankParameter.tank_id) == tank_id)
                ).all()
            }
            next_order = self._next_sort_order(session, tank_id)
            for parameter_id in parameter_ids:
                if parameter_id in existing:
                    continue
                session.add(
                    TankParameter(
                        tank_id=tank_id,
                        parameter_id=parameter_id,
                        enabled=enabled,
                        sort_order=next_order,
                    )
                )
                next_order += 1
            session.commit()

    def upsert_enabled(
        self,
        tank_id: int,
        parameter_id: int,
        enabled: bool,
        sort_order: int | None = None,
    ) -> TankParameter:
        with Session(engine) as session:
            row = session.exec(
                select(TankParameter).where(
                    and_(
                        col(TankParameter.tank_id) == tank_id,
                        col(TankParameter.parameter_id) == parameter_id,
                    )
                )
            ).first()
            if row is None:
                row = TankParameter(
                    tank_id=tank_id,
                    parameter_id=parameter_id,
                    enabled=enabled,
                    sort_order=sort_order if sort_order is not None else self._next_sort_order(session, tank_id),
                )
            else:
                row.enabled = enabled
                if sort_order is not None:
                    row.sort_order = sort_order
            session.add(row)
            session.commit()
            session.refresh(row)
            return row

    def create(self, tank_id: int, parameter_id: int, enabled: bool = True) -> TankParameter:
        with Session(engine) as session:
            row = TankParameter(
                tank_id=tank_id,
                parameter_id=parameter_id,
                enabled=enabled,
                sort_order=self._next_sort_order(session, tank_id),
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return row

    def delete_for_tank(self, tank_id: int) -> list[int]:
        """Delete tank_parameter rows and return linked custom parameter ids."""
        with Session(engine) as session:
            rows = session.exec(
                select(TankParameter, Parameter)
                .join(Parameter, col(Parameter.id) == col(TankParameter.parameter_id))
                .where(col(TankParameter.tank_id) == tank_id)
            ).all()
            custom_ids = [parameter.id for _, parameter in rows if parameter.is_custom]
            for tank_parameter, _ in rows:
                session.delete(tank_parameter)
            session.commit()
            return custom_ids
