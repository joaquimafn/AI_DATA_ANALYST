from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

import redis.asyncio as redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

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


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Callable[..., Awaitable[Response]],
        requests_per_minute: int | None = None,
        key_prefix: str = "rate_limit",
    ) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        settings = get_settings()
        self.requests_per_minute = requests_per_minute or settings.rate_limit_per_minute
        self.key_prefix = key_prefix
        self.window_seconds = 60

    def _get_identifier(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        return f"{self.key_prefix}:{client_ip}"

    async def _check_rate_limit(self, identifier: str) -> tuple[bool, int]:
        try:
            client = _get_redis_client()
            key = f"{identifier}:counter"

            current_window = int(time.time() // self.window_seconds)
            window_identifier = f"{key}:{current_window}"

            current_count = await client.get(window_identifier)
            if current_count is None:
                await client.setex(window_identifier, self.window_seconds + 1, "1")
                return True, self.requests_per_minute - 1

            count = int(current_count)
            if count >= self.requests_per_minute:
                ttl = await client.ttl(window_identifier)
                return False, ttl if ttl > 0 else 0

            await client.incr(window_identifier)
            return True, self.requests_per_minute - count - 1

        except Exception as e:
            logger.warning("Rate limit check failed", identifier=identifier, error=str(e))
            return True, self.requests_per_minute

    async def dispatch(self, request: Request, call_next: Callable[..., Awaitable[Response]]) -> Response:
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        identifier = self._get_identifier(request)
        allowed, remaining = await self._check_rate_limit(identifier)

        if not allowed:
            logger.warning("Rate limit exceeded", identifier=identifier)
            return Response(
                content='{"error": "Rate limit exceeded", "code": "RATE_LIMIT_ERROR"}',
                status_code=429,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(remaining),
                },
            )

        response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))

        return response


class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int | None = None,
        key_prefix: str = "rate_limit",
    ) -> None:
        settings = get_settings()
        self.requests_per_minute = requests_per_minute or settings.rate_limit_per_minute
        self.key_prefix = key_prefix

    async def check_rate_limit(self, identifier: str) -> tuple[bool, int]:
        try:
            client = _get_redis_client()
            key = f"{self.key_prefix}:{identifier}"
            current_window = int(time.time() // 60)
            window_key = f"{key}:{current_window}"

            current_count = await client.get(window_key)
            if current_count is None:
                await client.setex(window_key, 61, "1")
                return True, self.requests_per_minute - 1

            count = int(current_count)
            if count >= self.requests_per_minute:
                ttl = await client.ttl(window_key)
                return False, ttl if ttl > 0 else 0

            await client.incr(window_key)
            return True, self.requests_per_minute - count - 1

        except Exception as e:
            logger.warning("Rate limit check failed", identifier=identifier, error=str(e))
            return True, self.requests_per_minute

    async def acquire(self, identifier: str) -> bool:
        allowed, _ = await self.check_rate_limit(identifier)
        return allowed

    async def wait_time(self, identifier: str) -> int:
        _, wait_time = await self.check_rate_limit(identifier)
        return wait_time
