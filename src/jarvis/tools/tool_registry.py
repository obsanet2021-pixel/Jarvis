"""
JARVIS Tool Registry - manages available tools and their execution.

Provides a centralized registry for JARVIS commands with validation,
permission checking, and execution tracking.
"""

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

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """Definition of an executable tool."""

    name: str
    description: str
    category: str
    requires_confirmation: bool = False
    timeout_seconds: float = 30.0
    required_capabilities: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    executor: Optional[Callable[..., ToolResult]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "requires_confirmation": self.requires_confirmation,
            "timeout_seconds": self.timeout_seconds,
            "required_capabilities": self.required_capabilities,
            "parameters": self.parameters,
        }


class JARVISToolRegistry:
    """Registry for JARVIS tools with execution and validation."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}
        self._categories: Dict[str, List[str]] = {}
        self._capabilities: set[str] = set()

    def register(self, tool: ToolDefinition) -> None:
        """Register a new tool."""
        self._tools[tool.name] = tool
        if tool.category not in self._categories:
            self._categories[tool.category] = []
        self._categories[tool.category].append(tool.name)
        self._capabilities.update(tool.required_capabilities)
        logger.debug("Registered tool: %s (category: %s)", tool.name, tool.category)

    def register_tool(self, tool_instance) -> None:
        """Register a tool instance by extracting its spec."""
        spec = tool_instance.spec
        definition = ToolDefinition(
            name=spec.name,
            description=spec.description,
            category=spec.category,
            requires_confirmation=spec.requires_confirmation,
            timeout_seconds=spec.timeout_seconds,
            required_capabilities=list(spec.required_capabilities),
            parameters=spec.parameters,
            executor=tool_instance.execute,
        )
        self.register(definition)

    def unregister(self, name: str) -> None:
        """Remove a tool from the registry."""
        if name in self._tools:
            tool = self._tools.pop(name)
            if tool.category in self._categories:
                self._categories[tool.category].remove(name)
                if not self._categories[tool.category]:
                    del self._categories[tool.category]
            logger.debug("Unregistered tool: %s", name)

    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool definition by name."""
        return self._tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> List[ToolDefinition]:
        """List all tools, optionally filtered by category."""
        if category:
            names = self._categories.get(category, [])
            return [self._tools[n] for n in names if n in self._tools]
        return list(self._tools.values())

    def list_categories(self) -> List[str]:
        """List all tool categories."""
        return list(self._categories.keys())

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    def check_capability(self, capability: str) -> bool:
        """Check if the registry supports a capability."""
        return capability in self._capabilities

    def execute(
        self,
        tool_name: str,
        params: Dict[str, Any],
        *,
        confirm: bool = True,
    ) -> ToolResult:
        """Execute a registered tool with validation."""
        tool = self.get(tool_name)
        if tool is None:
            return ToolResult(
                tool_name=tool_name,
                content=f"Unknown tool: {tool_name}",
                success=False,
            )

        if tool.requires_confirmation and confirm:
            # In a real implementation, this would prompt the user
            logger.info("Tool %s requires confirmation", tool_name)

        if tool.executor is None:
            return ToolResult(
                tool_name=tool_name,
                content=f"Tool {tool_name} has no executor",
                success=False,
            )

        try:
            return tool.executor(**params)
        except Exception as exc:
            logger.error("Tool %s execution failed: %s", tool_name, exc)
            return ToolResult(
                tool_name=tool_name,
                content=f"Execution error: {exc}",
                success=False,
            )


def create_jarvis_tool_registry() -> JARVISToolRegistry:
    """Create a JARVIS tool registry with default tools."""
    registry = JARVISToolRegistry()
    _register_default_tools(registry)
    return registry


def _register_default_tools(registry: JARVISToolRegistry) -> None:
    """Register JARVIS's default tools."""
    from .jarvis_tools import (
        CallTool,
        BalanceTool,
        HangupTool,
        StatusTool,
        USSDTool,
    )

    for tool_cls in [CallTool, BalanceTool, HangupTool, StatusTool, USSDTool]:
        try:
            tool = tool_cls()
            registry.register_tool(tool)
        except Exception as exc:
            logger.warning("Failed to register tool %s: %s", tool_cls.__name__, exc)


__all__ = [
    "ToolDefinition",
    "JARVISToolRegistry",
    "create_jarvis_tool_registry",
]