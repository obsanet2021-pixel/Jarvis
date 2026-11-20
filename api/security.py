"""
Authentication and security middleware for JARVIS API.
Provides X-Jarvis-Auth validation and per-IP rate limiting.
"""
from __future__ import annotations

import collections
import hmac
import os
import secrets
import time
from pathlib import Path
from typing import Optional
from fastapi import Header, HTTPException, Request

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
ENV_KEY = "JARVIS_API_TOKEN"

def _get_or_create_token() -> str:
    # 1. Check existing environment variable
    token = os.environ.get(ENV_KEY)
    if token:
        return token.strip()

    # 2. Check .env file
    if ENV_PATH.exists():
        try:
            for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
                if line.startswith(f"{ENV_KEY}="):
                    val = line.split("=", 1)[1].strip().strip('"\'')
                    if val:
                        os.environ[ENV_KEY] = val
                        return val
        except Exception:
            pass

    # 3. Generate random token if unset
    new_token = secrets.token_hex(32)
    os.environ[ENV_KEY] = new_token

    # Save to .env (append or update)
    try:
        content = ""
        if ENV_PATH.exists():
            content = ENV_PATH.read_text(encoding="utf-8")

        if ENV_KEY in content:
            lines = []
            for line in content.splitlines():
                if line.startswith(f"{ENV_KEY}="):
                    lines.append(f"{ENV_KEY}={new_token}")
                else:
                    lines.append(line)
            ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            with open(ENV_PATH, "a", encoding="utf-8") as f:
                if content and not content.endswith("\n"):
                    f.write("\n")
                f.write(f"{ENV_KEY}={new_token}\n")
    except Exception:
        pass

    return new_token

# Initialize token on module load (never printed)
JARVIS_API_TOKEN = _get_or_create_token()
# Remove from environment so child processes don't inherit
if ENV_KEY in os.environ:
    del os.environ[ENV_KEY]

# Rate limiting storage: client_ip -> list of timestamps
REQUEST_LIMITS: dict[str, list[float]] = collections.defaultdict(list)
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 10

def check_rate_limit(request: Request) -> None:
    """Record every request (auth-pass or fail) in the per-IP sliding window.

    Auth failures still count against the bucket — standard practice prevents
    an attacker from resetting the count by retrying with different credentials.
    """
    client_ip = request.client.host if request.client else "unknown"
    reqs = REQUEST_LIMITS[client_ip]
    now = time.time()
    while reqs and reqs[0] < now - RATE_LIMIT_WINDOW:
        reqs.pop(0)
    if len(reqs) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    reqs.append(now)


def verify_auth(x_jarvis_auth: Optional[str] = Header(None)) -> str:
    if not x_jarvis_auth:
        raise HTTPException(status_code=401, detail="Missing X-Jarvis-Auth header")
    if not hmac.compare_digest(x_jarvis_auth.strip(), JARVIS_API_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid X-Jarvis-Auth token")
    return "authorized_client"
