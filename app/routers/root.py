from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.client_ip import get_client_ip
from app.core.rate_limit import rate_limit_auth
from app.core.security import Auth, Token, create_access_token
from app.core.turnstile import verify_turnstile_token

router = APIRouter(tags=["Authentication"])


@router.post("/token")
async def login_for_access_token(
        request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth: Annotated[Auth, Depends(Auth)],
        turnstileToken: Annotated[str | None, Form()] = None,
        _rate_limit: Annotated[None, Depends(rate_limit_auth)] = None,
) -> Token:
    verify_turnstile_token(turnstileToken, get_client_ip(request))
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"email": user.email, "scopes": user.scopes})
    return Token(access_token=access_token, token_type="bearer")
