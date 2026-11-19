import sys, asyncio, urllib.request, time
sys.path.insert(0, r'C:\Users\Free user\Jarvis')
from src.jarvis.runtime.event_bus import EventBus
from bridge.websocket_bridge import start_bridge

async def main():
    bus = EventBus()
    # Keep reference to prevent GC
    srv_task = asyncio.create_task(start_bridge(bus, port=8765))
    # Wait for server to come up
    for i in range(20):
        await asyncio.sleep(0.5)
        try:
            r = urllib.request.urlopen('http://127.0.0.1:8765/health', timeout=2)
            print('OK health:', r.read().decode()[:120])
            break
        except Exception as e:
            print(f'  attempt {i+1}: {e}')
    srv_task.cancel()
    try: await srv_task
    except asyncio.CancelledError: pass

asyncio.run(main())