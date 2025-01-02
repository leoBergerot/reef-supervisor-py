from passlib.context import CryptContext
from app.core.config import settings
from pydantic import BaseModel
from app.repositories.user_repository import UserRepository
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from app.db.session import get_db
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from app.schemas.user import User
from jwt.exceptions import InvalidTokenError
import jwt

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db, email: str, password: str) -> User | bool:
    user_repository = UserRepository(db)
    user = user_repository.get_by_email(email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: Annotated[Session, Depends(get_db)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user_repository = UserRepository(db)
    user = user_repository.get_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
