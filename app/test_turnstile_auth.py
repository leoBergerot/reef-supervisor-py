from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core import rate_limit as rate_limit_module
from app.core.config import settings
from app.core.turnstile import TURNSTILE_SITEVERIFY_URL
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    rate_limit_module.auth_rate_limiter.reset()
    yield
    rate_limit_module.auth_rate_limiter.reset()


@pytest.fixture
def turnstile_disabled(monkeypatch):
    monkeypatch.setattr(settings, "TURNSTILE_ENABLED", False)
    monkeypatch.setattr(settings, "TURNSTILE_SECRET_KEY", None)


@pytest.fixture
def turnstile_enabled(monkeypatch):
    monkeypatch.setattr(settings, "TURNSTILE_ENABLED", True)
    monkeypatch.setattr(settings, "TURNSTILE_SECRET_KEY", "test-secret")


def test_token_skips_turnstile_when_disabled(turnstile_disabled):
    with (
        patch("app.core.turnstile.httpx.post") as mock_post,
        patch("app.core.security.Auth.authenticate_user", return_value=False),
    ):
        response = client.post(
            "/token",
            data={"username": "nobody@example.com", "password": "x"},
        )
        mock_post.assert_not_called()
    assert response.status_code == 401


def test_users_skips_turnstile_when_disabled(turnstile_disabled):
    with patch("app.core.turnstile.httpx.post") as mock_post:
        # Reach past Turnstile into app logic without requiring a live DB.
        with patch(
            "app.repositories.user_repository.UserRepository.is_email_unique",
            return_value=False,
        ):
            response = client.post(
                "/users",
                json={"email": "turnstile-skip@reefsupervisor.fr", "password": "test"},
            )
        mock_post.assert_not_called()
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_token_rejects_missing_turnstile_when_enabled(turnstile_enabled):
    response = client.post(
        "/token",
        data={"username": "nobody@example.com", "password": "x"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Turnstile token required"


def test_users_rejects_missing_turnstile_when_enabled(turnstile_enabled):
    response = client.post(
        "/users",
        json={"email": "need-token@reefsupervisor.fr", "password": "test"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Turnstile token required"


def test_token_rejects_invalid_turnstile_when_enabled(turnstile_enabled):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"success": False}

    with patch("app.core.turnstile.httpx.post", return_value=mock_response) as mock_post:
        response = client.post(
            "/token",
            data={
                "username": "nobody@example.com",
                "password": "x",
                "turnstileToken": "bad-token",
            },
        )
        mock_post.assert_called_once()
        assert mock_post.call_args.args[0] == TURNSTILE_SITEVERIFY_URL

    assert response.status_code == 403
    assert response.json()["detail"] == "Turnstile verification failed"


def test_users_accepts_valid_turnstile_when_enabled(turnstile_enabled):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"success": True}

    with (
        patch("app.core.turnstile.httpx.post", return_value=mock_response) as mock_post,
        patch(
            "app.repositories.user_repository.UserRepository.is_email_unique",
            return_value=False,
        ),
    ):
        response = client.post(
            "/users",
            json={
                "email": "turnstile-ok@reefsupervisor.fr",
                "password": "test",
                "turnstileToken": "ok-token",
            },
            headers={"CF-Connecting-IP": "203.0.113.10"},
        )
        mock_post.assert_called_once()
        sent = mock_post.call_args.kwargs.get("data") or mock_post.call_args.args[1]
        assert sent["secret"] == "test-secret"
        assert sent["response"] == "ok-token"
        assert sent["remoteip"] == "203.0.113.10"

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_auth_rate_limit_on_token(turnstile_disabled):
    headers = {"CF-Connecting-IP": "198.51.100.99"}
    with patch("app.core.security.Auth.authenticate_user", return_value=False):
        for _ in range(10):
            client.post(
                "/token", headers=headers, data={"username": "a@b.c", "password": "x"}
            )
        response = client.post(
            "/token", headers=headers, data={"username": "a@b.c", "password": "x"}
        )
    assert response.status_code == 429
    assert response.json()["detail"] == "Too many requests"
