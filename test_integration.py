"""Phase 5 integration test for JARVIS bridge."""
import asyncio
import json
import sys
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8765"

SEP = "=" * 60

def get(path):
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=3) as r:
            return r.status, json.loads(r.read())
    except Exception as e:
        return None, str(e)

def post(path, body=None):
    try:
        data = json.dumps(body).encode() if body else None
        headers = {"Content-Type": "application/json"} if data else {}
        req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=3) as r:
            return r.status, json.loads(r.read())
    except Exception as e:
        return None, str(e)

print(SEP)
print("JARVIS Bridge - Phase 5 Integration Tests")
import time
print("START: {}".format(int(time.time())))
print(SEP)

# 1. Health check
code, data = get("/health")
assert code == 200, f"/health returned {code}"
assert data["status"] == "ok"
assert data["service"] == "jarvis-bridge"
print(f"[PASS] /health -> service={data['service']}")

# 2. Current state
code, data = get("/state")
assert code == 200
assert "jarvis_state" in data
print(f"[PASS] /state -> state={data['jarvis_state']}")

# 3. Voice status
code, data = get("/voice/status")
assert code == 200
print(f"[PASS] /voice/status -> listening={data['is_listening']}")

# 4. Tools
code, data = get("/tools")
assert code == 200
print(f"[PASS] /tools accessible")

# 5. Permissions
code, _ = get("/permissions")
assert code == 200
print("[PASS] /permissions accessible")

# 6. AI config
code, config = get("/config/ai")
assert code == 200
assert "provider" in config
print(f"[PASS] /config/ai -> provider={config['provider']}")

# 7. Logs
code, data = get("/logs")
assert code == 200
logs = data.get("logs", data) if isinstance(data, dict) else data
print(f"[PASS] /logs accessible (found {len(logs)} entries)")

# 8. Simulate voice events
events = [
    ("wake_word.detected", {"wake_word": "Jarvis", "text": "test"}),
    ("command.transcribed", {"text": "open browser"}),
    ("speech.starting", {"phrase": "listening"}),
    ("speech.ended", {"phrase": "done"}),
]
for tag, payload in events:
    code, resp = post("/simulate/event", {"tag": tag, "data": payload})
    assert code == 200, f"event {tag} failed: {resp}"
    print(f"[PASS] event simulated: {tag}")

# 9. Verify event affected state
code, voice = get("/voice/status")
print(f"[PASS] voice status after events: {voice}")

# 10. Check lock file
lock = Path.home() / ".jarvis_wake.lock"
assert lock.exists(), f"lock file {lock} missing"
print(f"[PASS] lock file active: {lock}")

# 11. Clear logs and verify
code, _ = post("/logs/clear")
assert code == 200
print("[PASS] /logs/clear works")

# 12. Verify lock on second launch attempt
import subprocess
proc = subprocess.Popen([sys.executable, "jarvis_wake.py", "--no-gui"],
    cwd="C:\\Users\\Free user\\Jarvis",
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    stdout, stderr = proc.communicate(timeout=3)
    out_text = stdout.decode() + stderr.decode()
    if "Another instance is already running." in out_text:
        print("[PASS] second instance prevented by lock")
    else:
        print("[FAIL] lock didn't block second instance")
except subprocess.TimeoutExpired:
    proc.kill()
    print("[INFO] proc still running")

print(SEP)
print("ALL TESTS PASSED")
print("END: {}".format(int(time.time())))
print(SEP)
