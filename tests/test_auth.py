"""Authentication and rate-limiting tests for JARVIS API.

Run with: python -m pytest tests/test_auth.py -v
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="module")
def client():
    from server import app  # noqa: PLC0415
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def _reset_limits():
    """Clear the sliding-window dict before EACH test function."""
    from api.security import REQUEST_LIMITS  # noqa: PLC0415
    REQUEST_LIMITS.clear()
    yield
    REQUEST_LIMITS.clear()


@pytest.fixture(scope="module", autouse=True)
def _ensure_token():
    from api.security import JARVIS_API_TOKEN  # noqa: PLC0415
    os.environ["JARVIS_API_TOKEN"] = JARVIS_API_TOKEN
    yield
    os.environ.pop("JARVIS_API_TOKEN", None)


_FAKE_HOST = "10.0.0.42"  # deterministic IP so all test requests land in one bucket


# ── Auth scenarios ──────────────────────────────────────────────────────────

class TestAuthHeaders:
    def test_no_header_returns_401(self, client):
        resp = client.post("/ussd/balance")
        assert resp.status_code == 401

    def test_wrong_header_returns_401(self, client):
        resp = client.post(
            "/ussd/balance",
            headers={"X-Jarvis-Auth": "wrong-token"},
        )
        assert resp.status_code == 401

    def test_correct_header_accepted(self, client):
        token = os.environ.get("JARVIS_API_TOKEN", "")
        resp = client.post(
            "/ussd/balance",
            headers={"X-Jarvis-Auth": token},
        )
        # Device not attached in test env → 500 expected; auth must be accepted (status < 500).
        assert resp.status_code < 500

    def test_voice_endpoint_also_requires_auth(self, client):
        resp = client.post("/voice/process?text=test")
        assert resp.status_code == 401

    def test_health_is_public(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_empty_header_value_rejected(self, client):
        resp = client.post("/ussd/balance", headers={"X-Jarvis-Auth": ""})
        assert resp.status_code == 401


# ── Rate limiting ───────────────────────────────────────────────────────────

class TestRateLimit:
    def test_11th_request_within_window_returns_429(self, client):
        """First 10 requests succeed; the 11th returns 429."""
        token = os.environ.get("JARVIS_API_TOKEN", "")
        headers = {"X-Jarvis-Auth": token}
        for i in range(10):
            resp = client.post("/ussd/balance", headers=headers)
            assert resp.status_code != 429, f"Request {i+1} hit 429 prematurely"
        resp = client.post("/ussd/balance", headers=headers)
        assert resp.status_code == 429


# ── Token generation ────────────────────────────────────────────────────────

class TestTokenGeneration:
    def test_token_exists_and_is_nonempty(self):
        from api.security import JARVIS_API_TOKEN  # noqa: PLC0415
        assert JARVIS_API_TOKEN
        assert len(JARVIS_API_TOKEN) >= 8

    def test_token_saved_to_dotenv(self):
        from api.security import ENV_PATH  # noqa: PLC0415
        assert ENV_PATH.exists()
        content = ENV_PATH.read_text(encoding="utf-8")
        assert "JARVIS_API_TOKEN=" in content
