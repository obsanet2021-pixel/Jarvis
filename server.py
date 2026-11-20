"""JARVIS FastAPI backend — replaces Electron main process."""
from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from google.cloud import firestore as firestore_mod

# ── Auth + rate limiting (api/security.py) ──────────────────────────────────
from api.security import check_rate_limit, verify_auth

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent                # C:\Users\…\Jarvis
DIST = ROOT / "jarvis-electron" / "dist"             # Vite-built frontend
CONFIG = ROOT / ".jarvis_config.json"                # Server-side persistent config

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("jarvis")

# ── Config helpers (replaces Electron userData storage) ───────────────────────
def _load_config() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_config(cfg: dict) -> None:
    CONFIG.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

def _get_firebase_cfg() -> dict | None:
    return _load_config().get("firebase")   # {projectId, clientEmail, privateKey, …}

# ── Firebase (lazy-init, mirrors karionBridge.ts logic) ──────────────────────
_admin_app: Any = None
_db: Any = None
_key_buf: bytes | None = None


def _ensure_admin(firebase_cfg: dict) -> None:
    global _admin_app, _db
    if _admin_app is not None:
        return
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError as exc:
        raise RuntimeError("firebase-admin not installed — pip install firebase-admin") from exc

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": firebase_cfg.get("projectId", ""),
        "private_key": firebase_cfg.get("privateKey", ""),
        "client_email": firebase_cfg.get("clientEmail", ""),
    })
    _admin_app = firebase_admin.initialize_app(cred)
    _db = firestore_mod.client()
    log.info("Firebase Admin initialised for %s", firebase_cfg.get("projectId"))


def get_db(firebase_cfg: dict | None = None) -> Any:
    global _db, _admin_app
    cfg = firebase_cfg or _get_firebase_cfg()
    if cfg is None:
        raise HTTPException(400, "KARION not paired — configure Firebase in Settings first")
    _ensure_admin(cfg)
    return _db


def _try_decrypt_task(task: dict, key: bytes) -> dict:
    """Mirror AES-256-GCM decrypt from karionBridge.ts."""
    if not task.get("encryptedPayload") or not task.get("encryptionIv"):
        return task
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        # Convert URL-safe base64 to standard
        def b64(s: str) -> bytes:
            s = s.replace("-", "+").replace("_", "/")
            s += "=" * ((4 - len(s) % 4) % 4)
            return bytes.fromhex("") or __import__("base64").b64decode(s)
        ct = b64(task["encryptedPayload"])
        iv = b64(task["encryptionIv"])[:12]
        aesgcm = AESGCM(key)
        plain = aesgcm.decrypt(iv, ct + b"\x00\x00\x00\x00", None).decode("utf-8")
        obj = json.loads(plain)
        return {**task, "title": obj.get("title", task["title"]),
                "description": obj.get("description", task["description"])}
    except Exception as e:
        log.warning("Decrypt failed: %s", e)
        return task


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="JARVIS FastAPI Backend", version="2.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:5174", "http://127.0.0.1:5174", "http://127.0.0.1:8765"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": time.time(), "version": "2.5.0"}


# ── Existing api/main.py endpoints (proxy to preserve behaviour) ─────────────
@app.get("/health")
async def legacy_health():
    """Backward-compatible health endpoint."""
    return {"status": "ok", "backend": "fastapi-jarvis", "port": 8000}


@app.post("/api/wake", dependencies=[Depends(verify_auth)])
async def wake_endpoint(payload: dict[str, Any]):
    """Receives transcript from browser SpeechRecognition wake-word hook."""
    transcript = payload.get("transcript", "")
    log.info("[wake] received: %r", transcript)
    return {"acknowledged": True, "transcript": transcript}


# ── KARION endpoints (ported from karionBridge.ts) ───────────────────────────

@app.get("/api/karion/state")
async def karion_state():
    fb_cfg = _get_firebase_cfg()
    connected = fb_cfg is not None and bool(_key_buf)
    cfg = _load_config()
    pairing = cfg.get("pairing")
    return {
        "connected": connected,
        "pairing": pairing,
        "lastError": None,
    }


