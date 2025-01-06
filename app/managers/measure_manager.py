from app.db.session import engine
from app.models import MeasureRequest
from sqlmodel import Session

from app.schemas import Measure


class MeasureManager:

    def create(self, measure_request: MeasureRequest) -> Measure:
        measure = Measure(**measure_request.model_dump())
        with Session(engine) as session:
            session.add(measure)
            session.commit()
            session.refresh(measure)
        print("test", measure)
        return measure
