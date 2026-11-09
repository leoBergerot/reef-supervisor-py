import bcrypt
from app.core.config import settings
from pydantic import BaseModel
from app.repositories.user_repository import UserRepository
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from app.schemas.user import User
from jwt.exceptions import InvalidTokenError
import jwt

ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"USER": "Basic user.", "ADMIN": "Admin User."},
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    scopes: list[str] = []


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


class Auth:
    def __init__(self, user_repository: Annotated[UserRepository, Depends(UserRepository)]):
        self.user_repository = user_repository

    def authenticate_user(self, email: str, password: str) -> User | bool:
        user = self.user_repository.get_by_email(email)
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        if not user.is_active:
            return False
        return user


async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)],
                           user_repository: Annotated[UserRepository, Depends(UserRepository)]) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        token_scopes = payload.get("scopes", [])
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, scopes=token_scopes)
    except InvalidTokenError:
        raise credentials_exception
    user = user_repository.get_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def _action_secret(purpose: str, password_hash: str | None = None) -> str:
    if purpose == "password_reset":
        return f"{settings.SECRET_KEY}:{password_hash}"
    return settings.SECRET_KEY


def create_action_token(purpose: str, user_id: int, email: str, password_hash: str | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"purpose": purpose, "user_id": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, _action_secret(purpose, password_hash), algorithm=ALGORITHM)


def decode_action_token(token: str, purpose: str, password_hash: str | None = None) -> dict:
    try:
        payload = jwt.decode(token, _action_secret(purpose, password_hash), algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    if payload.get("purpose") != purpose:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    return payload