@app.post("/api/karion/pair", dependencies=[Depends(verify_auth)])
async def karion_pair(payload: dict[str, Any]):
    global _key_buf, _admin_app, _db
    firebase_cfg = payload.get("firebaseConfig", {})
    uid = payload.get("operatorUid", "").strip()
    e2ee_b64 = payload.get("e2eeSessionKey", "").strip()
    device_name = payload.get("deviceName", "Workstation-PC")

    if not uid or not e2ee_b64:
        raise HTTPException(400, "operatorUid and e2eeSessionKey are required")

    # Validate key length
    import base64 as _b64
    try:
        raw = _b64.b64decode(e2ee_b64)
    except Exception as e:
        raise HTTPException(400, f"Invalid base64 E2EE key: {e}")
    if len(raw) != 32:
        raise HTTPException(400, "E2EE key must be exactly 32 bytes (256-bit AES)")

    _key_buf = raw

    # Save config server-side
    cfg = _load_config()
    cfg["firebase"] = firebase_cfg
    cfg["pairing"] = {"uid": uid, "deviceName": device_name,
                      "e2eeKeyBase64": e2ee_b64, "pairedAt": int(time.time() * 1000)}
    _save_config(cfg)

    # Init firebase so we can create user profile
    try:
        db = get_db(firebase_cfg)
        import datetime as _dt
        ref = db.collection("users").doc(uid)
        snap = ref.get()
        now_str = _dt.datetime.utcnow().isoformat() + "Z"
        if not snap.exists:
            ref.set({
                "userId": uid, "displayName": device_name,
                "assistantName": "Nexus",
                "assistantPersona": "Direct, high-clarity productivity strategist.",
                "pcDeviceName": device_name, "focusLockArmed": True,
                "strictModeEnabled": True, "aiVoiceCredits": 500,
                "createdAt": now_str, "updatedAt": now_str,
            })
        else:
            ref.update({"updatedAt": now_str})
    except Exception as e:
        log.error("Profile init failed: %s", e)
        raise HTTPException(500, f"Pairing succeeded but profile init failed: {e}")

    # Return fingerprint
    import hashlib
    fp_bytes = hashlib.sha256(raw).digest()[:8]
    fingerprint = ":".join(f"{b:02x}" for b in fp_bytes)
    return {"status": "ok", "fingerprint": fingerprint, "uid": uid}


@app.post("/api/karion/tasks/{uid}", dependencies=[Depends(verify_auth)])
async def karion_tasks(uid: str):
    db = get_db()
    snap = await db.collection("users").doc(uid).collection("tasks") \
        .order_by("createdAt", direction=firestore.Query.DESCENDING).limit(50).get()
    tasks = [{**d.to_dict(), "id": d.id} for d in snap.docs]
    if _key_buf:
        tasks = [_try_decrypt_task(t, _key_buf) for t in tasks]
    return tasks


@app.post("/api/karion/focus-sessions/{uid}", dependencies=[Depends(verify_auth)])
async def karion_focus_sessions(uid: str):
    db = get_db()
    snap = await db.collection("users").doc(uid).collection("focus_sessions") \
        .order_by("createdAt", direction=firestore.Query.DESCENDING).limit(20).get()
    return [{"id": d.id, **d.to_dict()} for d in snap.docs]


@app.post("/api/karion/call-requests/{uid}", dependencies=[Depends(verify_auth)])
async def karion_call_requests(uid: str):
    db = get_db()
    snap = await db.collection("users").doc(uid).collection("call_requests") \
        .order_by("createdAt", direction=firestore.Query.DESCENDING).limit(20).get()
    return [{"id": d.id, **d.to_dict()} for d in snap.docs]


