"""Health monitoring for JARVIS runtime."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health status of a component."""

    name: str
    healthy: bool = True
    message: str = ""
    last_check: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)


class HealthMonitor:
    """Monitors the health of JARVIS components."""

    def __init__(self) -> None:
        self._statuses: Dict[str, HealthStatus] = {}
        self._checks: Dict[str, callable] = {}

    def register_component(self, name: str, check: callable | None = None) -> None:
        """Register a component for health monitoring."""
        self._statuses[name] = HealthStatus(name=name)
        if check:
            self._checks[name] = check

    def check(self, name: str) -> HealthStatus:
        """Check the health of a component."""
        status = self._statuses.get(name)
        if status is None:
            return HealthStatus(name=name, healthy=False, message="Unknown component")

        if name in self._checks:
            try:
                result = self._checks[name]()
                if isinstance(result, HealthStatus):
                    self._statuses[name] = result
                elif isinstance(result, bool):
                    status.healthy = result
                elif isinstance(result, dict):
                    status.details.update(result)
            except Exception as exc:
                status.healthy = False
                status.message = str(exc)

        status.last_check = time.time()
        return status

    def check_all(self) -> Dict[str, HealthStatus]:
        """Check all registered components."""
        return {name: self.check(name) for name in self._statuses}

    def is_healthy(self) -> bool:
        """Check if all components are healthy."""
        return all(s.healthy for s in self.check_all().values())

    def get_unhealthy(self) -> List[HealthStatus]:
        """Get list of unhealthy components."""
        return [s for s in self.check_all().values() if not s.healthy]


__all__ = ["HealthMonitor", "HealthStatus"]