"""
Firebase Admin bootstrap.

Azure sometimes stores the service-account JSON as raw JSON, sometimes as
Base64. Accept both so token verification and FCM keep working.
"""

from __future__ import annotations

import base64
import json
import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_FIREBASE_PROJECT_ID = "braelo-app"


def firebase_project_id() -> str:
    return (
        os.getenv("FIREBASE_PROJECT_ID", "").strip()
        or os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
        or DEFAULT_FIREBASE_PROJECT_ID
    )


def parse_firebase_credentials(raw: str) -> dict | None:
    text = (raw or "").strip()
    if not text:
        return None
    if text.startswith("{"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) else None
    try:
        decoded = base64.b64decode(text).decode("utf-8")
        data = json.loads(decoded)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def credentials_from_env() -> dict | None:
    raw = (
        os.getenv("FIREBASE_CREDENTIALS", "").strip()
        or os.getenv("FIREBASE_CREDENTIALS_BASE64", "").strip()
    )
    return parse_firebase_credentials(raw)


def ensure_firebase_app() -> bool:
    try:
        from firebase_admin import credentials, get_app, initialize_app
    except Exception:
        return False

    try:
        get_app()
        return True
    except ValueError:
        pass

    info = credentials_from_env()
    if not info:
        return False

    try:
        initialize_app(credentials.Certificate(info))
        return True
    except Exception as exc:
        logger.warning("Firebase app init failed: %s", exc)
        return False
