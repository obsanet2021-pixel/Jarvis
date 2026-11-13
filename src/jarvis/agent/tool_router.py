"""Tool router - routes agent decisions to appropriate tools."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

try:
    from openjarvis.core.types import ToolResult
except ImportError:
    from dataclasses import dataclass, field
    from typing import Any

    @dataclass
    class ToolResult:
        tool_name: str
        content: str
        success: bool = True
        metadata: dict = field(default_factory=dict)

from ..tools.tool_registry import JARVISToolRegistry

logger = logging.getLogger(__name__)


@dataclass
class ToolRoute:
    """A routing decision for a tool call."""

    tool_name: str
    parameters: Dict[str, Any]
    reason: str = ""
    confidence: float = 1.0


class ToolRouter:
    """Routes agent decisions to the appropriate tools."""

    def __init__(self, registry: JARVISToolRegistry) -> None:
        self._registry = registry
        self._execution_log: List[Dict[str, Any]] = []

    def route(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool call through the registry."""
        logger.info("Routing tool: %s with params: %s", tool_name, parameters)

        result = self._registry.execute(tool_name, parameters)

        self._execution_log.append(
            {
                "tool": tool_name,
                "params": parameters,
                "success": result.success,
                "content": result.content[:200] if result.content else "",
                "timestamp": __import__("time").time(),
            }
        )

        return result

    def list_available_tools(self) -> List[str]:
        """List all available tool names."""
        return [t.name for t in self._registry.list_tools()]

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a tool."""
        tool = self._registry.get(tool_name)
        if tool is None:
            return None
        return tool.to_dict()

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get the execution log."""
        return list(self._execution_log)

    def clear_log(self) -> None:
        """Clear the execution log."""
        self._execution_log.clear()


__all__ = ["ToolRouter", "ToolRoute"]