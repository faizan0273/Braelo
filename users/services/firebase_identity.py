"""
Server-side Firebase identity verification.

Never trust a client-supplied phone number or social ID. Extract the verified
identity from a Firebase ID token after signature verification.
"""

from __future__ import annotations

import logging

from rest_framework.exceptions import ValidationError

from config.firebase_admin_init import ensure_firebase_app, firebase_project_id

logger = logging.getLogger(__name__)

_CLOCK_SKEW_SECONDS = 60


def verify_firebase_id_token(id_token: str) -> dict:
    token = (id_token or "").strip()
    if not token:
        raise ValidationError({"id_token": "Firebase ID token is required."})

    ensure_firebase_app()

    admin_error = _verify_with_firebase_admin(token)
    if isinstance(admin_error, dict):
        return admin_error

    google_claims = _verify_with_google_auth(token)
    if isinstance(google_claims, dict):
        return google_claims

    if admin_error is not None:
        logger.warning("Firebase token verification failed: %s", admin_error)
    raise ValidationError({"id_token": "Invalid Firebase token."})


def _raise_if_known_token_error(exc: Exception) -> None:
    name = type(exc).__name__
    if name in ("ExpiredIdTokenError",):
        raise ValidationError(
            {"id_token": "Firebase token has expired. Please verify again."}
        ) from exc
    if name in ("RevokedIdTokenError",):
        raise ValidationError(
            {"id_token": "Firebase token has been revoked. Please verify again."}
        ) from exc


def _verify_with_firebase_admin(token: str) -> dict | Exception | None:
    try:
        from firebase_admin import auth as firebase_auth
    except Exception as exc:  # pragma: no cover - import environment
        logger.warning("firebase_admin.auth unavailable: %s", exc)
        return exc

    try:
        try:
            return firebase_auth.verify_id_token(
                token, clock_skew_seconds=_CLOCK_SKEW_SECONDS
            )
        except TypeError:
            return firebase_auth.verify_id_token(token)
    except Exception as exc:
        _raise_if_known_token_error(exc)
        logger.warning(
            "firebase_admin.verify_id_token failed (%s): %s",
            type(exc).__name__,
            exc,
        )
        return exc


def _verify_with_google_auth(token: str) -> dict | None:
    """
    Verify a Firebase ID token with Google's public keys.

    This does not need a service-account JSON, so Google/Apple/phone login
    still works when FIREBASE_CREDENTIALS is missing or not Base64 on Azure.
    """
    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token as google_id_token
    except Exception as exc:  # pragma: no cover - import environment
        logger.warning("google.oauth2 id_token verify unavailable: %s", exc)
        return None

    audience = firebase_project_id()
    request = google_requests.Request()
    try:
        try:
            claims = google_id_token.verify_firebase_token(
                token,
                request,
                audience=audience,
                clock_skew_in_seconds=_CLOCK_SKEW_SECONDS,
            )
        except TypeError:
            claims = google_id_token.verify_firebase_token(
                token,
                request,
                audience=audience,
            )
    except Exception as exc:
        logger.warning(
            "google.oauth2.verify_firebase_token failed (%s): %s",
            type(exc).__name__,
            exc,
        )
        return None

    if not isinstance(claims, dict):
        return None
    # firebase_admin copies sub → uid; google-auth returns JWT claims as-is.
    if not str(claims.get("uid") or "").strip() and claims.get("sub"):
        claims["uid"] = claims["sub"]
    return claims


def phone_from_firebase_claims(claims: dict) -> str:
    phone = str((claims or {}).get("phone_number") or "").strip()
    if not phone:
        raise ValidationError(
            {
                "id_token": (
                    "Firebase token does not contain a verified phone number."
                )
            }
        )
    return phone


def email_from_firebase_claims(claims: dict) -> str:
    email = str((claims or {}).get("email") or "").strip().lower()
    if not email:
        raise ValidationError(
            {
                "id_token": (
                    "Firebase token does not contain a verified email address."
                )
            }
        )
    return email


def uid_from_firebase_claims(claims: dict) -> str:
    payload = claims or {}
    uid = str(
        payload.get("uid") or payload.get("sub") or payload.get("user_id") or ""
    ).strip()
    if not uid:
        raise ValidationError(
            {"id_token": "Firebase token does not contain a user id."}
        )
    return uid


def name_parts_from_firebase_claims(claims: dict) -> tuple[str, str, str]:
    payload = claims or {}
    full = str(payload.get("name") or "").strip()
    first = str(payload.get("given_name") or "").strip()
    last = str(payload.get("family_name") or "").strip()
    if not full and (first or last):
        full = f"{first} {last}".strip()
    if not first and full:
        parts = full.split()
        first = parts[0]
        last = " ".join(parts[1:]) if len(parts) > 1 else last
    return full, first, last


def sign_in_provider(claims: dict) -> str:
    firebase = (claims or {}).get("firebase") or {}
    return str(firebase.get("sign_in_provider") or "").strip()


def extract_id_token(data: dict | None) -> str:
    payload = data or {}
    for key in ("id_token", "firebase_id_token", "firebase_token"):
        value = payload.get(key)
        if value:
            return str(value).strip()
    return ""
