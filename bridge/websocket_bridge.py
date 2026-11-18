"""
WebSocket + REST bridge for JARVIS wake-mode application.

Runs as a background asyncio task inside jarvis_wake.py's own process.
Connects to the existing EventBus, broadcasts live events over WebSockets,
and exposes HTTP endpoints for configuration, tool listing, and permissions.

Security: never logs or returns API keys — uses masked representations only.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── FastAPI / uvicorn (lightweight addition; installs on first run if missing) ──

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse, JSONResponse
except ImportError:
    raise ImportError(
        "fastapi and uvicorn are required for the web frontend. "
        "Install with: .wakevenv\\Scripts\\pip install fastapi uvicorn"
    )

# ── Project modules ────────────────────────────────────────────────────────────

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.jarvis.runtime.event_bus import Event, EventBus, EventType  # noqa: E402
from src.jarvis.permissions.approval_manager import ApprovalManager  # noqa: E402
from src.jarvis.permissions.policy_engine import DEFAULT_POLICIES, PermissionLevel  # noqa: E402
from src.jarvis.tools.tool_registry import create_jarvis_tool_registry  # noqa: E402

logger = logging.getLogger("jarvis.bridge")

# ── Globals ─────────────────────────────────────────────────────────────────────

_event_bus: Optional[EventBus] = None
_lock: Optional[asyncio.Lock] = None


def _get_lock() -> asyncio.Lock:
    """Return a lazily-created lock."""
    global _lock
    if _lock is None:
        _lock = asyncio.Lock()
    return _lock


# ── WebSocket client tracking ─────────────────────────────────────────────────

_clients: Dict[str, WebSocket] = {}


# ── Config store (written to ~/.jarvis/config.json by the GUI) ────────────────

CONFIG_PATH = Path(os.environ.get("USERPROFILE", "~")) / ".jarvis" / "config.json"

_DEFAULT_CONFIG: Dict[str, Any] = {
    "freellmapi_api_key": "",
    "freellmapi_base_url": "https://api.freellmapi.com/v1",
    "freellmapi_model": "kokoro",
    "web_bridge_port": 8765,
}


def _load_config() -> Dict[str, Any]:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return dict(_DEFAULT_CONFIG)


def _save_config(cfg: Dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def _mask_key(key: str) -> str:
    """Return a safely-masked version of an API key for UI display."""
    if not key:
        return ""
    if len(key) <= 8:
        return chr(0x2022) * len(key)
    return key[:4] + chr(0x2022) * (len(key) - 8) + key[-4:]


# ── Live state (populated by event subscriptions) ─────────────────────────────

_live_state: Dict[str, Any] = {
    "jarvis_state": "unknown",
    "connection_status": "disconnected",
    "last_message": "",
    "log_buffer": [],
    "started_at": None,
    # Voice components — updated by SPEECH_STARTING / SPEECH_ENDED / WAKE_WORD_DETECTED
    "is_listening": False,
    "is_speaking": False,
    "wake_word": None,       # last detected wake word, or null
    "integration_status": "unknown",
}


# ── Module-level broadcast helper ──────────────────────────────────────────────
# Used by _on_bus_event (tkinter thread via ensure_future) and by route handlers.

async def _broadcast(payload: dict) -> None:
    """Send payload to every connected WebSocket client."""
    dead: List[str] = []
    for sid, ws in list(_clients.items()):
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(sid)
    for sid in dead:
        _clients.pop(sid, None)


# ── Factory ────────────────────────────────────────────────────────────────────

_last_port_used = [8765]  # mutable so _build_app can report bind port


def _last_port() -> int:
    """Return the port most recently bound by _build_app."""
    return _last_port_used[0]


async def start_bridge(event_bus: EventBus, port: int | None = None) -> None:
    """Entry point for use when an event loop is already running."""
    app = _build_app(event_bus, port)
    import uvicorn as _uvicorn
    config = _uvicorn.Config(app, host="127.0.0.1", port=_last_port(), log_level="warning")
    server = _uvicorn.Server(config)
    await server.serve()


def _build_app(event_bus: EventBus, port: int | None = None) -> FastAPI:
    """Build and return the FastAPI app with all routes registered."""
    global _event_bus
    _event_bus = event_bus

    # Subscribe to every event type the bus publishes
    for evt_type in EventType:
        _event_bus.subscribe(evt_type, lambda e: asyncio.ensure_future(_on_bus_event(e)))

    cfg = _load_config()
    bind_port = port or int(cfg.get("web_bridge_port", 8765))

    app = FastAPI(title="JARVIS Bridge", docs_url="/docs", redoc_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def _on_start():
        logger.info("JARVIS Bridge starting on ws://0.0.0.0:%d", bind_port)
        _live_state["connection_status"] = "listening"
        _live_state["started_at"] = time.time()

    # Serve frontend from same port so open(http://127.0.0.1:8765) works directly
    _frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        return (_frontend_dir / "index.html").read_text(encoding="utf-8")

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": "jarvis-bridge",
            "port": bind_port,
            "timestamp": time.time(),
        }

    @app.get("/state")
    async def get_state():
        return dict(_live_state)

    # ── WebSocket endpoint ───────────────────────────────────────────────────

    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        session_id = str(uuid.uuid4())[:8]
        await ws.accept()
        _clients[session_id] = ws
        await ws.send_json({"type": "snapshot", "data": dict(_live_state)})
        await ws.send_json({
            "type": "connected",
            "session_id": session_id,
            "event_count": len(_live_state.get("log_buffer", [])),
        })
        logger.info("Client connected: %s (%d total)", session_id, len(_clients))
        try:
            while True:
                raw = await ws.receive_text()
                msg = json.loads(raw)
                if msg.get("action") == "ping":
                    await ws.send_json({"type": "pong"})
                else:
                    logger.debug("Received from %s: %s", session_id, msg.get("action"))
        except WebSocketDisconnect:
            pass
        finally:
            _clients.pop(session_id, None)
            logger.info("Client disconnected: %s (%d remaining)", session_id, len(_clients))

    # ── AI Configuration ─────────────────────────────────────────────────────

    @app.get("/config/ai")
    async def get_ai_config():
        cfg = _load_config()
        return {
            "provider": "freellmapi",
            "base_url": cfg.get("freellmapi_base_url", ""),
            "model": cfg.get("freellmapi_model", ""),
            "api_key_masked": _mask_key(cfg.get("freellmapi_api_key", "")),
            "api_key_set": bool(cfg.get("freellmapi_api_key")),
        }

    @app.post("/config/ai")
    async def save_ai_config(body: dict):
        cfg = _load_config()
        cfg["freellmapi_base_url"] = body.get("base_url", cfg.get("freellmapi_base_url", ""))
        cfg["freellmapi_model"] = body.get("model", cfg.get("freellmapi_model", ""))
        api_key = body.get("api_key", "")
        if api_key and api_key != "••••••••":
            cfg["freellmapi_api_key"] = api_key
        elif api_key == "":
            cfg["freellmapi_api_key"] = ""
        _save_config(cfg)
        await _broadcast({"type": "config_updated", "config": await get_ai_config()})
        return {"status": "saved"}

    @app.post("/config/ai/test")
    async def test_ai_config(body: dict):
        """Lightweight test: call the configured endpoint with a short prompt."""
        cfg = _load_config()
        key = body.get("api_key", cfg.get("freellmapi_api_key", ""))
        base_url = body.get("base_url", cfg.get("freellmapi_base_url", ""))
        model = body.get("model", cfg.get("freellmapi_model", "kokoro"))
        if not key:
            return JSONResponse(status_code=400, content={"error": "API key not provided"})
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key, base_url=base_url, timeout=15.0)
            reply = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Reply with exactly: ok"}],
                max_tokens=5,
            )
            response_text = (reply.choices[0].message.content or "").strip()
            success = "ok" in response_text.lower()
            return {"success": success, "response": response_text}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    # ── Tools ────────────────────────────────────────────────────────────────

    @app.get("/tools")
    async def list_tools():
        try:
            reg = create_jarvis_tool_registry()
            categories = reg.list_categories()
            tools_by_cat: Dict[str, List[Dict]] = {}
            for cat in categories:
                tools = [t.to_dict() for t in reg.list_tools(cat)]
                tools_by_cat[cat] = tools
            return {"categories": categories, "tools_by_category": tools_by_cat}
        except Exception as exc:
            return {"error": str(exc), "categories": [], "tools_by_category": {}}

    # ── Permissions ──────────────────────────────────────────────────────────

    _perm_manager = ApprovalManager(timeout=300.0)

    @app.get("/permissions")
    async def get_permissions():
        policies = {}
        for name, pol in DEFAULT_POLICIES.items():
            policies[name] = {
                "tool": pol.tool,
                "level": pol.level.name,
                "level_value": int(pol.level),
                "description": pol.description,
                "requires_confirmation": pol.requires_confirmation,
                "auto_approve": pol.auto_approve,
            }
        pending = [asdict(r) for r in _perm_manager.get_pending()]
        history = [asdict(r) for r in _perm_manager.get_history()[-50:]]
        return {"policies": policies, "pending_requests": pending, "history": history}

    @app.post("/permissions/{request_id}/approve")
    async def approve_request(request_id: str):
        ok = _perm_manager.approve(request_id)
        await _broadcast({"type": "permission_result", "id": request_id, "approved": ok})
        return {"approved": ok}

    @app.post("/permissions/{request_id}/deny")
    async def deny_request(request_id: str):
        ok = _perm_manager.deny(request_id)
        await _broadcast({"type": "permission_result", "id": request_id, "approved": False})
        return {"denied": ok}

    # ── Simulator ─────────────────────────────────────────────────────────────

    @app.post("/simulate/event")
    async def simulate_event(body: dict):
        """Push a synthetic event into the bus for UI testing."""
        evt_type_str = body.get("event", "task.completed")
        try:
            evt_type = EventType(evt_type_str)
        except ValueError:
            return JSONResponse(status_code=400, content={"error": f"Unknown event type: {evt_type_str}"})
        _event_bus.publish_simple(evt_type, data=body.get("data", {}), source="simulator")
        return {"status": "simulated"}

    @app.post("/simulate/state")
    async def simulate_state(body: dict):
        """Directly update the live state displayed in the UI."""
        for k, v in body.items():
            if k in _live_state:
                _live_state[k] = v
        return {"status": "updated"}

    # ── Log reading ──────────────────────────────────────────────────────────

    @app.get("/logs")
    async def get_logs(limit: int = 200):
        buf = list(reversed(_live_state.get("log_buffer", [])))
        return {"logs": buf[:limit]}

    @app.post("/logs/clear")
    async def clear_logs():
        _live_state["log_buffer"] = []
        return {"cleared": True}

    @app.get("/voice/status")
    async def get_voice_status():
        """Return current voice integration state for the Voice Settings page."""
        return {
            "is_listening": _live_state.get("is_listening", False),
            "is_speaking": _live_state.get("is_speaking", False),
            "wake_word": _live_state.get("wake_word"),
            "integration_status": _live_state.get("integration_status", "unknown"),
        }

    _last_port_used[0] = bind_port
    return app


# ── Synchronous entry-point (runs on a background thread inside tkinter) ─────

def start_bridge_sync(event_bus: EventBus, port: int | None = None) -> None:
    """Synchronous wrapper — safe to call from a Tkinter daemon thread.
    Calls _build_app then server.run() directly (no asyncio loop needed).
    shortcut: _build_app also sets _event_bus; callers that need the app itself
    can call _build_app directly instead of going through start_bridge_sync.
    """
    app = _build_app(event_bus, port)
    import uvicorn
    bp = _last_port_used[0]
    config = uvicorn.Config(app, host="127.0.0.1", port=bp, log_level="warning")
    uvicorn.Server(config).run()


# ── EventBus subscriber (runs in async context) ───────────────────────────────

async def _on_bus_event(event: Event) -> None:
    ts = time.strftime("%H:%M:%S", time.localtime(event.timestamp))
    tag = event.type.value
    data = event.data or {}
    src = event.source or "unknown"

    # Keep a rolling buffer (max 500 entries)
    buf = _live_state.setdefault("log_buffer", [])
    buf.append({"time": ts, "tag": tag, "data": data, "source": src})
    if len(buf) > 500:
        _live_state["log_buffer"] = buf = buf[-500:]

    # Map specific event types to live-state fields for quick UI access
    if tag == "wake_word.detected":
        _live_state["jarvis_state"] = "LISTENING"
        _live_state["is_listening"] = True
        _live_state["wake_word"] = data.get("wake_word", "Jarvis")
        last_msg = data.get("wake_word", tag)
    elif tag == "command.transcribed":
        _live_state["jarvis_state"] = "TRANSCRIBED"
        _live_state["is_listening"] = True  # mid-listen while transcribing
        last_msg = data.get("text") or data.get("phrase") or tag
    elif tag == "speech.starting":
        _live_state["jarvis_state"] = "LISTENING"
        _live_state["is_listening"] = True
        _live_state["integration_status"] = "active"
        last_msg = data.get("phrase", "Listening…")
    elif tag == "speech.ended":
        _live_state["jarvis_state"] = "PROCESSING"
        _live_state["is_listening"] = False
        last_msg = data.get("phrase", "")
    else:
        mapping = {
            "startup":              ("jarvis_state", "IDLE"),
            "shutdown":             ("jarvis_state", "SHUTDOWN"),
            "agent.started":        ("jarvis_state", "PROCESSING"),
            "agent.completed":      ("jarvis_state", "IDLE"),
            "agent.failed":         ("jarvis_state", "ERROR"),
            "task.completed":       ("jarvis_state", "TASK_COMPLETED"),
        }
        if tag in mapping:
            key, val = mapping[tag]
            _live_state[key] = val
        last_msg = data.get("text") or data.get("phrase") or data.get("wake_word") or tag
    if 'last_msg' not in locals():
        last_msg = tag
    _live_state["last_message"] = str(last_msg)

    payload = {
        "type": "event",
        "time": ts,
        "tag": tag,
        "data": data,
        "source": src,
    }
    await _broadcast(payload)
