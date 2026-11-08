from datetime import datetime

from app.db.session import engine
from app.models import MeasureRequest
from sqlmodel import Session
from pydantic import ValidationError
from app.models.measure import MeasureRequestPatch
from app.repositories import ParameterRepository
from app.schemas import Measure
from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError


class MeasureManager:

    def create(self, measure_request: MeasureRequest) -> Measure:
        measure = Measure(**measure_request.model_dump())
        with Session(engine) as session:
            session.add(measure)
            session.commit()
            session.refresh(measure)
        return measure

    def updateValue(self, measure_request: MeasureRequestPatch, measure: Measure) -> Measure:
        measure.value = measure_request.value
        if measure_request.created_at:
            measure.created_at = measure_request.created_at

        try:
            MeasureRequest.model_validate(measure.model_dump())
        except ValidationError as e:
            raise RequestValidationError(e.errors(), )

        with Session(engine) as session:
            measure = session.merge(measure)
            session.commit()
            session.refresh(measure)
        return measure

    def update_timestamp(self, created_at: datetime, measure: Measure) -> Measure:
        parameter = ParameterRepository().get_by_id(measure.parameter_id)
        if parameter is None or parameter.need_value or measure.value is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Timestamp can only be set on a parameter that has no value",
            )
        measure.created_at = created_at
        with Session(engine) as session:
            measure = session.merge(measure)
            session.commit()
            session.refresh(measure)
        return measure

    def delete(self, measure_id: int, measure: Measure) -> None:
        with Session(engine) as sesion:
            sesion.delete(measure)
            sesion.commit()
