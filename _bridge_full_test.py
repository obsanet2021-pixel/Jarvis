"""Full endpoint smoke test for JARVIS web bridge."""
import sys, threading, time, urllib.request, json
sys.path.insert(0, r"C:\Users\Free user\Jarvis")
from src.jarvis.runtime.event_bus import EventBus
from bridge.websocket_bridge import start_bridge_sync


def main():
    bus = EventBus()
    t = threading.Thread(target=start_bridge_sync, args=(bus, 8765), daemon=True)
    t.start()
    time.sleep(2)

    base = "http://127.0.0.1:8765"
    all_ok = True

    # GET endpoints
    for path in ["/health", "/state", "/config/ai", "/tools", "/permissions", "/logs"]:
        try:
            r = urllib.request.urlopen(base + path, timeout=3)
            body = r.read().decode()[:100]
            print(f"OK  GET {path} -> {r.status}")
        except Exception as e:
            print(f"FAIL GET {path} -> {e}")
            all_ok = False

    # POST /simulate/event
    try:
        data = json.dumps({"event": "agent.started", "data": {"task": "smoke"}}).encode()
        req = urllib.request.Request(base + "/simulate/event", data=data,
                                     headers={"Content-Type": "application/json"})
        r = urllib.request.urlopen(req, timeout=3)
        print(f"OK  POST /simulate/event -> {r.status}")
    except Exception as e:
        print(f"FAIL POST /simulate/event -> {e}")
        all_ok = False

    # POST /config/ai (save)
    try:
        data = json.dumps({"base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini",
                           "api_key": "sk-test-key"}).encode()
        req = urllib.request.Request(base + "/config/ai", data=data,
                                     headers={"Content-Type": "application/json"})
        r = urllib.request.urlopen(req, timeout=3)
        print(f"OK  POST /config/ai (save) -> {r.status}")
    except Exception as e:
        print(f"FAIL POST /config/ai -> {e}")
        all_ok = False

    # POST /config/ai/test
    try:
        data = json.dumps({"api_key": "sk-test-key", "base_url": "https://api.openai.com/v1",
                           "model": "gpt-4o-mini"}).encode()
        req = urllib.request.Request(base + "/config/ai/test", data=data,
                                     headers={"Content-Type": "application/json"})
        r = urllib.request.urlopen(req, timeout=5)
        body = r.read().decode()
        print(f"OK  POST /config/ai/test -> {r.status} ({body[:60]})")
    except Exception as e:
        print(f"FAIL POST /config/ai/test -> {e}")
        all_ok = False

    # POST /logs/clear
    try:
        req = urllib.request.Request(base + "/logs/clear", method="POST")
        r = urllib.request.urlopen(req, timeout=3)
        print(f"OK  POST /logs/clear -> {r.status}")
    except Exception as e:
        print(f"FAIL POST /logs/clear -> {e}")
        all_ok = False

    if all_ok:
        print("\nAll endpoints OK -- bridge is fully operational.")
    else:
        print("\nSome endpoints failed.")


if __name__ == "__main__":
    main()
