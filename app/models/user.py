from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    email: str


class UserRequest(BaseModel):
    email: EmailStr
    password: str
