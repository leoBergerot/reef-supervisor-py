import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.core.client_ip import get_client_ip


class InMemoryRateLimiter:
    """Simple sliding-window rate limiter (suitable for a single API instance)."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.monotonic()
        window_start = now - self.window_seconds
        hits = self._hits[key]
        while hits and hits[0] <= window_start:
            hits.popleft()
        if len(hits) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
            )
        hits.append(now)

    def reset(self) -> None:
        self._hits.clear()


auth_rate_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)


def rate_limit_auth(request: Request) -> None:
    """~10 requests per minute per client IP on auth endpoints."""
    auth_rate_limiter.check(get_client_ip(request))
