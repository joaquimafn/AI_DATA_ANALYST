"""Unit tests for LLM providers"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_llm_manager_defaults_to_openai():
    from src.services.llm import LLMManager

    manager = LLMManager()
    assert manager.provider_name == "openai"
    assert manager.get_provider_name() == "openai"


def test_llm_manager_with_anthropic():
    from src.services.llm import LLMManager

    manager = LLMManager(provider="anthropic")
    assert manager.provider_name == "anthropic"
    assert manager.get_provider_name() == "anthropic"


def test_create_llm_manager():
    from src.services.llm import create_llm_manager

    manager = create_llm_manager("openai")
    assert manager.provider_name == "openai"


@pytest.mark.asyncio
async def test_openai_provider_generate():
    from src.services.llm import OpenAIProvider

    mock_response = MagicMock()
    mock_response.json.return_value = {"choices": [{"message": {"content": "SELECT * FROM users"}}]}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(api_key="test-key")
        result = await provider.generate("Show me users", system_prompt="You are a SQL assistant")

        assert result == "SELECT * FROM users"


@pytest.mark.asyncio
async def test_openai_provider_get_name():
    from src.services.llm import OpenAIProvider

    provider = OpenAIProvider(api_key="test")
    assert provider.get_provider_name() == "openai"


@pytest.mark.asyncio
async def test_anthropic_provider_generate():
    from src.services.llm import AnthropicProvider

    mock_response = MagicMock()
    mock_response.json.return_value = {"content": [{"text": "SELECT * FROM orders"}]}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        provider = AnthropicProvider(api_key="test-key")
        result = await provider.generate("Show me orders")

        assert result == "SELECT * FROM orders"


@pytest.mark.asyncio
async def test_anthropic_provider_get_name():
    from src.services.llm import AnthropicProvider

    provider = AnthropicProvider(api_key="test")
    assert provider.get_provider_name() == "anthropic"


@pytest.mark.asyncio
async def test_llm_manager_delegates_to_provider():
    from src.services.llm import LLMManager

    manager = LLMManager(provider="openai")

    with patch.object(manager.provider, "generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = "SELECT 1"
        result = await manager.generate("test prompt")

        assert result == "SELECT 1"
        mock_generate.assert_called_once_with("test prompt", None)


def test_base_llm_provider_is_abc():
    from src.services.llm import BaseLLMProvider

    assert issubclass(BaseLLMProvider, __import__("abc").ABC)
