from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, Auth, Token
from typing import Annotated

router = APIRouter(tags=["Authentication"])


@router.post("/token", )
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth: Annotated[Auth, Depends(Auth)]
) -> Token:
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"email": user.email, "scopes": user.scopes})
    return Token(access_token=access_token, token_type="bearer")
