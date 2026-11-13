"""Bootstrap module for JARVIS application startup."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class JarvisBootstrap:
    """Handles JARVIS application initialization and configuration."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        self._config_path = Path(config_path) if config_path else None
        self._config: Dict[str, Any] = {}
        self._initialized = False

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or defaults."""
        if self._config_path and self._config_path.exists():
            try:
                import json

                with open(self._config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                logger.info("Config loaded from %s", self._config_path)
            except Exception as exc:
                logger.warning("Failed to load config: %s", exc)
                self._config = self._default_config()
        else:
            self._config = self._default_config()
        return self._config

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "app": {
                "name": "JARVIS",
                "version": "1.0.0",
                "debug": False,
            },
            "adb": {
                "path": r"C:\Users\Free user\Jarvis\platform-tools\platform-tools\adb.exe",
                "device": "d12090e57900",
            },
            "memory": {
                "enabled": True,
                "backend": "local",
                "max_facts": 5000,
                "facts_path": str(
                    Path(__file__).resolve().parents[4] / "data" / "memory_facts.jsonl"
                ),
            },
            "agent": {
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 1024,
            },
            "tools": {
                "require_confirmation": True,
                "timeout_seconds": 30,
            },
        }

    def initialize(self) -> bool:
        """Initialize all JARVIS components."""
        logger.info("Initializing JARVIS...")
        self.load_config()
        self._initialized = True
        logger.info("JARVIS initialization complete")
        return True

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    @property
    def is_initialized(self) -> bool:
        return self._initialized


__all__ = ["JarvisBootstrap"]