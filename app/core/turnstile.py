import httpx
from fastapi import HTTPException, status

from app.core.config import settings

TURNSTILE_SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile_token(token: str | None, remote_ip: str | None = None) -> None:
    """Verify a Cloudflare Turnstile token when TURNSTILE_ENABLED is true.

    Skips verification when disabled (local/dev). Rejects missing tokens with 400
    and failed siteverify responses with 403.
    """
    if not settings.TURNSTILE_ENABLED:
        return

    if not token or not str(token).strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Turnstile token required",
        )

    if not settings.TURNSTILE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Turnstile is not configured",
        )

    data = {
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": str(token).strip(),
    }
    if remote_ip and remote_ip != "unknown":
        data["remoteip"] = remote_ip

    try:
        response = httpx.post(TURNSTILE_SITEVERIFY_URL, data=data, timeout=10.0)
        response.raise_for_status()
        result = response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Turnstile verification failed",
        ) from None

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Turnstile verification failed",
        )
