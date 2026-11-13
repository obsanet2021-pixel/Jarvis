"""Model adapter - abstracts AI model providers from the agent engine."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for an AI model provider."""

    provider: str = "openai"
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 1024
    api_key: str = ""
    base_url: str = ""
    timeout: float = 60.0


class ModelAdapter:
    """Abstracts different AI model providers behind a common interface."""

    def __init__(self, config: ModelConfig | None = None) -> None:
        self._config = config or ModelConfig()
        self._client: Any = None

    @property
    def config(self) -> ModelConfig:
        return self._config

    def initialize(self) -> bool:
        """Initialize the model client."""
        try:
            if self._config.provider == "openai":
                from openai import OpenAI

                self._client = OpenAI(
                    api_key=self._config.api_key,
                    base_url=self._config.base_url or None,
                    timeout=self._config.timeout,
                )
            elif self._config.provider == "anthropic":
                from anthropic import Anthropic

                self._client = Anthropic(
                    api_key=self._config.api_key,
                    timeout=self._config.timeout,
                )
            elif self._config.provider == "ollama":
                import requests

                self._client = {"type": "ollama", "base_url": self._config.base_url}
            else:
                logger.warning("Unknown provider: %s", self._config.provider)
                return False
            return True
        except Exception as exc:
            logger.error("Model initialization failed: %s", exc)
            return False

    def generate(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        """Generate a response from the model."""
        if self._client is None:
            return {"content": "", "error": "Model not initialized"}

        try:
            if self._config.provider == "openai":
                kwargs: Dict[str, Any] = {
                    "model": self._config.model,
                    "messages": messages,
                    "temperature": temperature or self._config.temperature,
                    "max_tokens": max_tokens or self._config.max_tokens,
                }
                if tools:
                    kwargs["tools"] = tools
                response = self._client.chat.completions.create(**kwargs)
                choice = response.choices[0]
                return {
                    "content": choice.message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in (choice.message.tool_calls or [])
                    ],
                    "finish_reason": choice.finish_reason,
                }

            elif self._config.provider == "anthropic":
                kwargs = {
                    "model": self._config.model,
                    "messages": messages,
                    "temperature": temperature or self._config.temperature,
                    "max_tokens": max_tokens or self._config.max_tokens,
                }
                response = self._client.messages.create(**kwargs)
                return {
                    "content": "".join(
                        block.text for block in response.content if hasattr(block, "text")
                    ),
                    "stop_reason": response.stop_reason,
                }

            elif self._config.provider == "ollama":
                import requests

                response = requests.post(
                    f"{self._config.base_url}/api/chat",
                    json={
                        "model": self._config.model,
                        "messages": messages,
                        "temperature": temperature or self._config.temperature,
                        "num_predict": max_tokens or self._config.max_tokens,
                    },
                    timeout=self._config.timeout,
                )
                response.raise_for_status()
                data = response.json()
                return {"content": data.get("message", {}).get("content", "")}

        except Exception as exc:
            logger.error("Model generation failed: %s", exc)
            return {"content": "", "error": str(exc)}

        return {"content": "", "error": "Unknown provider"}


__all__ = ["ModelAdapter", "ModelConfig"]