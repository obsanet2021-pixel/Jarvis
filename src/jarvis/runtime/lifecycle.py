"""Lifecycle management for JARVIS application."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List

from .event_bus import EventBus, EventType
from .health_monitor import HealthMonitor

logger = logging.getLogger(__name__)


class JarvisLifecycle:
    """Manages the startup, running and shutdown phases of JARVIS."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._event_bus = event_bus or EventBus()
        self._health_monitor = HealthMonitor()
        self._startup_hooks: List[Callable[[], None]] = []
        self._shutdown_hooks: List[Callable[[], None]] = []
        self._running = False

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    @property
    def health_monitor(self) -> HealthMonitor:
        return self._health_monitor

    def on_startup(self, hook: Callable[[], None]) -> None:
        """Register a startup hook."""
        self._startup_hooks.append(hook)

    def on_shutdown(self, hook: Callable[[], None]) -> None:
        """Register a shutdown hook."""
        self._shutdown_hooks.append(hook)

    def start(self) -> bool:
        """Start the JARVIS lifecycle."""
        logger.info("Starting JARVIS lifecycle...")
        self._event_bus.publish_simple(EventType.STARTUP, {}, source="lifecycle")

        for hook in self._startup_hooks:
            try:
                hook()
            except Exception as exc:
                logger.error("Startup hook failed: %s", exc)
                return False

        self._running = True
        logger.info("JARVIS lifecycle started")
        return True

    def stop(self) -> None:
        """Stop the JARVIS lifecycle."""
        logger.info("Stopping JARVIS lifecycle...")
        self._running = False

        for hook in reversed(self._shutdown_hooks):
            try:
                hook()
            except Exception as exc:
                logger.error("Shutdown hook failed: %s", exc)

        self._event_bus.publish_simple(EventType.SHUTDOWN, {}, source="lifecycle")
        logger.info("JARVIS lifecycle stopped")

    @property
    def is_running(self) -> bool:
        return self._running


__all__ = ["JarvisLifecycle"]