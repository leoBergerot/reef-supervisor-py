from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core import rate_limit as rate_limit_module
from app.core.config import settings
from app.db.session import engine
from app.main import app
from app.schemas import User
from app.services.email import (
    MAILJET_SEND_URL,
    MailjetEmailSender,
    SmtpEmailSender,
    account_activation_link,
    password_reset_link,
    resolve_mail_driver,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    rate_limit_module.auth_rate_limiter.reset()
    yield
    rate_limit_module.auth_rate_limiter.reset()


def _email() -> str:
    return f"mail-{uuid4().hex}@reefsupervisor.fr"


def _activate(email: str) -> None:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).one()
        user.is_active = True
        session.add(user)
        session.commit()


def test_resolve_mail_driver_auto(monkeypatch):
    monkeypatch.setattr(settings, "MAIL_DRIVER", "auto")
    monkeypatch.setattr(settings, "MAILJET_API_KEY", "key")
    monkeypatch.setattr(settings, "MAILJET_API_SECRET", "secret")
    assert resolve_mail_driver() == "mailjet"
    monkeypatch.setattr(settings, "MAILJET_API_KEY", None)
    monkeypatch.setattr(settings, "MAILJET_API_SECRET", None)
    assert resolve_mail_driver() == "smtp"


def test_mailjet_sender_posts_v31_payload(monkeypatch):
    monkeypatch.setattr(settings, "EMAIL_FROM", "contact@reef-supervisor.fr")
    sender = MailjetEmailSender("key", "secret", "contact@reef-supervisor.fr", "Reef Supervisor")
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    with patch("app.services.email.httpx.post", return_value=mock_response) as mock_post:
        from app.services.email import EmailMessage

        sender.send(
            EmailMessage(
                to_email="user@example.com",
                subject="Hello",
                html="<p>Hi</p>",
                to_name="User",
            )
        )
    mock_post.assert_called_once()
    assert mock_post.call_args.args[0] == MAILJET_SEND_URL
    assert mock_post.call_args.kwargs["auth"] == ("key", "secret")
    body = mock_post.call_args.kwargs["json"]
    assert body["Messages"][0]["From"]["Email"] == "contact@reef-supervisor.fr"
    assert body["Messages"][0]["To"][0]["Email"] == "user@example.com"


def test_smtp_sender_uses_host_port():
    sender = SmtpEmailSender("maildev", 1025, "contact@reef-supervisor.fr", "Reef Supervisor")
    with patch("app.services.email.smtplib.SMTP") as mock_smtp:
        instance = mock_smtp.return_value.__enter__.return_value
        from app.services.email import EmailMessage

        sender.send(
            EmailMessage(to_email="user@example.com", subject="Hello", html="<p>Hi</p>")
        )
        mock_smtp.assert_called_once_with("maildev", 1025, timeout=15)
        instance.send_message.assert_called_once()


def test_link_builders(monkeypatch):
    monkeypatch.setattr(settings, "FRONTEND_BASE_URL", "https://app.example.com/")
    assert password_reset_link(9, "a.b.c") == (
        "https://app.example.com/recover-password/9/a.b.c"
    )
    assert account_activation_link("tok.en") == "https://app.example.com/login/tok.en"


def test_forgot_password_happy_path_and_non_enumeration(capture_auth_emails):
    email = _email()
    created = client.post("/users", json={"email": email, "password": "test"})
    assert created.status_code == 200
    assert "token" not in created.json()
    _activate(email)
    capture_auth_emails["reset"].clear()

    unknown = client.post("/forgot-password", json={"email": "nobody@reefsupervisor.fr"})
    known = client.post("/forgot-password", json={"email": email})
    assert unknown.status_code == 200
    assert known.status_code == 200
    assert unknown.json() == known.json()
    assert "token" not in known.json()
    assert "id" not in known.json()
    assert len(capture_auth_emails["reset"]) == 1
    payload = capture_auth_emails["reset"][0]

    recovered = client.post(
        "/recover-password",
        json={
            "id": payload["user_id"],
            "token": payload["token"],
            "password": "newpass1",
        },
    )
    assert recovered.status_code == 200
    assert recovered.json()["email"] == email
    assert "token" not in recovered.json()
    login = client.post("/token", data={"username": email, "password": "newpass1"})
    assert login.status_code == 200


