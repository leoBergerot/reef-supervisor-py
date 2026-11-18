"""Resolve FR/EN locale for auth emails."""

from __future__ import annotations

from fastapi import Request

SUPPORTED = frozenset({"fr", "en"})
DEFAULT_LOCALE = "fr"


def normalize_locale(value: str | None) -> str | None:
    if not value:
        return None
    raw = value.strip().lower().replace("_", "-")
    if not raw:
        return None
    primary = raw.split("-", 1)[0]
    if primary in SUPPORTED:
        return primary
    if raw.startswith("fr"):
        return "fr"
    if raw.startswith("en"):
        return "en"
    return None


def locale_from_accept_language(header: str | None) -> str | None:
    if not header:
        return None
    # Take first tag; ignore q-weights for simplicity (FR default covers ambiguity).
    for part in header.split(","):
        tag = part.split(";", 1)[0].strip()
        resolved = normalize_locale(tag)
        if resolved:
            return resolved
    return None


def resolve_locale(
    *,
    body_locale: str | None = None,
    body_lang: str | None = None,
    request: Request | None = None,
) -> str:
    for candidate in (body_locale, body_lang):
        resolved = normalize_locale(candidate)
        if resolved:
            return resolved
    if request is not None:
        resolved = locale_from_accept_language(request.headers.get("accept-language"))
        if resolved:
            return resolved
    return DEFAULT_LOCALE
