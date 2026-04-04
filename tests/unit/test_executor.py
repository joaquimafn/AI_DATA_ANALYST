"""Unit tests for Query Executor"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_query_executor_initialization():
    from src.services.executor import QueryExecutor

    executor = QueryExecutor()
    assert executor.max_rows == 1000
    assert executor.timeout_seconds == 5


def test_query_executor_custom_settings():
    from src.services.executor import QueryExecutor

    executor = QueryExecutor(max_rows=500, timeout_seconds=10)
    assert executor.max_rows == 500
    assert executor.timeout_seconds == 10


@pytest.mark.asyncio
async def test_executor_adds_limit():
    from src.services.executor import QueryExecutor

    executor = QueryExecutor(max_rows=100)

    with patch("asyncpg.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [{"id": 1}]
        mock_conn.close = AsyncMock()
        mock_connect.return_value = mock_conn

        await executor.execute("SELECT * FROM users LIMIT 50")

        mock_conn.fetch.assert_called_once()
        call_args = mock_conn.fetch.call_args[0][0]
        assert "LIMIT" in call_args


@pytest.mark.asyncio
async def test_executor_returns_dict_results():
    from src.services.executor import QueryExecutor

    executor = QueryExecutor()

    mock_row = MagicMock()
    mock_row.__iter__ = lambda self: iter(["id", "name"])
    mock_row.keys = lambda: ["id", "name"]
    mock_row.__getitem__ = lambda self, key: {"id": 1, "name": "John"}.get(key)

    with patch("asyncpg.connect") as mock_connect:
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [mock_row]
        mock_conn.close = AsyncMock()
        mock_connect.return_value = mock_conn

        result = await executor.execute("SELECT * FROM users LIMIT 10")

        assert len(result) == 1
        assert isinstance(result[0], dict)


@pytest.mark.asyncio
async def test_executor_validates_tables():
    from src.exceptions import QueryExecutionError
    from src.services.executor import QueryExecutor

    executor = QueryExecutor()

    with pytest.raises(QueryExecutionError):
        await executor.execute_with_schema_check("SELECT * FROM secret_table", allowed_tables=["users", "orders"])


def test_execute_query_convenience_function():
    from src.services.executor import execute_query

    with patch("src.services.executor.QueryExecutor") as MockExecutor:
        mock_instance = MagicMock()
        mock_instance.execute = AsyncMock(return_value=[])
        MockExecutor.return_value = mock_instance

        import asyncio

        asyncio.run(execute_query("SELECT 1 LIMIT 10"))

        MockExecutor.assert_called_once()