def test_register_sends_activation_email_without_token(capture_auth_emails):
    email = _email()
    capture_auth_emails["activation"].clear()
    response = client.post("/users", json={"email": email, "password": "test"})
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == email
    assert "token" not in body
    assert len(capture_auth_emails["activation"]) == 1
    assert capture_auth_emails["activation"][0]["locale"] == "fr"
    token = capture_auth_emails["activation"][0]["token"]
    assert client.post("/token", data={"username": email, "password": "test"}).status_code == 401
    confirmed = client.post("/account-activations/confirm", json={"token": token})
    assert confirmed.status_code == 200
    assert client.post("/token", data={"username": email, "password": "test"}).status_code == 200


def test_register_respects_locale_body_field(capture_auth_emails):
    email = _email()
    capture_auth_emails["activation"].clear()
    response = client.post(
        "/users",
        json={"email": email, "password": "test", "locale": "en"},
    )
    assert response.status_code == 200
    assert len(capture_auth_emails["activation"]) == 1
    assert capture_auth_emails["activation"][0]["locale"] == "en"


def test_register_respects_accept_language(capture_auth_emails):
    email = _email()
    capture_auth_emails["activation"].clear()
    response = client.post(
        "/users",
        json={"email": email, "password": "test"},
        headers={"Accept-Language": "en-US,en;q=0.9"},
    )
    assert response.status_code == 200
    assert capture_auth_emails["activation"][0]["locale"] == "en"


def test_forgot_password_respects_lang_alias(capture_auth_emails):
    email = _email()
    created = client.post("/users", json={"email": email, "password": "test"})
    assert created.status_code == 200
    _activate(email)
    capture_auth_emails["reset"].clear()
    response = client.post(
        "/forgot-password",
        json={"email": email, "lang": "en"},
    )
    assert response.status_code == 200
    assert len(capture_auth_emails["reset"]) == 1
    assert capture_auth_emails["reset"][0]["locale"] == "en"


def test_activation_templates_fr_en_include_cta_and_text():
    from app.services.email_templates import (
        render_activation_email,
        render_password_reset_email,
    )

    fr = render_activation_email(
        locale="fr", action_url="https://app.example.com/login/tok"
    )
    en = render_activation_email(
        locale="en", action_url="https://app.example.com/login/tok"
    )
    assert "Activez" in fr.subject
    assert "Activer mon compte" in fr.html
    assert "https://app.example.com/login/tok" in fr.text
    assert "Enable your account" in en.subject
    assert "Enable my account" in en.html
    assert "Reef Supervisor" in fr.html and "Reef Supervisor" in en.html

    reset = render_password_reset_email(
        locale="fr", action_url="https://app.example.com/recover-password/1/tok"
    )
    assert "Réinitialisation" in reset.subject
    assert "Réinitialiser mon mot de passe" in reset.html
    assert "https://app.example.com/recover-password/1/tok" in reset.text


def test_mailjet_includes_text_part(monkeypatch):
    monkeypatch.setattr(settings, "EMAIL_FROM", "contact@reef-supervisor.fr")
    sender = MailjetEmailSender("key", "secret", "contact@reef-supervisor.fr", "Reef Supervisor")
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    with patch("app.services.email.httpx.post", return_value=mock_response) as mock_post:
        from app.services.email import EmailMessage

        sender.send(
            EmailMessage(
                to_email="user@example.com",
                subject="Hello",
                html="<p>Hi</p>",
                text="Hi",
            )
        )
    body = mock_post.call_args.kwargs["json"]
    assert body["Messages"][0]["TextPart"] == "Hi"
    assert body["Messages"][0]["HTMLPart"] == "<p>Hi</p>"


def test_forgot_and_recover_require_turnstile_when_enabled(monkeypatch):
    monkeypatch.setattr(settings, "TURNSTILE_ENABLED", True)
    monkeypatch.setattr(settings, "TURNSTILE_SECRET_KEY", "test-secret")
    forgot = client.post("/forgot-password", json={"email": "a@b.c"})
    assert forgot.status_code == 400
    assert forgot.json()["detail"] == "Turnstile token required"
    recover = client.post(
        "/recover-password",
        json={"id": 1, "token": "x", "password": "newpass1"},
    )
    assert recover.status_code == 400
    assert recover.json()["detail"] == "Turnstile token required"
