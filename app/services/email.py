"""Outbound email: Mailjet (prod) or SMTP (Maildev / local)."""

from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage as StdEmailMessage
from typing import Protocol
from urllib.parse import quote

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.services.email_templates import (
    render_activation_email,
    render_password_reset_email,
)
from app.services.locale import DEFAULT_LOCALE, normalize_locale

logger = logging.getLogger(__name__)

MAILJET_SEND_URL = "https://api.mailjet.com/v3.1/send"


@dataclass(frozen=True)
class EmailMessage:
    to_email: str
    subject: str
    html: str
    text: str = ""
    to_name: str | None = None


class EmailSender(Protocol):
    def send(self, message: EmailMessage) -> None: ...


class MailjetEmailSender:
    def __init__(self, api_key: str, api_secret: str, from_email: str, from_name: str) -> None:
        self._api_key = api_key
        self._api_secret = api_secret
        self._from_email = from_email
        self._from_name = from_name

    def send(self, message: EmailMessage) -> None:
        part: dict = {
            "From": {"Email": self._from_email, "Name": self._from_name},
            "To": [
                {
                    "Email": message.to_email,
                    "Name": message.to_name or message.to_email,
                }
            ],
            "Subject": message.subject,
            "HTMLPart": message.html,
        }
        if message.text:
            part["TextPart"] = message.text
        payload = {"Messages": [part]}
        try:
            response = httpx.post(
                MAILJET_SEND_URL,
                json=payload,
                auth=(self._api_key, self._api_secret),
                timeout=15.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("Mailjet send failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to send email",
            ) from exc


class SmtpEmailSender:
    def __init__(
        self,
        host: str,
        port: int,
        from_email: str,
        from_name: str,
        *,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = False,
    ) -> None:
        self._host = host
        self._port = port
        self._from_email = from_email
        self._from_name = from_name
        self._username = username
        self._password = password
        self._use_tls = use_tls

    def send(self, message: EmailMessage) -> None:
        mail = StdEmailMessage()
        mail["Subject"] = message.subject
        mail["From"] = f"{self._from_name} <{self._from_email}>"
        mail["To"] = message.to_email
        if message.text:
            mail.set_content(message.text)
            mail.add_alternative(message.html, subtype="html")
        else:
            mail.set_content(message.html, subtype="html")
        try:
            with smtplib.SMTP(self._host, self._port, timeout=15) as smtp:
                if self._use_tls:
                    smtp.starttls()
                if self._username and self._password:
                    smtp.login(self._username, self._password)
                smtp.send_message(mail)
        except OSError as exc:
            logger.exception("SMTP send failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to send email",
            ) from exc


def resolve_mail_driver() -> str:
    driver = (settings.MAIL_DRIVER or "auto").strip().lower()
    if driver in {"mailjet", "smtp"}:
        return driver
    if settings.MAILJET_API_KEY and settings.MAILJET_API_SECRET:
        return "mailjet"
    return "smtp"


def get_email_sender() -> EmailSender:
    driver = resolve_mail_driver()
    if driver == "mailjet":
        if not settings.MAILJET_API_KEY or not settings.MAILJET_API_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Mailjet is not configured",
            )
        return MailjetEmailSender(
            settings.MAILJET_API_KEY,
            settings.MAILJET_API_SECRET,
            settings.EMAIL_FROM,
            settings.EMAIL_FROM_NAME,
        )
    return SmtpEmailSender(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        settings.EMAIL_FROM,
        settings.EMAIL_FROM_NAME,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
        use_tls=settings.SMTP_USE_TLS,
    )


def frontend_base_url() -> str:
    return settings.FRONTEND_BASE_URL.rstrip("/")


def password_reset_link(user_id: int, token: str) -> str:
    return f"{frontend_base_url()}/recover-password/{user_id}/{quote(token, safe='')}"


def account_activation_link(token: str) -> str:
    return f"{frontend_base_url()}/login/{quote(token, safe='')}"


def _locale(locale: str | None) -> str:
    return normalize_locale(locale) or DEFAULT_LOCALE


def send_password_reset_email(
    sender: EmailSender,
    *,
    email: str,
    user_id: int,
    token: str,
    locale: str | None = None,
) -> None:
    link = password_reset_link(user_id, token)
    rendered = render_password_reset_email(locale=_locale(locale), action_url=link)
    sender.send(
        EmailMessage(
            to_email=email,
            subject=rendered.subject,
            html=rendered.html,
            text=rendered.text,
        )
    )


def send_account_activation_email(
    sender: EmailSender,
    *,
    email: str,
    token: str,
    locale: str | None = None,
) -> None:
    link = account_activation_link(token)
    rendered = render_activation_email(locale=_locale(locale), action_url=link)
    sender.send(
        EmailMessage(
            to_email=email,
            subject=rendered.subject,
            html=rendered.html,
            text=rendered.text,
        )
    )
