"""Gravatar OSINT integration for VulnHunterAI.

Uses the public Gravatar API (no API key needed).
Lookup by email MD5 hash: https://www.gravatar.com/{md5}.json
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def email_to_gravatar_hash(email: str) -> str:
    """Convert email to Gravatar MD5 hash."""
    cleaned = email.strip().lower()
    return hashlib.md5(cleaned.encode()).hexdigest()


def lookup_gravatar(email: str) -> dict[str, Any]:
    """Look up a Gravatar profile by email. No API key needed."""
    if not HAS_HTTPX and not HAS_REQUESTS:
        return {"error": "httpx or requests required"}

    hash_ = email_to_gravatar_hash(email)
    url = f"https://www.gravatar.com/{hash_}.json"

    try:
        if HAS_HTTPX:
            resp = httpx.get(url, timeout=10, follow_redirects=True)
        else:
            resp = requests.get(url, timeout=10, allow_redirects=True)

        if resp.status_code == 200:
            data = resp.json()
            entry = data.get("entry", [{}])[0]
            return {
                "found": True,
                "email": email,
                "hash": hash_,
                "display_name": entry.get("displayName", ""),
                "profile_url": entry.get("profileUrl", ""),
                "thumbnail_url": entry.get("thumbnailUrl", ""),
                "photos": [p.get("value", "") for p in entry.get("photos", [])],
                "accounts": [
                    {"service": a.get("shortname", ""), "url": a.get("url", "")}
                    for a in entry.get("accounts", [])
                ],
                "urls": [u.get("value", "") for u in entry.get("urls", [])],
            }
        elif resp.status_code == 404:
            return {"found": False, "email": email, "hash": hash_}
        else:
            return {"error": f"HTTP {resp.status_code}", "email": email}

    except Exception as e:
        logger.error("gravatar_lookup_error", email=email, error=str(e))
        return {"error": str(e), "email": email}


def batch_lookup(emails: list[str]) -> list[dict[str, Any]]:
    """Look up multiple emails."""
    return [lookup_gravatar(e) for e in emails]


if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else "test@example.com"
    result = lookup_gravatar(email)
    print(json.dumps(result, indent=2))
