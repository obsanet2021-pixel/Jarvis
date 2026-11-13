"""Approval manager for sensitive JARVIS operations."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ApprovalRequest:
    """A request for user approval."""

    id: str
    tool: str
    description: str
    parameters: Dict[str, Any]
    level: str = "external"
    timestamp: float = field(default_factory=time.time)
    status: str = "pending"  # pending, approved, denied, expired
    resolved_at: float | None = None


class ApprovalManager:
    """Manages approval requests for sensitive operations."""

    def __init__(self, timeout: float = 300.0) -> None:
        self._timeout = timeout
        self._pending: Dict[str, ApprovalRequest] = {}
        self._resolved: List[ApprovalRequest] = []
        self._callbacks: Dict[str, Callable[[ApprovalRequest], None]] = {}

    def request_approval(
        self,
        tool: str,
        description: str,
        parameters: Dict[str, Any],
        level: str = "external",
    ) -> ApprovalRequest:
        """Create an approval request."""
        request = ApprovalRequest(
            id=f"{tool}_{int(time.time() * 1000)}",
            tool=tool,
            description=description,
            parameters=parameters,
            level=level,
        )
        self._pending[request.id] = request
        logger.info("Approval requested: %s - %s", tool, description)
        return request

    def approve(self, request_id: str) -> bool:
        """Approve a pending request."""
        request = self._pending.pop(request_id, None)
        if request is None:
            return False
        request.status = "approved"
        request.resolved_at = time.time()
        self._resolved.append(request)
        self._notify(request)
        return True

    def deny(self, request_id: str) -> bool:
        """Deny a pending request."""
        request = self._pending.pop(request_id, None)
        if request is None:
            return False
        request.status = "denied"
        request.resolved_at = time.time()
        self._resolved.append(request)
        self._notify(request)
        return False

    def get_pending(self) -> List[ApprovalRequest]:
        """Get all pending approval requests."""
        self._expire_stale()
        return list(self._pending.values())

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get a specific approval request."""
        return self._pending.get(request_id)

    def _expire_stale(self) -> None:
        """Remove expired requests."""
        now = time.time()
        expired = [
            rid
            for rid, req in self._pending.items()
            if now - req.timestamp > self._timeout
        ]
        for rid in expired:
            req = self._pending.pop(rid)
            req.status = "expired"
            req.resolved_at = time.time()
            self._resolved.append(req)

    def _notify(self, request: ApprovalRequest) -> None:
        """Notify callbacks of resolution."""
        for callback in self._callbacks.values():
            try:
                callback(request)
            except Exception as exc:
                logger.error("Approval callback failed: %s", exc)

    def on_resolved(self, callback: Callable[[ApprovalRequest], None]) -> None:
        """Register a callback for resolved requests."""
        callback_id = f"cb_{id(callback)}"
        self._callbacks[callback_id] = callback

    def get_history(self) -> List[ApprovalRequest]:
        """Get resolution history."""
        return list(self._resolved)


__all__ = ["ApprovalManager", "ApprovalRequest"]