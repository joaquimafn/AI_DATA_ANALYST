from __future__ import annotations

import hashlib
import json
from typing import Any

import redis.asyncio as redis

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)

_redis_client: redis.Redis | None = None


def _get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = redis.from_url(  # type: ignore[no-untyped-call]
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis_connection() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


def generate_cache_key(*args: Any, prefix: str = "cache") -> str:
    content = json.dumps(args, sort_keys=True, default=str)
    hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"{prefix}:{hash_value}"


async def get_cached(key: str) -> str | None:
    try:
        client = _get_redis_client()
        value: str | None = await client.get(key)
        if value:
            logger.debug("Cache hit", key=key)
        else:
            logger.debug("Cache miss", key=key)
        return value
    except Exception as e:
        logger.warning("Cache get failed", key=key, error=str(e))
        return None


async def set_cached(key: str, value: str, ttl_seconds: int | None = None) -> bool:
    try:
        client = _get_redis_client()
        if ttl_seconds:
            await client.setex(key, ttl_seconds, value)
        else:
            await client.set(key, value)
        logger.debug("Cache set", key=key, ttl=ttl_seconds)
        return True
    except Exception as e:
        logger.warning("Cache set failed", key=key, error=str(e))
        return False


async def delete_cached(key: str) -> bool:
    try:
        client = _get_redis_client()
        result: int = await client.delete(key)
        logger.debug("Cache delete", key=key, result=result)
        return result > 0
    except Exception as e:
        logger.warning("Cache delete failed", key=key, error=str(e))
        return False


async def get_cached_json(key: str) -> dict[str, Any] | None:
    value = await get_cached(key)
    if value:
        try:
            return json.loads(value)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            logger.warning("Cache JSON decode failed", key=key)
            return None
    return None


async def set_cached_json(key: str, value: dict[str, Any], ttl_seconds: int | None = None) -> bool:
    try:
        json_str = json.dumps(value, default=str)
        return await set_cached(key, json_str, ttl_seconds)
    except Exception as e:
        logger.warning("Cache JSON set failed", key=key, error=str(e))
        return False


class CacheService:
    def __init__(self, prefix: str = "ai_analyst", default_ttl: int | None = None) -> None:
        settings = get_settings()
        self.prefix = prefix
        self.default_ttl = default_ttl or settings.cache_ttl_seconds

    def make_key(self, *args: Any) -> str:
        content = json.dumps(args, sort_keys=True, default=str)
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"{self.prefix}:{hash_value}"

    async def get(self, key: str) -> str | None:
        return await get_cached(key)

    async def get_json(self, key: str) -> dict[str, Any] | None:
        return await get_cached_json(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        return await set_cached(key, value, ttl or self.default_ttl)

    async def set_json(self, key: str, value: dict[str, Any], ttl: int | None = None) -> bool:
        return await set_cached_json(key, value, ttl or self.default_ttl)

    async def delete(self, key: str) -> bool:
        return await delete_cached(key)

    async def clear_prefix(self, pattern: str | None = None) -> int:
        try:
            client = _get_redis_client()
            search_pattern = pattern or f"{self.prefix}:*"
            keys = []
            async for key in client.scan_iter(match=search_pattern):
                keys.append(key)
            if keys:
                return await client.delete(*keys)  # type: ignore[no-any-return]
            return 0
        except Exception as e:
            logger.warning("Cache clear prefix failed", pattern=search_pattern, error=str(e))
            return 0
