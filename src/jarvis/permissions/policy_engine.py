"""Permission policy engine for JARVIS tools."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PermissionLevel(IntEnum):
    """Four permission levels for JARVIS actions."""

    READ = 0
    ROUTINE = 1
    EXTERNAL = 2
    CRITICAL = 3


@dataclass
class PermissionPolicy:
    """Defines permission requirements for a tool or action."""

    tool: str
    level: PermissionLevel
    description: str = ""
    requires_confirmation: bool = False
    auto_approve: bool = False
    conditions: List[str] = field(default_factory=list)


# Default permission policies for JARVIS tools
DEFAULT_POLICIES: Dict[str, PermissionPolicy] = {
    "call": PermissionPolicy(
        tool="call",
        level=PermissionLevel.EXTERNAL,
        description="Make phone calls",
        requires_confirmation=True,
    ),
    "hangup": PermissionPolicy(
        tool="hangup",
        level=PermissionLevel.EXTERNAL,
        description="Terminate active calls",
        requires_confirmation=True,
    ),
    "balance": PermissionPolicy(
        tool="balance",
        level=PermissionLevel.ROUTINE,
        description="Check SIM balance",
        requires_confirmation=False,
        auto_approve=True,
    ),
    "ussd": PermissionPolicy(
        tool="ussd",
        level=PermissionLevel.ROUTINE,
        description="Execute USSD codes",
        requires_confirmation=False,
        auto_approve=True,
    ),
    "status": PermissionPolicy(
        tool="status",
        level=PermissionLevel.READ,
        description="Check device status",
        requires_confirmation=False,
        auto_approve=True,
    ),
    "shell.execute": PermissionPolicy(
        tool="shell.execute",
        level=PermissionLevel.CRITICAL,
        description="Execute shell commands",
        requires_confirmation=True,
    ),
    "file.delete": PermissionPolicy(
        tool="file.delete",
        level=PermissionLevel.CRITICAL,
        description="Delete files",
        requires_confirmation=True,
    ),
    "email.send": PermissionPolicy(
        tool="email.send",
        level=PermissionLevel.EXTERNAL,
        description="Send emails",
        requires_confirmation=True,
    ),
    "telegram.send": PermissionPolicy(
        tool="telegram.send",
        level=PermissionLevel.EXTERNAL,
        description="Send Telegram messages",
        requires_confirmation=True,
    ),
}


class PermissionEngine:
    """Enforces permission policies for tool execution."""

    def __init__(self, policies: Dict[str, PermissionPolicy] | None = None) -> None:
        self._policies = policies or DEFAULT_POLICIES
        self._overrides: Dict[str, bool] = {}

    def get_policy(self, tool: str) -> Optional[PermissionPolicy]:
        """Get the permission policy for a tool."""
        return self._policies.get(tool)

    def check(self, tool: str, context: Dict[str, Any] | None = None) -> bool:
        """Check if a tool can execute without confirmation."""
        policy = self._policies.get(tool)
        if policy is None:
            # Unknown tools require confirmation by default
            return False
        if tool in self._overrides:
            return self._overrides[tool]
        return policy.auto_approve and not policy.requires_confirmation

    def requires_confirmation(self, tool: str) -> bool:
        """Check if a tool requires user confirmation."""
        policy = self._policies.get(tool)
        if policy is None:
            return True
        return policy.requires_confirmation

    def get_level(self, tool: str) -> PermissionLevel:
        """Get the permission level for a tool."""
        policy = self._policies.get(tool)
        return policy.level if policy else PermissionLevel.CRITICAL

    def set_override(self, tool: str, approved: bool) -> None:
        """Set an approval override for a tool."""
        self._overrides[tool] = approved

    def clear_overrides(self) -> None:
        """Clear all approval overrides."""
        self._overrides.clear()


def check_permission(tool: str, context: Dict[str, Any] | None = None) -> bool:
    """Quick permission check using default policies."""
    engine = PermissionEngine()
    return engine.check(tool, context)


__all__ = [
    "PermissionLevel",
    "PermissionPolicy",
    "PermissionEngine",
    "check_permission",
    "DEFAULT_POLICIES",
]