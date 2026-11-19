import sys, asyncio, urllib.request, time
sys.path.insert(0, r'C:\Users\Free user\Jarvis')
from src.jarvis.runtime.event_bus import EventBus
from bridge.websocket_bridge import start_bridge

async def main():
    bus = EventBus()
    task = asyncio.create_task(start_bridge(bus, port=8765))
    # Give server time to bind
    for i in range(10):
        await asyncio.sleep(0.3)
        try:
            r = urllib.request.urlopen('http://127.0.0.1:8765/health', timeout=2)
            print('Health:', r.read().decode())
            break
        except Exception as e:
            print(f'Wait {i+1}: {e}')
    task.cancel()
    try: await task
    except asyncio.CancelledError: pass

asyncio.run(main())