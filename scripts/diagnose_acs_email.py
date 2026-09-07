"""Send one ACS test mail using Braelo-V1 app settings. Prints a sanitized error."""

from __future__ import annotations

import json
import os
import subprocess
import sys


APP_NAME = os.getenv("APP_NAME", "Braelo-V1")
TEST_TO = os.getenv("ACS_TEST_TO", "ch1@gmail.com")


def _az(*args: str) -> str:
    result = subprocess.run(
        ["az", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"::error::az {' '.join(args[:4])} failed: {result.stderr.strip()[:400]}")
        sys.exit(1)
    return result.stdout


def main() -> int:
    rg = _az(
        "webapp",
        "list",
        "--query",
        f"[?name=='{APP_NAME}'].resourceGroup | [0]",
        "-o",
        "tsv",
    ).strip()
    if not rg:
        print("::error::Braelo-V1 resource group not found")
        return 1
    print(f"Resource group: {rg}")

    raw = _az(
        "webapp",
        "config",
        "appsettings",
        "list",
        "-n",
        APP_NAME,
        "-g",
        rg,
        "-o",
        "json",
    )
    settings = {item.get("name"): item.get("value") or "" for item in json.loads(raw)}
    names = sorted(
        name
        for name in settings
        if name.startswith(("EMAIL", "ACS_", "AZURE_COMMUNICATION", "SENDGRID"))
    )
    print("Email setting names:", ", ".join(names) or "(none)")
    for name in names:
        print(f"{name} length={len(settings.get(name) or '')}")

    conn = (
        settings.get("AZURE_COMMUNICATION_CONNECTION_STRING")
        or settings.get("COMMUNICATION_SERVICES_CONNECTION_STRING")
        or ""
    ).strip()
    sender = (settings.get("ACS_EMAIL_SENDER") or "").strip()
    if not conn or not sender:
        print("::error::ACS settings missing on Braelo-V1")
        return 1

    try:
        from azure.communication.email import EmailClient
    except Exception as exc:
        print(f"::error::azure-communication-email import failed: {type(exc).__name__}: {exc}")
        return 1

    client = EmailClient.from_connection_string(conn)
    message = {
        "senderAddress": sender,
        "content": {
            "subject": "Braelo email diagnostic",
            "plainText": "ACS diagnostic send from GitHub Actions.",
        },
        "recipients": {"to": [{"address": TEST_TO}]},
    }
    try:
        result = client.begin_send(message).result()
    except Exception as exc:
        text = str(exc)
        for secret in (conn, conn.split("accessKey=")[-1] if "accessKey=" in conn else ""):
            if secret:
                text = text.replace(secret, "***")
        print(f"::error::ACS send failed {type(exc).__name__}: {text[:500]}")
        return 1

    status = getattr(result, "status", None) or (
        result.get("status") if isinstance(result, dict) else result
    )
    print(f"ACS send status={status} sender={sender} to={TEST_TO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
