"""Delete marketplace listings and related user docs from Braelo-V1 Mongo."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from urllib.parse import quote_plus, unquote, urlsplit, urlencode, urlunsplit, parse_qs


APP_NAME = os.getenv("APP_NAME", "Braelo-V1")

LISTING_COLLECTIONS = (
    "vehicle_listing",
    "real_estate_listing",
    "services_listing",
    "events_listing",
    "jobs_listing",
    "electronics_listing",
    "furniture_listing",
    "fashion_listing",
    "kids_listing",
    "sports_hobby_listing",
    "listsync",
    "saved_listings",
)

USER_COLLECTIONS = (
    "interests",
    "device_token",
    "business_listings",
    "business_settings",
    "business_analytics_events",
)


def _az(*args: str) -> str:
    result = subprocess.run(
        ["az", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"::error::az failed: {result.stderr.strip()[:400]}")
        sys.exit(1)
    return result.stdout


def _normalize_uri(uri: str) -> str:
    uri = (uri or "").strip()
    if not uri or "://" not in uri:
        return uri
    try:
        scheme, rest = uri.split("://", 1)
        if scheme not in ("mongodb", "mongodb+srv") or "@" not in rest:
            return uri
        authority, hostpath = rest.split("@", 1)
        if ":" not in authority:
            return uri
        colon = authority.index(":")
        user_raw = unquote(authority[:colon])
        pass_raw = unquote(authority[colon + 1 :])
        if not user_raw:
            return uri
        return (
            f"{scheme}://{quote_plus(user_raw, safe='')}:"
            f"{quote_plus(pass_raw, safe='')}@{hostpath}"
        )
    except Exception:
        return uri


def _with_auth_source(uri: str) -> str:
    try:
        parsed = urlsplit(uri)
        query = parse_qs(parsed.query, keep_blank_values=True)
        if not any(key.lower() == "authsource" for key in query):
            query["authSource"] = ["admin"]
        return urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path, urlencode(query, doseq=True), parsed.fragment)
        )
    except Exception:
        return uri


def _resolve_uri(settings: dict[str, str]) -> tuple[str, str]:
    db_name = (settings.get("MONGO_DB_NAME") or "braelo").strip() or "braelo"
    uri = (
        settings.get("MONGO_URI")
        or settings.get("CUSTOMCONNSTR_MONGO_URI")
        or settings.get("MONGODB_URI")
        or settings.get("MONGO_URL")
        or ""
    ).strip()
    if not uri:
        user = (settings.get("MONGO_USERNAME") or "").strip()
        password = (settings.get("MONGO_PASSWORD") or "").strip()
        host = (settings.get("MONGO_ATLAS_HOST") or "").strip()
        if user and password and host:
            uri = (
                f"mongodb+srv://{quote_plus(user)}:{quote_plus(password)}"
                f"@{host}/{db_name}?retryWrites=true&w=majority"
            )
    return _with_auth_source(_normalize_uri(uri)), db_name


def _counts(db, names: tuple[str, ...]) -> dict[str, int]:
    return {name: int(db[name].estimated_document_count()) for name in names}


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
    uri, db_name = _resolve_uri(settings)
    if not uri:
        print("::error::MONGO_URI missing on Braelo-V1")
        return 1

    from pymongo import MongoClient

    client = MongoClient(uri, serverSelectionTimeoutMS=15000)
    client.admin.command("ping")
    db = client[db_name]

    listing_before = _counts(db, LISTING_COLLECTIONS)
    user_before = _counts(db, USER_COLLECTIONS)
    mirror_before = db["businesses"].count_documents({"listing_source": {"$exists": True}})
    print("Before listings:", json.dumps(listing_before))
    print("Before user docs:", json.dumps(user_before))
    print(f"Before listing mirrors in businesses: {mirror_before}")

    deleted = {}
    for name in LISTING_COLLECTIONS:
        deleted[name] = db[name].delete_many({}).deleted_count
    for name in USER_COLLECTIONS:
        deleted[name] = db[name].delete_many({}).deleted_count
    deleted["businesses_listing_mirrors"] = db["businesses"].delete_many(
        {"listing_source": {"$exists": True}}
    ).deleted_count

    listing_after = _counts(db, LISTING_COLLECTIONS)
    user_after = _counts(db, USER_COLLECTIONS)
    mirror_after = db["businesses"].count_documents({"listing_source": {"$exists": True}})
    print("Deleted:", json.dumps(deleted))
    print("After listings:", json.dumps(listing_after))
    print("After user docs:", json.dumps(user_after))
    print(f"After listing mirrors in businesses: {mirror_after}")
    print("::notice::Mongo listings and related user documents deleted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
