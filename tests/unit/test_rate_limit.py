"""Unit tests for rate limiting"""

from unittest.mock import AsyncMock, patch

import pytest


def test_rate_limiter_initialization():
    from src.core.rate_limit import RateLimiter

    limiter = RateLimiter(requests_per_minute=30)
    assert limiter.requests_per_minute == 30
    assert limiter.key_prefix == "rate_limit"


@pytest.mark.asyncio
async def test_rate_limiter_allows_within_limit():
    from src.core.rate_limit import RateLimiter

    limiter = RateLimiter(requests_per_minute=60)

    with patch("src.core.rate_limit._get_redis_client") as mock_client:
        mock_client.return_value.get = AsyncMock(return_value=None)
        mock_client.return_value.setex = AsyncMock()

        allowed, remaining = await limiter.check_rate_limit("test_user")

        assert allowed is True
        assert remaining == 59


@pytest.mark.asyncio
async def test_rate_limiter_blocks_when_exceeded():
    from src.core.rate_limit import RateLimiter

    limiter = RateLimiter(requests_per_minute=60)

    with patch("src.core.rate_limit._get_redis_client") as mock_client:
        mock_client.return_value.get = AsyncMock(return_value="60")
        mock_client.return_value.ttl = AsyncMock(return_value=30)

        allowed, remaining = await limiter.check_rate_limit("test_user")

        assert allowed is False
        assert remaining == 30


@pytest.mark.asyncio
async def test_rate_limiter_acquire():
    from src.core.rate_limit import RateLimiter

    limiter = RateLimiter(requests_per_minute=60)

    with patch.object(limiter, "check_rate_limit", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = (True, 59)

        result = await limiter.acquire("test_user")
        assert result is True


@pytest.mark.asyncio
async def test_rate_limiter_wait_time():
    from src.core.rate_limit import RateLimiter

    limiter = RateLimiter(requests_per_minute=60)

    with patch.object(limiter, "check_rate_limit", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = (False, 30)

        wait = await limiter.wait_time("test_user")
        assert wait == 30


def test_rate_limiter_identifier_construction():
    from src.core.rate_limit import RateLimiter

    limiter = RateLimiter(key_prefix="custom")

    with patch("src.core.rate_limit._get_redis_client") as mock_client:
        mock_client.return_value.get = AsyncMock(return_value=None)
        mock_client.return_value.setex = AsyncMock()

        import asyncio

        asyncio.run(limiter.check_rate_limit("user_123"))

        mock_client.return_value.setex.assert_called()
        call_args = mock_client.return_value.setex.call_args
        assert "custom:user_123:" in call_args[0][0]


@pytest.mark.asyncio
async def test_rate_limiter_graceful_failure():
    from src.core.rate_limit import RateLimiter

    limiter = RateLimiter(requests_per_minute=60)

    with patch("src.core.rate_limit._get_redis_client") as mock_client:
        mock_client.return_value.get = AsyncMock(side_effect=Exception("Redis error"))

        allowed, remaining = await limiter.check_rate_limit("test_user")

        assert allowed is True
        assert remaining == 60