@app.post("/api/karion/dispatch-call", dependencies=[Depends(verify_auth)])
async def karion_dispatch(payload: dict[str, Any]):
    uid = payload.get("uid", "").strip()
    command = payload.get("command", "VOICE_AGENT_TURN")
    phone = (payload.get("phoneNumber") or "").strip()
    agent_script = (payload.get("agentScript") or "").strip()
    ussd_code = (payload.get("ussdCode") or "").strip() or None
    if not uid:
        raise HTTPException(400, "uid is required")
    db = get_db()
    doc_ref = db.collection("users").doc(uid).collection("call_requests").document()
    await doc_ref.set({
        "userId": uid, "command": command,
        "phoneNumber": phone[:32],
        "agentScript": agent_script[:1000],
        **({"ussdCode": ussd_code} if ussd_code else {}),
        "requestedBy": "PC_AGENT", "callState": "QUEUED",
        "createdAt": firestore_mod.SERVER_TIMESTAMP,
        "updatedAt": firestore_mod.SERVER_TIMESTAMP,
    })
    return {"status": "ok", "requestId": doc_ref.id}


@app.post("/api/karion/hang-up", dependencies=[Depends(verify_auth)])
async def karion_hang_up(payload: dict[str, Any]):
    uid = payload.get("uid", "").strip()
    if not uid:
        raise HTTPException(400, "uid is required")
    # Reuse dispatch with HANG_UP command
    return await karion_dispatch({"uid": uid, "command": "HANG_UP", "phoneNumber": ""})


@app.post("/api/karion/check-balance", dependencies=[Depends(verify_auth)])
async def karion_check_balance(payload: dict[str, Any]):
    uid = payload.get("uid", "").strip()
    ussd = payload.get("ussdCode") or "*123#"
    if not uid:
        raise HTTPException(400, "uid is required")
    return await karion_dispatch({"uid": uid, "command": "CHECK_BALANCE",
                                  "phoneNumber": "", "ussdCode": ussd})


@app.post("/api/karion/approve-task", dependencies=[Depends(verify_auth)])
async def karion_approve(payload: dict[str, Any]):
    uid = payload.get("uid", "").strip()
    task_id = payload.get("taskId", "").strip()
    agent = payload.get("agentName", "Workstation-PC")
    if not uid or not task_id:
        raise HTTPException(400, "uid and taskId required")
    db = get_db()
    await db.collection("users").doc(uid).collection("tasks").document(task_id).update({
        "pcApproved": True,
        "pcApprovedBy": agent[:80],
        "syncStatus": "PC_VERIFIED",
        "status": "COMPLETED_ON_PC",
        "updatedAt": firestore_mod.SERVER_TIMESTAMP,
    })
    return {"status": "ok"}


@app.post("/api/karion/set-focus-lock", dependencies=[Depends(verify_auth)])
async def karion_set_lock(payload: dict[str, Any]):
    uid = payload.get("uid", "").strip()
    armed = bool(payload.get("armed", False))
    if not uid:
        raise HTTPException(400, "uid is required")
    db = get_db()
    await db.collection("users").doc(uid).update({
        "focusLockArmed": armed,
        "updatedAt": firestore_mod.SERVER_TIMESTAMP,
    })
    return {"status": "ok"}


# ── Legacy api/main.py compat endpoints (telephony, USSD, voice) ─────────────
# These mirror the original api/main.py so existing frontend callers still work.
sys.path.insert(0, str(ROOT))

# Minimal ADB telephony stub that uses the same platform-tools
ADB_PATH = None
_DEVICE_ID = ""

def _find_adb() -> str:
    global ADB_PATH
    if ADB_PATH:
        return ADB_PATH
    for candidate in [
        ROOT / "platform-tools" / "platform-tools" / "adb.exe",
        ROOT / "platform-tools-extracted" / "platform-tools" / "adb.exe",
        "adb",
    ]:
        p = Path(candidate)
        if p.exists():
            ADB_PATH = str(p)
            return ADB_PATH
    return ADB_PATH or "adb"


