from pydantic import BaseModel, EmailStr, Field


class EmailRequest(BaseModel):
    email: EmailStr


class ActivationTokenResponse(BaseModel):
    email: EmailStr
    token: str


class ActivationConfirmRequest(BaseModel):
    token: str = Field(min_length=1)


class PasswordResetTokenResponse(BaseModel):
    id: int
    email: EmailStr
    token: str


class PasswordResetConfirmRequest(BaseModel):
    id: int
    token: str = Field(min_length=1)
    password: str = Field(min_length=1)
