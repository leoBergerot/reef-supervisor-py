from app.db.session import engine
from app.models import MeasureRequest
from sqlmodel import Session
from pydantic import ValidationError
from app.models.measure import MeasureRequestPatch
from app.schemas import Measure
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

    def delete(self, measure_id: int, measure: Measure) -> None:
        with Session(engine) as sesion:
            sesion.delete(measure)
            sesion.commit()
