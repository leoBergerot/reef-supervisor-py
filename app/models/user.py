from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    email: str


class UserRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreateRequest(UserRequest):
    """Registration body. turnstileToken is required when TURNSTILE_ENABLED=true."""

    turnstileToken: str | None = None
