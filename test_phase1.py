"""Test script for Phase 1 - Agent Foundation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.jarvis.tools.tool_registry import create_jarvis_tool_registry
from src.jarvis.agent.orchestrator import JarvisOrchestrator
from src.jarvis.agent.tool_router import ToolRouter
from src.jarvis.agent.model_adapter import ModelAdapter, ModelConfig
from src.jarvis.runtime.event_bus import EventBus, EventType
from src.jarvis.runtime.health_monitor import HealthMonitor
from src.jarvis.runtime.lifecycle import JarvisLifecycle


def test_tool_registry():
    """Test the tool registry."""
    print("=== Testing Tool Registry ===")
    registry = create_jarvis_tool_registry()
    tools = registry.list_tools()
    print(f"Registered tools: {[t.name for t in tools]}")
    print(f"Categories: {registry.list_categories()}")
    assert len(tools) > 0, "No tools registered"
    print("Tool registry: OK\n")


def test_orchestrator():
    """Test the orchestrator with a simple request."""
    print("=== Testing Orchestrator ===")
    registry = create_jarvis_tool_registry()
    tool_router = ToolRouter(registry)
    model_config = ModelConfig(provider="openai", model="gpt-4o")
    model_adapter = ModelAdapter(model_config)
    orchestrator = JarvisOrchestrator(tool_router, model_adapter)

    result = orchestrator.process_request("check status")
    print(f"Summary: {result['summary']}")
    print(f"Plan steps: {len(result['plan'])}")
    assert result["summary"], "No summary returned"
    print("Orchestrator: OK\n")


def test_lifecycle():
    """Test the lifecycle management."""
    print("=== Testing Lifecycle ===")
    event_bus = EventBus()
    lifecycle = JarvisLifecycle(event_bus)
    health_monitor = lifecycle.health_monitor

    health_monitor.register_component("test", lambda: {"healthy": True})

    lifecycle.start()
    assert lifecycle.is_running, "Lifecycle not running"

    health = health_monitor.check_all()
    for name, status in health.items():
        print(f"  {name}: {'healthy' if status.healthy else 'unhealthy'}")

    lifecycle.stop()
    assert not lifecycle.is_running, "Lifecycle still running"
    print("Lifecycle: OK\n")


def test_event_bus():
    """Test the event bus."""
    print("=== Testing Event Bus ===")
    bus = EventBus()
    received = []

    def handler(event):
        received.append(event.type)

    bus.subscribe(EventType.TOOL_EXECUTED, handler)
    bus.publish_simple(EventType.TOOL_EXECUTED, {"test": True}, source="test")

    assert len(received) > 0, "No events received"
    print(f"Received events: {[e.value for e in received]}")
    print("Event Bus: OK\n")


def main():
    print("JARVIS Phase 1 Tests\n")
    print("=" * 40)

    try:
        test_tool_registry()
        test_orchestrator()
        test_lifecycle()
        test_event_bus()
        print("=" * 40)
        print("All Phase 1 tests passed!")
        return 0
    except Exception as exc:
        print(f"Test failed: {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())