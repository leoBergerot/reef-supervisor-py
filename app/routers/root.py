from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.db.session import get_db
from app.core.security import authenticate_user, create_access_token, Token
from typing import Annotated
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.post("/token", )
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"email": user.email})
    return Token(access_token=access_token, token_type="bearer")
