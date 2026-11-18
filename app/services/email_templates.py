"""HTML + plain-text auth email templates (FR/EN) for Reef Supervisor."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

BRAND = "Reef Supervisor"
ACCENT = "#0f766e"  # teal — light product branding, not purple/glow
INK = "#0f172a"
MUTED = "#475569"
BG = "#f1f5f9"
CARD = "#ffffff"


@dataclass(frozen=True)
class RenderedEmail:
    subject: str
    html: str
    text: str


_COPY = {
    "fr": {
        "activation": {
            "subject": f"{BRAND} — Activez votre compte",
            "preheader": "Un clic pour activer votre compte Reef Supervisor.",
            "title": "Activez votre compte",
            "body": (
                "Bienvenue sur Reef Supervisor. Pour activer votre compte et commencer "
                "à suivre vos paramètres d’aquarium, cliquez sur le bouton ci-dessous."
            ),
            "cta": "Activer mon compte",
            "fallback": "Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :",
            "ignore": "Si vous n’avez pas créé de compte, vous pouvez ignorer cet e-mail.",
        },
        "password_reset": {
            "subject": f"{BRAND} — Réinitialisation du mot de passe",
            "preheader": "Réinitialisez votre mot de passe Reef Supervisor.",
            "title": "Réinitialiser le mot de passe",
            "body": (
                "Une demande de réinitialisation de mot de passe a été faite pour votre compte. "
                "Cliquez sur le bouton ci-dessous pour en choisir un nouveau."
            ),
            "cta": "Réinitialiser mon mot de passe",
            "fallback": "Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :",
            "ignore": "Si vous n’êtes pas à l’origine de cette demande, ignorez cet e-mail.",
        },
    },
    "en": {
        "activation": {
            "subject": f"{BRAND} — Enable your account",
            "preheader": "One click to activate your Reef Supervisor account.",
            "title": "Enable your account",
            "body": (
                "Welcome to Reef Supervisor. To enable your account and start tracking "
                "your aquarium parameters, click the button below."
            ),
            "cta": "Enable my account",
            "fallback": "If the button does not work, copy this link into your browser:",
            "ignore": "If you did not create an account, you can ignore this email.",
        },
        "password_reset": {
            "subject": f"{BRAND} — Password reset",
            "preheader": "Reset your Reef Supervisor password.",
            "title": "Reset your password",
            "body": (
                "A password reset was requested for your account. "
                "Click the button below to choose a new password."
            ),
            "cta": "Reset my password",
            "fallback": "If the button does not work, copy this link into your browser:",
            "ignore": "If you did not request this, you can ignore this email.",
        },
    },
}


def _shell(*, locale: str, kind: str, action_url: str) -> RenderedEmail:
    copy = _COPY[locale if locale in _COPY else "fr"][kind]
    safe_url = escape(action_url, quote=True)
    safe_url_attr = escape(action_url, quote=True)
    brand = escape(BRAND)
    title = escape(copy["title"])
    body = escape(copy["body"])
    cta = escape(copy["cta"])
    fallback = escape(copy["fallback"])
    ignore = escape(copy["ignore"])
    preheader = escape(copy["preheader"])

    html = f"""<!DOCTYPE html>
<html lang="{escape(locale)}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(copy["subject"])}</title>
</head>
<body style="margin:0;padding:0;background:{BG};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:{INK};">
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;">{preheader}</div>
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:{BG};padding:32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background:{CARD};border-radius:12px;overflow:hidden;border:1px solid #e2e8f0;">
          <tr>
            <td style="background:{ACCENT};padding:20px 28px;">
              <p style="margin:0;font-size:18px;font-weight:700;letter-spacing:0.02em;color:#ffffff;">{brand}</p>
            </td>
          </tr>
          <tr>
            <td style="padding:28px;">
              <h1 style="margin:0 0 12px;font-size:22px;line-height:1.3;color:{INK};">{title}</h1>
              <p style="margin:0 0 24px;font-size:15px;line-height:1.55;color:{MUTED};">{body}</p>
              <table role="presentation" cellspacing="0" cellpadding="0" style="margin:0 0 24px;">
                <tr>
                  <td style="border-radius:8px;background:{ACCENT};">
                    <a href="{safe_url_attr}" style="display:inline-block;padding:12px 22px;font-size:15px;font-weight:600;color:#ffffff;text-decoration:none;">{cta}</a>
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 8px;font-size:13px;line-height:1.5;color:{MUTED};">{fallback}</p>
              <p style="margin:0 0 24px;font-size:12px;line-height:1.5;word-break:break-all;">
                <a href="{safe_url_attr}" style="color:{ACCENT};">{safe_url}</a>
              </p>
              <p style="margin:0;font-size:13px;line-height:1.5;color:{MUTED};">{ignore}</p>
            </td>
          </tr>
          <tr>
            <td style="padding:16px 28px 22px;border-top:1px solid #e2e8f0;">
              <p style="margin:0;font-size:12px;color:#94a3b8;">{brand}</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    text = "\n".join(
        [
            BRAND,
            "",
            copy["title"],
            "",
            copy["body"],
            "",
            f"{copy['cta']}: {action_url}",
            "",
            copy["ignore"],
        ]
    )
    return RenderedEmail(subject=copy["subject"], html=html, text=text)


def render_activation_email(*, locale: str, action_url: str) -> RenderedEmail:
    return _shell(locale=locale, kind="activation", action_url=action_url)


def render_password_reset_email(*, locale: str, action_url: str) -> RenderedEmail:
    return _shell(locale=locale, kind="password_reset", action_url=action_url)
