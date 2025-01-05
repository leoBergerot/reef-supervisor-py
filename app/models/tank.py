from pydantic import BaseModel


class TankRequest(BaseModel):
    name: str


class TankResponse(TankRequest):
    id: int
