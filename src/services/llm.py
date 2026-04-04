from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from src.core.config import get_settings
from src.core.logging import get_logger
from src.exceptions import LLMGenerationError

logger = get_logger(__name__)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name."""
        raise NotImplementedError


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4 provider."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4") -> None:
        self.api_key = api_key or get_settings().openai_api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 2000,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]  # type: ignore[no-any-return]
        except httpx.HTTPStatusError as e:
            logger.error("OpenAI API error", status_code=e.response.status_code, error=str(e))
            raise LLMGenerationError(f"OpenAI API error: {e.response.status_code}") from e
        except Exception as e:
            logger.error("OpenAI generation failed", error=str(e))
            raise LLMGenerationError(f"OpenAI generation failed: {e}") from e

    def get_provider_name(self) -> str:
        return "openai"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: str | None = None, model: str = "claude-3-sonnet-20240229") -> None:
        self.api_key = api_key or get_settings().anthropic_api_key
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": self.model,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]  # type: ignore[no-any-return]
        except httpx.HTTPStatusError as e:
            logger.error("Anthropic API error", status_code=e.response.status_code, error=str(e))
            raise LLMGenerationError(f"Anthropic API error: {e.response.status_code}") from e
        except Exception as e:
            logger.error("Anthropic generation failed", error=str(e))
            raise LLMGenerationError(f"Anthropic generation failed: {e}") from e

    def get_provider_name(self) -> str:
        return "anthropic"


class LLMManager:
    """Manager for LLM providers."""

    def __init__(self, provider: str = "openai") -> None:
        self.provider_name = provider
        self._provider: BaseLLMProvider | None = None

    @property
    def provider(self) -> BaseLLMProvider:
        if self._provider is None:
            if self.provider_name == "anthropic":
                self._provider = AnthropicProvider()
            else:
                self._provider = OpenAIProvider()
        return self._provider

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        logger.info("Generating LLM response", provider=self.provider_name)
        return await self.provider.generate(prompt, system_prompt)

    def get_provider_name(self) -> str:
        return self.provider.get_provider_name()


def create_llm_manager(provider: str = "openai") -> LLMManager:
    """Factory function to create an LLM manager."""
    return LLMManager(provider=provider)
