"""Event bus for JARVIS runtime communication."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Core event types for the JARVIS runtime."""

    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    TOOL_EXECUTED = "tool.executed"
    TOOL_FAILED = "tool.failed"
    MEMORY_STORED = "memory.stored"
    MEMORY_RECALLED = "memory.recalled"
    PERMISSION_REQUIRED = "permission.required"
    PERMISSION_GRANTED = "permission.granted"
    PERMISSION_DENIED = "permission.denied"
    TASK_SCHEDULED = "task.scheduled"
    TASK_COMPLETED = "task.completed"
    ERROR = "error"


@dataclass
class Event:
    """A single event in the bus."""

    type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    timestamp: float = field(default_factory=lambda: __import__("time").time())


class EventBus:
    """Publish-subscribe event bus for component communication."""

    def __init__(self) -> None:
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._lock = threading.RLock()

    def subscribe(
        self, event_type: EventType, handler: Callable[[Event], None]
    ) -> None:
        """Subscribe to an event type."""
        with self._lock:
            self._subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(
        self, event_type: EventType, handler: Callable[[Event], None]
    ) -> None:
        """Unsubscribe from an event type."""
        with self._lock:
            if event_type in self._subscribers:
                self._subscribers[event_type] = [
                    h for h in self._subscribers[event_type] if h is not handler
                ]

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        with self._lock:
            handlers = list(self._subscribers.get(event.type, []))
        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:
                logger.error("Event handler failed: %s", exc)

    def publish_simple(
        self,
        event_type: EventType,
        data: Dict[str, Any] | None = None,
        source: str = "",
    ) -> None:
        """Publish an event with simple parameters."""
        self.publish(Event(type=event_type, data=data or {}, source=source))


__all__ = ["EventBus", "EventType", "Event"]