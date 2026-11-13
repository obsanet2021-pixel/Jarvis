"""JARVIS Orchestrator - coordinates agents, tools and execution."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

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

from ..runtime.event_bus import EventBus, EventType
from .model_adapter import ModelAdapter, ModelConfig
from .planner import PlanStep, TaskPlanner
from .reasoning import MultiStepReasoner, ReasoningResult
from .tool_router import ToolRouter

logger = logging.getLogger(__name__)


class JarvisOrchestrator:
    """Main agent orchestrator that coordinates planning, reasoning and execution."""

    def __init__(
        self,
        tool_router: ToolRouter,
        model_adapter: ModelAdapter | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self._tool_router = tool_router
        self._model = model_adapter
        self._event_bus = event_bus
        self._planner = TaskPlanner(model_adapter)
        self._reasoner = MultiStepReasoner(model_adapter)
        self._active_plans: Dict[str, List[PlanStep]] = {}

    def process_request(self, user_request: str) -> Dict[str, Any]:
        """Process a user request through the full agent pipeline."""
        logger.info("Processing request: %s", user_request[:100])

        if self._event_bus:
            self._event_bus.publish_simple(
                EventType.AGENT_STARTED,
                {"request": user_request},
                source="orchestrator",
            )

        # Plan the task
        available_tools = self._tool_router.list_available_tools()
        plan = self._planner.plan(user_request, available_tools)
        self._active_plans[user_request] = plan

        # Execute the plan
        results = []
        for step in plan:
            step.status = "in_progress"

            reasoning = self._reasoner.reason(
                user_request, plan, available_tools
            )

            if step.tool:
                result = self._tool_router.route(step.tool, step.parameters)
                step.result = result.content
                step.status = "completed" if result.success else "failed"
                results.append(
                    {
                        "step": step.to_dict(),
                        "reasoning": reasoning.thought,
                        "success": result.success,
                    }
                )

                if self._event_bus:
                    event_type = (
                        EventType.TOOL_EXECUTED
                        if result.success
                        else EventType.TOOL_FAILED
                    )
                    self._event_bus.publish_simple(
                        event_type,
                        {
                            "tool": step.tool,
                            "success": result.success,
                            "content": result.content[:200],
                        },
                        source="orchestrator",
                    )
            else:
                step.status = "completed"
                results.append({"step": step.to_dict(), "success": True})

        summary = self._summarize_results(results)

        if self._event_bus:
            self._event_bus.publish_simple(
                EventType.AGENT_COMPLETED,
                {"request": user_request, "summary": summary},
                source="orchestrator",
            )

        return {
            "request": user_request,
            "plan": [s.to_dict() for s in plan],
            "results": results,
            "summary": summary,
        }

    def _summarize_results(self, results: List[Dict[str, Any]]) -> str:
        """Summarize the execution results."""
        successful = sum(1 for r in results if r.get("success"))
        total = len(results)
        return f"Completed {successful}/{total} steps successfully"

    def get_active_plan(self, request: str) -> Optional[List[PlanStep]]:
        """Get the active plan for a request."""
        return self._active_plans.get(request)

    def clear_plans(self) -> None:
        """Clear all active plans."""
        self._active_plans.clear()


__all__ = ["JarvisOrchestrator"]