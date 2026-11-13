"""Task planner - breaks down user requests into executable steps."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PlanStep:
    """A single step in a task plan."""

    id: int
    description: str
    tool: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[int] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "tool": self.tool,
            "parameters": self.parameters,
            "depends_on": self.depends_on,
            "status": self.status,
            "result": self.result,
        }


class TaskPlanner:
    """Breaks user requests into executable task plans."""

    def __init__(self, model_adapter=None) -> None:
        self._model = model_adapter
        self._plans: Dict[str, List[PlanStep]] = {}

    def plan(self, user_request: str, available_tools: List[str]) -> List[PlanStep]:
        """Create an executable plan for a user request."""
        logger.info("Planning for request: %s", user_request[:100])

        # Use model for complex planning
        if self._model is not None:
            plan = self._plan_with_model(user_request, available_tools)
            if plan:
                self._plans[user_request] = plan
                return plan

        # Fallback to rule-based planning
        return self._plan_rule_based(user_request, available_tools)

    def _plan_with_model(
        self, user_request: str, available_tools: List[str]
    ) -> Optional[List[PlanStep]]:
        """Use the AI model to create a plan."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a task planner. Break the user's request into "
                        "executable steps using available tools. Respond with a JSON "
                        "array of steps. Each step has: id, description, tool, "
                        "parameters, depends_on (list of step ids)."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Request: {user_request}\nAvailable tools: {available_tools}",
                },
            ]
            response = self._model.generate(messages, temperature=0.0)
            content = response.get("content", "")
            import json

            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                steps_data = json.loads(match.group(0))
                return [
                    PlanStep(
                        id=s.get("id", i),
                        description=s.get("description", ""),
                        tool=s.get("tool", ""),
                        parameters=s.get("parameters", {}),
                        depends_on=s.get("depends_on", []),
                    )
                    for i, s in enumerate(steps_data)
                ]
        except Exception as exc:
            logger.warning("Model planning failed: %s", exc)
        return None

    def _plan_rule_based(
        self, user_request: str, available_tools: List[str]
    ) -> List[PlanStep]:
        """Create a plan using rule-based heuristics."""
        steps = []
        request_lower = user_request.lower()

        step_id = 0

        # Phone call requests
        if any(kw in request_lower for kw in ["call", "dial", "phone"]):
            step_id += 1
            steps.append(
                PlanStep(
                    id=step_id,
                    description="Make phone call",
                    tool="call",
                    parameters={"target": self._extract_phone(user_request)},
                )
            )

        # Balance check requests
        if any(kw in request_lower for kw in ["balance", "credit", "airtime"]):
            step_id += 1
            steps.append(
                PlanStep(
                    id=step_id,
                    description="Check balance",
                    tool="balance",
                    parameters={"sim": "SIM1"},
                )
            )

        # Hangup requests
        if any(kw in request_lower for kw in ["hang up", "hangup", "end call"]):
            step_id += 1
            steps.append(
                PlanStep(
                    id=step_id,
                    description="Hang up active call",
                    tool="hangup",
                )
            )

        # Status check
        if any(kw in request_lower for kw in ["status", "check"]):
            step_id += 1
            steps.append(
                PlanStep(
                    id=step_id,
                    description="Check system status",
                    tool="status",
                )
            )

        # Default: single step
        if not steps:
            step_id += 1
            steps.append(
                PlanStep(
                    id=step_id,
                    description=user_request,
                    tool="",
                    parameters={},
                )
            )

        return steps

    def _extract_phone(self, text: str) -> str:
        """Extract a phone number from text."""
        match = re.search(r"\+?\d{10,15}", text)
        return match.group(0) if match else ""

    def get_plan(self, request: str) -> Optional[List[PlanStep]]:
        """Get a stored plan for a request."""
        return self._plans.get(request)

    def clear_plans(self) -> None:
        """Clear all stored plans."""
        self._plans.clear()


__all__ = ["TaskPlanner", "PlanStep"]