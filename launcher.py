"""Unified launcher for JARVIS application."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.jarvis.runtime.bootstrap import JarvisBootstrap
from src.jarvis.runtime.event_bus import EventBus, EventType
from src.jarvis.runtime.health_monitor import HealthMonitor
from src.jarvis.runtime.lifecycle import JarvisLifecycle
from src.jarvis.tools.tool_registry import create_jarvis_tool_registry
from src.jarvis.agent.orchestrator import JarvisOrchestrator
from src.jarvis.agent.model_adapter import ModelAdapter, ModelConfig
from src.jarvis.agent.tool_router import ToolRouter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="JARVIS - Personal AI Assistant")
    parser.add_argument(
        "command",
        nargs="?",
        default="gui",
        choices=["gui", "cli", "status", "test"],
        help="Command to execute",
    )
    parser.add_argument("--request", "-r", help="User request for CLI mode")
    parser.add_argument("--model", default="gpt-4o", help="AI model to use")
    args = parser.parse_args()

    # Bootstrap
    bootstrap = JarvisBootstrap()
    bootstrap.initialize()
    config = bootstrap.config

    # Setup runtime
    event_bus = EventBus()
    lifecycle = JarvisLifecycle(event_bus)
    health_monitor = lifecycle.health_monitor

    # Register components
    health_monitor.register_component("bootstrap", lambda: {"healthy": True})
    health_monitor.register_component("tools")

    # Setup tools and agent
    registry = create_jarvis_tool_registry()
    tool_router = ToolRouter(registry)
    model_config = ModelConfig(
        provider="openai",
        model=args.model,
        api_key=config.get("agent", {}).get("api_key", ""),
    )
    model_adapter = ModelAdapter(model_config)
    orchestrator = JarvisOrchestrator(tool_router, model_adapter, event_bus)

    # Lifecycle hooks
    lifecycle.on_startup(lambda: logger.info("JARVIS ready"))
    lifecycle.on_shutdown(lambda: logger.info("JARVIS shutting down"))

    # Execute command
    if args.command == "status":
        health = health_monitor.check_all()
        for name, status in health.items():
            print(f"{name}: {'healthy' if status.healthy else 'unhealthy'}")
        print(f"Available tools: {registry.list_tools()}")

    elif args.command == "test":
        # Test tool registry
        tools = registry.list_tools()
        print(f"Registered tools: {[t.name for t in tools]}")

        # Test orchestrator with simple request
        result = orchestrator.process_request("check status")
        print(f"Orchestrator result: {result['summary']}")

    elif args.command == "cli":
        if not args.request:
            print("Error: --request required for CLI mode")
            return 1
        result = orchestrator.process_request(args.request)
        print(result["summary"])
        for r in result["results"]:
            print(f"  {r['step']['description']}: {r.get('success', False)}")

    elif args.command == "gui":
        lifecycle.start()
        try:
            from gui.jarvis_gui_enhanced import main as gui_main
            gui_main()
        except Exception as exc:
            logger.error("GUI failed: %s", exc)
            return 1
        finally:
            lifecycle.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())