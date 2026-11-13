"""Multi-step reasoning engine for JARVIS agent."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .planner import PlanStep

logger = logging.getLogger(__name__)


@dataclass
class ReasoningResult:
    """Result of a reasoning step."""

    thought: str
    action: str = ""
    action_input: Dict[str, Any] = field(default_factory=dict)
    observation: str = ""
    is_final: bool = False
    confidence: float = 1.0


class MultiStepReasoner:
    """Implements chain-of-thought reasoning for multi-step tasks."""

    def __init__(self, model_adapter=None) -> None:
        self._model = model_adapter
        self._history: List[ReasoningResult] = []

    def reason(
        self,
        user_request: str,
        plan: List[PlanStep],
        available_tools: List[str],
        context: Dict[str, Any] | None = None,
    ) -> ReasoningResult:
        """Perform one step of reasoning."""
        context = context or {}
        completed = [s for s in plan if s.status == "completed"]
        pending = [s for s in plan if s.status == "pending"]

        if not pending:
            return ReasoningResult(
                thought="All steps completed",
                is_final=True,
                confidence=1.0,
            )

        next_step = pending[0]

        # Check dependencies
        deps_met = all(
            plan[s.id - 1].status == "completed" if 0 < s.id <= len(plan) else True
            for s in next_step.depends_on
        )

        if not deps_met:
            return ReasoningResult(
                thought=f"Waiting for dependencies: {next_step.depends_on}",
                is_final=False,
                confidence=0.5,
            )

        return ReasoningResult(
            thought=f"Executing step: {next_step.description}",
            action=next_step.tool,
            action_input=next_step.parameters,
            is_final=False,
            confidence=1.0,
        )

    def record_observation(self, result: ReasoningResult) -> None:
        """Record an observation from a tool execution."""
        self._history.append(result)

    def get_history(self) -> List[ReasoningResult]:
        """Get the reasoning history."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear the reasoning history."""
        self._history.clear()

    def summarize(self) -> str:
        """Summarize the reasoning process."""
        if not self._history:
            return "No reasoning steps recorded."
        return "\n".join(
            f"Step {i+1}: {r.thought} -> {r.action} ({r.observation})"
            for i, r in enumerate(self._history)
        )


__all__ = ["MultiStepReasoner", "ReasoningResult"]