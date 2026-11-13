"""JARVIS-specific tools integrating with existing telephony and USSD modules."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

try:
    from openjarvis.core.types import ToolResult
    from openjarvis.tools._stubs import BaseTool, ToolSpec
except ImportError:
    from dataclasses import dataclass, field
    from typing import Any, Dict

    @dataclass
    class ToolResult:
        tool_name: str
        content: str
        success: bool = True
        metadata: dict = field(default_factory=dict)

    @dataclass
    class ToolSpec:
        name: str
        description: str
        parameters: Dict[str, Any] = field(default_factory=dict)
        category: str = "general"
        requires_confirmation: bool = False
        timeout_seconds: float = 30.0
        required_capabilities: list = field(default_factory=list)

    class BaseTool:
        tool_id: str = ""

        @property
        def name(self) -> str:
            return self.tool_id

        @property
        def spec(self) -> "ToolSpec":
            raise NotImplementedError

        def execute(self, **params: Any) -> ToolResult:
            raise NotImplementedError

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from core.telephony import AndroidTelephonyAdapter
from core.ussd import USSDManager

logger = logging.getLogger(__name__)

ADB_PATH = r"C:\Users\Free user\Jarvis\platform-tools\platform-tools\adb.exe"
DEVICE_ID = "d12090e57900"


class CallTool(BaseTool):
    """Tool for making phone calls via Android ADB."""

    tool_id = "call"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="call",
            description="Make a phone call to the specified number via Android device",
            parameters={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Phone number to call",
                    }
                },
                "required": ["target"],
            },
            category="phone",
            requires_confirmation=True,
            timeout_seconds=30.0,
            required_capabilities=["phone:call"],
        )

    def execute(self, **params: Any) -> ToolResult:
        target = params.get("target", "")
        if not target:
            return ToolResult(
                tool_name="call",
                content="No phone number provided.",
                success=False,
            )

        try:
            adapter = AndroidTelephonyAdapter(ADB_PATH, DEVICE_ID)
            result = adapter.dial(target)
            if result.returncode == 0:
                return ToolResult(
                    tool_name="call",
                    content=f"Call initiated to {target}",
                    success=True,
                    metadata={"returncode": result.returncode},
                )
            return ToolResult(
                tool_name="call",
                content=f"Call failed: {result.stderr or result.stdout}",
                success=False,
                metadata={"returncode": result.returncode},
            )
        except Exception as exc:
            return ToolResult(
                tool_name="call",
                content=f"Error: {exc}",
                success=False,
            )


class BalanceTool(BaseTool):
    """Tool for checking SIM balance via USSD."""

    tool_id = "balance"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="balance",
            description="Check SIM card balance using USSD code",
            parameters={
                "type": "object",
                "properties": {
                    "sim": {
                        "type": "string",
                        "description": "SIM card to use (SIM1 or SIM2)",
                        "default": "SIM1",
                    }
                },
            },
            category="phone",
            requires_confirmation=False,
            timeout_seconds=30.0,
            required_capabilities=["phone:ussd"],
        )

    def execute(self, **params: Any) -> ToolResult:
        sim_key = params.get("sim", "SIM1")
        try:
            manager = USSDManager(ADB_PATH, DEVICE_ID)
            details = manager.get_sim_details(sim_key)
            result = manager.check_balance(sim_key)
            return ToolResult(
                tool_name="balance",
                content=result["message"],
                success=True,
                metadata={
                    "sim": sim_key,
                    "network": details["network"],
                    "code": result["code"],
                },
            )
        except Exception as exc:
            return ToolResult(
                tool_name="balance",
                content=f"Error: {exc}",
                success=False,
            )


class HangupTool(BaseTool):
    """Tool for hanging up active calls."""

    tool_id = "hangup"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="hangup",
            description="Terminate the active phone call",
            parameters={},
            category="phone",
            requires_confirmation=True,
            timeout_seconds=15.0,
            required_capabilities=["phone:call"],
        )

    def execute(self, **params: Any) -> ToolResult:
        try:
            adapter = AndroidTelephonyAdapter(ADB_PATH, DEVICE_ID)
            result = adapter.hangup()
            if result.returncode == 0:
                return ToolResult(
                    tool_name="hangup",
                    content="Call terminated",
                    success=True,
                )
            return ToolResult(
                tool_name="hangup",
                content=f"Hangup failed: {result.stderr or result.stdout}",
                success=False,
            )
        except Exception as exc:
            return ToolResult(
                tool_name="hangup",
                content=f"Error: {exc}",
                success=False,
            )


class StatusTool(BaseTool):
    """Tool for checking device and call status."""

    tool_id = "status"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="status",
            description="Check device status and active call state",
            parameters={},
            category="phone",
            requires_confirmation=False,
            timeout_seconds=15.0,
            required_capabilities=["phone:status"],
        )

    def execute(self, **params: Any) -> ToolResult:
        try:
            adapter = AndroidTelephonyAdapter(ADB_PATH, DEVICE_ID)
            state = adapter.get_call_state()
            return ToolResult(
                tool_name="status",
                content=state or "No active call",
                success=True,
                metadata={"device": DEVICE_ID},
            )
        except Exception as exc:
            return ToolResult(
                tool_name="status",
                content=f"Error: {exc}",
                success=False,
            )


class USSDTool(BaseTool):
    """Tool for executing USSD codes directly."""

    tool_id = "ussd"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="ussd",
            description="Execute a USSD code on the device",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "USSD code (e.g. *804#)",
                    },
                    "sim": {
                        "type": "string",
                        "description": "SIM card to use",
                        "default": "SIM1",
                    },
                },
                "required": ["code"],
            },
            category="phone",
            requires_confirmation=False,
            timeout_seconds=30.0,
            required_capabilities=["phone:ussd"],
        )

    def execute(self, **params: Any) -> ToolResult:
        code = params.get("code", "")
        sim_key = params.get("sim", "SIM1")
        if not code:
            return ToolResult(
                tool_name="ussd",
                content="No USSD code provided.",
                success=False,
            )
        try:
            manager = USSDManager(ADB_PATH, DEVICE_ID)
            details = manager.get_sim_details(sim_key)
            result = manager.check_balance(sim_key)
            return ToolResult(
                tool_name="ussd",
                content=f"USSD {code} sent for {sim_key}",
                success=True,
                metadata={
                    "sim": sim_key,
                    "network": details["network"],
                    "code": result["code"],
                },
            )
        except Exception as exc:
            return ToolResult(
                tool_name="ussd",
                content=f"Error: {exc}",
                success=False,
            )


__all__ = [
    "CallTool",
    "BalanceTool",
    "HangupTool",
    "StatusTool",
    "USSDTool",
]