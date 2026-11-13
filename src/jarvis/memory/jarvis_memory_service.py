"""
JARVIS Memory Service - background fact extraction for JARVIS interactions.

Integrates OpenJarvis's MemoryService with JARVIS-specific extraction
and storage capabilities.
"""

from __future__ import annotations

import logging
import queue
import threading
from typing import Any, List, Optional

from openjarvis.core.events import Event, EventBus, EventType
from openjarvis.memory.service import MemoryService

from .jarvis_fact_store import JARVISFactStore
from .jarvis_extractor import JARVISFactExtractor

logger = logging.getLogger(__name__)


class JARVISMemoryService(MemoryService):
    """Extended memory service with JARVIS-specific interaction handling."""

    def __init__(
        self,
        store: JARVISFactStore,
        extractor: JARVISFactExtractor,
        *,
        event_bus: EventBus | None = None,
        scanner: Any = None,
        max_queue: int = 256,
    ) -> None:
        super().__init__(store, extractor, event_bus=event_bus, scanner=scanner, max_queue=max_queue)

    def submit_interaction(
        self,
        user_input: str,
        jarvis_response: str = "",
    ) -> bool:
        """Submit a JARVIS interaction for memory extraction."""
        return self.submit(user_input, jarvis_response)

    def get_user_phone_numbers(self) -> List[str]:
        """Retrieve all stored phone numbers."""
        if hasattr(self._store, "get_phone_numbers"):
            return self._store.get_phone_numbers()
        return []

    def get_user_sim_details(self) -> List[str]:
        """Retrieve all stored SIM details."""
        if hasattr(self._store, "get_sim_details"):
            return self._store.get_sim_details()
        return []

    def get_user_preferences(self) -> List[str]:
        """Retrieve all stored user preferences."""
        if hasattr(self._store, "get_preferences"):
            return self._store.get_preferences()
        return []

    def search_memory(self, query: str) -> List[str]:
        """Search memory for relevant facts."""
        if hasattr(self._store, "search_facts"):
            facts = self._store.search_facts(query)
            return [fact.text for fact in facts]
        return []


def build_jarvis_memory_service(
    config: Any,
    engine: Any,
    default_model: str = "",
    *,
    event_bus: EventBus | None = None,
) -> Optional[JARVISMemoryService]:
    """Build a JARVIS memory service from configuration."""
    mem = getattr(config, "memory", None)
    if mem is None or not getattr(mem, "enabled", False):
        return None
    if engine is None:
        return None

    model = getattr(mem, "extraction_model", "") or default_model
    if not model:
        logger.debug("Memory service disabled: no extraction model available")
        return None

    store = JARVISFactStore(
        path=getattr(mem, "facts_path", None),
        max_facts=getattr(mem, "max_facts", 5000),
    )
    extractor = JARVISFactExtractor(engine, model)
    return JARVISMemoryService(
        store, extractor, event_bus=event_bus, scanner=None
    )


__all__ = ["JARVISMemoryService", "build_jarvis_memory_service"]