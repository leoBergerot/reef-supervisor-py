import pytest

from app.core import rate_limit as rate_limit_module


@pytest.fixture(autouse=True)
def reset_auth_rate_limiter():
    rate_limit_module.auth_rate_limiter.reset()
    yield
    rate_limit_module.auth_rate_limiter.reset()


@pytest.fixture(autouse=True)
def capture_auth_emails(monkeypatch):
    """Prevent real SMTP/Mailjet calls; record activation and reset payloads."""
    sent = {"activation": [], "reset": []}

    def fake_activation(_sender, *, email, token, locale=None):
        sent["activation"].append({"email": email, "token": token, "locale": locale})

    def fake_reset(_sender, *, email, user_id, token, locale=None):
        sent["reset"].append(
            {"email": email, "user_id": user_id, "token": token, "locale": locale}
        )

    monkeypatch.setattr(
        "app.routers.users.send_account_activation_email", fake_activation
    )
    monkeypatch.setattr(
        "app.routers.account.send_account_activation_email", fake_activation
    )
    monkeypatch.setattr(
        "app.routers.account.send_password_reset_email", fake_reset
    )
    return sent
