from pydantic import BaseModel, EmailStr, Field


class EmailRequest(BaseModel):
    """Auth email trigger body. turnstileToken is required when TURNSTILE_ENABLED=true."""

    email: EmailStr
    turnstileToken: str | None = None
    # Preferred: locale; lang accepted as alias from the Vite app.
    locale: str | None = None
    lang: str | None = None


class MessageResponse(BaseModel):
    detail: str


class ActivationConfirmRequest(BaseModel):
    token: str = Field(min_length=1)


class PasswordResetConfirmRequest(BaseModel):
    """Recover-password body. turnstileToken is required when TURNSTILE_ENABLED=true."""

    id: int
    token: str = Field(min_length=1)
    password: str = Field(min_length=1)
    turnstileToken: str | None = None