def _detect_device() -> str:
    global _DEVICE_ID
    if _DEVICE_ID:
        return _DEVICE_ID
    adb = _find_adb()
    try:
        r = subprocess.run([adb, "devices"], capture_output=True, text=True, timeout=5)
        for line in r.stdout.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                _DEVICE_ID = parts[0]
                return _DEVICE_ID
    except Exception:
        pass
    return ""


def _adb_run(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run([_find_adb(), "-s", _detect_device()] + args,
                            capture_output=True, text=True, timeout=30)
    return result.returncode, result.stdout, result.stderr


@app.get("/voice/status", dependencies=[Depends(verify_auth)])
async def voice_status():
    return {"integration_status": "offline", "is_listening": False, "is_speaking": False}

@app.post("/voice/process", dependencies=[Depends(verify_auth)])
async def voice_process(payload: dict[str, Any]):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(400, "text is required")
    # Try to match known commands locally; otherwise return echo
    lower = text.lower()
    if any(kw in lower for kw in ("call", "dial", "phone")) and _detect_device():
        import re as _re
        m = _re.search(r'[\+]?[\d\-\s]{7,15}', text)
        if m:
            rc, out, err = _adb_run(["shell", "am", "start", "-a",
                                     "android.intent.action.CALL", "-d", f"tel:{m.group()}"])
            return {"success": rc == 0, "response": f"Initiating call to {m.group()}", "raw": {"output": out}}
    if any(kw in lower for kw in ("balance", "credit")):
        return {"success": True, "response": "Balance check queued — check KARION panel."}
    if any(kw in lower for kw in ("hangup", "end call")):
        _adb_run(["shell", "input", "keyevent", "KEYCODE_ENDCALL"])
        return {"success": True, "response": "Call terminated"}
    # Fallback: proxy to freellmapi for real AI response
    return await _proxy_to_freellm(text)


@app.post("/voice/listen/start", dependencies=[Depends(verify_auth)])
async def voice_listen_start():
    return {"status": "listening_started"}

@app.post("/voice/listen/stop", dependencies=[Depends(verify_auth)])
async def voice_listen_stop():
    return {"status": "listening_stopped"}

@app.get("/voice/history", dependencies=[Depends(verify_auth)])
async def voice_history(limit: int = 20):
    return {"history": []}

@app.get("/voice/help", dependencies=[Depends(verify_auth)])
async def voice_help():
    return {"help": ["call <number>", "balance", "hangup", "status"]}


@app.get("/sims", dependencies=[Depends(verify_auth)])
async def get_sims():
    # Return placeholder structure; real values come via KARION / USSD flow
    return {"SIM1": {"phone_number": "", "network": "unknown", "ussd_code": "*123#", "sub_id": 0},
            "SIM2": {"phone_number": "", "network": "unknown", "ussd_code": "*123#", "sub_id": 1}}

@app.post("/call", dependencies=[Depends(check_rate_limit), Depends(verify_auth)])
async def initiate_call(target: str, sim: str = "SIM1"):
    if not _detect_device():
        raise HTTPException(400, "No Android device connected via ADB")
    rc, out, err = _adb_run(["shell", "am", "start", "-a",
                             "android.intent.action.CALL", "-d", f"tel:{target}"])
    if rc != 0:
        raise HTTPException(400, err.strip() or out.strip())
    return {"status": "call_initiated", "target": target, "output": out.strip() or "Call sent"}

@app.post("/calls/hangup", dependencies=[Depends(check_rate_limit), Depends(verify_auth)])
async def terminate_call():
    _adb_run(["shell", "input", "keyevent", "KEYCODE_ENDCALL"])
    return {"status": "call_terminated", "output": "Hang-up keyevent sent"}

@app.post("/ussd/balance", dependencies=[Depends(check_rate_limit), Depends(verify_auth)])
async def check_balance(sim_id: str = "SIM1"):
    # USSD requires interactive session; delegate to KARION panel for real operations
    return {"status": "balance_check_queued", "sim": sim_id, "message": "Use KARION Mobile Bridge panel for USSD balance checks."}

@app.get("/status", dependencies=[Depends(verify_auth)])
async def get_status():
    adb_connected = bool(_detect_device())
    return {
        "call_state": "idle" if adb_connected else "unavailable",
        "device_id": _detect_device() or None,
        "adb_connected": adb_connected,
        "timestamp": time.time(),
    }

@app.get("/network", dependencies=[Depends(verify_auth)])
async def detect_network(number: str = "+251954531474"):
    return {"status": "network_detection", "detected_network": "ethiotelecom",
            "detected_ussd_code": "#100#", "sample_number": number}


# ── Freellmapi proxy (centralised LLM calls) ────────────────────────────────
FREELLM_BASE = "http://127.0.0.1:31415"

async def _proxy_to_freellm(prompt: str) -> dict:
    """Best-effort proxy to freellmapi when no local tool matches."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=15) as c:
            resp = await c.post(f"{FREELLM_BASE}/v1/chat/completions", json={
                "model": "default", "messages": [{"role": "user", "content": prompt}],
            }, headers={"Content-Type": "application/json"})
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                reply = choices[0]["message"]["content"] if choices else str(data)
                return {"success": True, "response": reply}
            else:
                return {"success": False, "response": f"Freellmapi returned status {resp.status_code}. Check API key."}
    except Exception as exc:
        log.debug("freellmapi proxy hit: %s", exc)
        return {"success": False, "response": f"Freellmapi unavailable ({exc}). Check Settings > API config."}


@app.post("/api/chat", dependencies=[Depends(verify_auth)])
async def chat_proxy(payload: dict[str, Any]):
    """Proxy arbitrary chat request to freellmapi."""
    messages = payload.get("messages", [])
    if not messages:
        raise HTTPException(400, "messages required")
    model = payload.get("model", "default")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as c:
            resp = await c.post(f"{FREELLM_BASE}/v1/chat/completions", json={
                "model": model, "messages": messages,
            }, headers={"Content-Type": "application/json"})
            return resp.json()
    except Exception as e:
        raise HTTPException(502, f"freellmapi unreachable: {e}")


# ── OS control endpoints ────────────────────────────────────────────────────
@app.post("/api/os/open-app", dependencies=[Depends(verify_auth)])
async def os_open_app(app_name: str):
    try:
        subprocess.Popen(["cmd.exe", "/c", "start", "", app_name], shell=False)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/os/open-url", dependencies=[Depends(verify_auth)])
async def os_open_url(url: str):
    import webbrowser
    webbrowser.open(url)
    return {"status": "ok"}

@app.get("/api/os/status", dependencies=[Depends(verify_auth)])
async def os_status():
    import platform
    return {
        "os": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }


# ── WebSocket — backend status + live events ────────────────────────────────
_connections: set[WebSocket] = set()

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket, token: Optional[str] = Query(None)):
    # Accept token as ?token=... or first message
    async def _read_token() -> str | None:
        try:
            raw = await asyncio.wait_for(ws.receive_text(), timeout=8)
            return raw  # caller must validate
        except (asyncio.TimeoutError, WebSocketDisconnect):
            return None

    if not token:
        raw = await _read_token()
        if raw is None:
            await ws.close(code=4001)
            return
        token = raw.strip()

    try:
        verify_auth(token)
    except HTTPException as exc:
        await ws.close(code=4001)
        log.warning("WS auth failed for initial connect: %s", exc.detail)
        return

    await ws.accept()
    _connections.add(ws)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text("pong")
            elif data == "status":
                await ws.send_text(json.dumps({"status": "healthy", "version": "2.5.0"}))
    except WebSocketDisconnect:
        _connections.discard(ws)
    except Exception as e:
        log.warning("WS error: %s", e)
        _connections.discard(ws)

@app.on_event("shutdown")
async def shutdown():
    for ws in list(_connections):
        try:
            await ws.close()
        except Exception:
            pass


# ── Serve built SPA (fallback to index.html for client-side routing) ──────────
# MUST be last so it doesn't shadow API/WebSocket routes.
if DIST.exists():
    app.mount("/", StaticFiles(directory=str(DIST), html=True), name="static")
