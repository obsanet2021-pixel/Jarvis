"""Smoke test for threaded bridge start."""
import sys, threading, time, urllib.request
sys.path.insert(0, r"C:\Users\Free user\Jarvis")
from src.jarvis.runtime.event_bus import EventBus
from bridge.websocket_bridge import start_bridge_sync

def main():
    bus = EventBus()
    t = threading.Thread(target=start_bridge_sync, args=(bus, 8765), daemon=True)
    t.start()
    time.sleep(2)
    try:
        r = urllib.request.urlopen("http://127.0.0.1:8765/health", timeout=3)
        print("Health:", r.read().decode())
    except Exception as e:
        print("FAIL:", e)
    exit(0)

main()
