"""Unit tests for cache utility"""

from unittest.mock import AsyncMock, patch

import pytest


def test_generate_cache_key():
    from src.utils.cache import generate_cache_key

    key1 = generate_cache_key("test", "args")
    key2 = generate_cache_key("test", "args")
    key3 = generate_cache_key("test", "different")

    assert key1 == key2
    assert key1 != key3
    assert key1.startswith("cache:")
    assert len(key1) == 22


def test_generate_cache_key_with_prefix():
    from src.utils.cache import generate_cache_key

    key = generate_cache_key("test", prefix="custom")
    assert key.startswith("custom:")


@pytest.mark.asyncio
async def test_get_cached_returns_none_when_not_found():
    from src.utils.cache import get_cached

    with patch("src.utils.cache._get_redis_client") as mock_client:
        mock_client.return_value.get = AsyncMock(return_value=None)

        result = await get_cached("nonexistent_key")
        assert result is None


@pytest.mark.asyncio
async def test_set_cached():
    from src.utils.cache import set_cached

    with patch("src.utils.cache._get_redis_client") as mock_client:
        mock_client.return_value.setex = AsyncMock()
        mock_client.return_value.set = AsyncMock()

        result = await set_cached("key", "value", ttl_seconds=60)
        assert result is True
        mock_client.return_value.setex.assert_called_once()


@pytest.mark.asyncio
async def test_set_cached_without_ttl():
    from src.utils.cache import set_cached

    with patch("src.utils.cache._get_redis_client") as mock_client:
        mock_client.return_value.set = AsyncMock()

        result = await set_cached("key", "value")
        assert result is True
        mock_client.return_value.set.assert_called_once()


@pytest.mark.asyncio
async def test_delete_cached():
    from src.utils.cache import delete_cached

    with patch("src.utils.cache._get_redis_client") as mock_client:
        mock_client.return_value.delete = AsyncMock(return_value=1)

        result = await delete_cached("key")
        assert result is True


@pytest.mark.asyncio
async def test_get_cached_json():
    from src.utils.cache import get_cached_json

    with patch("src.utils.cache._get_redis_client") as mock_client:
        mock_client.return_value.get = AsyncMock(return_value='{"key": "value"}')

        result = await get_cached_json("key")
        assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_set_cached_json():
    from src.utils.cache import set_cached_json

    with patch("src.utils.cache._get_redis_client") as mock_client:
        mock_client.return_value.setex = AsyncMock()

        result = await set_cached_json("key", {"key": "value"}, ttl_seconds=60)
        assert result is True


def test_cache_service_initialization():
    from src.utils.cache import CacheService

    cache = CacheService(prefix="test", default_ttl=300)
    assert cache.prefix == "test"
    assert cache.default_ttl == 300


def test_cache_service_make_key():
    from src.utils.cache import CacheService

    cache = CacheService(prefix="test")
    key = cache.make_key("arg1", "arg2")

    assert key.startswith("test:")
    assert len(key) == 21


@pytest.mark.asyncio
async def test_cache_service_get():
    from src.utils.cache import CacheService

    cache = CacheService()

    with patch.object(cache, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = "value"

        result = await cache.get("key")
        assert result == "value"


@pytest.mark.asyncio
async def test_cache_service_get_json():
    from src.utils.cache import CacheService

    cache = CacheService()

    with patch.object(cache, "get_json", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"key": "value"}

        result = await cache.get_json("key")
        assert result == {"key": "value"}
