"""Audit logging for JARVIS tool executions and permissions."""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """A single audit log entry."""

    timestamp: str
    event_type: str
    tool: str = ""
    user: str = ""
    action: str = ""
    result: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    level: str = "info"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AuditLog:
    """Persistent audit log for JARVIS operations."""

    def __init__(self, log_path: str | Path | None = None) -> None:
        self._log_path = Path(log_path) if log_path else None
        self._entries: List[AuditEntry] = []
        self._lock = threading.Lock()
        self._max_entries = 10000

    def log(
        self,
        event_type: str,
        tool: str = "",
        action: str = "",
        result: str = "",
        details: Dict[str, Any] | None = None,
        level: str = "info",
    ) -> AuditEntry:
        """Add an audit entry."""
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            tool=tool,
            action=action,
            result=result,
            details=details or {},
            level=level,
        )
        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > self._max_entries:
                self._entries = self._entries[-self._max_entries :]
            if self._log_path:
                self._append_to_file(entry)
        return entry

    def log_tool_execution(
        self,
        tool: str,
        params: Dict[str, Any],
        success: bool,
        content: str = "",
    ) -> AuditEntry:
        """Log a tool execution."""
        return self.log(
            event_type="tool_executed",
            tool=tool,
            action="execute",
            result="success" if success else "failed",
            details={"params": params, "content_preview": content[:200]},
            level="info" if success else "warning",
        )

    def log_approval(
        self,
        tool: str,
        action: str,
        approved: bool,
        user: str = "",
    ) -> AuditEntry:
        """Log an approval decision."""
        return self.log(
            event_type="approval",
            tool=tool,
            action=action,
            result="approved" if approved else "denied",
            user=user,
            level="info",
        )

    def log_permission_denied(
        self,
        tool: str,
        reason: str,
    ) -> AuditEntry:
        """Log a permission denial."""
        return self.log(
            event_type="permission_denied",
            tool=tool,
            result=reason,
            level="warning",
        )

    def get_entries(
        self,
        tool: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """Get audit entries with optional filtering."""
        with self._lock:
            entries = list(self._entries)
        if tool:
            entries = [e for e in entries if e.tool == tool]
        if event_type:
            entries = [e for e in entries if e.event_type == event_type]
        return entries[-limit:]

    def _append_to_file(self, entry: AuditEntry) -> None:
        """Append an entry to the log file."""
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(entry.to_json() + "\n")
        except Exception as exc:
            logger.error("Failed to write audit log: %s", exc)

    def clear(self) -> int:
        """Clear all audit entries."""
        with self._lock:
            count = len(self._entries)
            self._entries = []
            if self._log_path and self._log_path.exists():
                self._log_path.unlink()
            return count

    def count(self) -> int:
        """Get the number of audit entries."""
        with self._lock:
            return len(self._entries)


__all__ = ["AuditLog", "AuditEntry"]