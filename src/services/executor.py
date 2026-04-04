from __future__ import annotations

from typing import Any

import asyncpg

from src.core.config import get_settings
from src.core.logging import get_logger
from src.exceptions import QueryExecutionError
from src.services.validator import SQLValidator

logger = get_logger(__name__)


class QueryExecutor:
    """Executes SQL queries with timeout and row limits."""

    def __init__(self, max_rows: int | None = None, timeout_seconds: int | None = None) -> None:
        settings = get_settings()
        self.max_rows = max_rows or settings.max_rows_limit
        self.timeout_seconds = timeout_seconds or settings.query_timeout_seconds
        self.validator = SQLValidator(max_rows=self.max_rows)

    async def execute(self, sql: str) -> list[dict[str, Any]]:
        """Execute a validated SQL query and return results."""
        is_valid, message = self.validator.validate(sql)
        if not is_valid:
            raise QueryExecutionError(f"Invalid SQL: {message}")

        sql = self.validator.add_limit_if_missing(sql)

        settings = get_settings()

        try:
            conn = await asyncpg.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db,
                command_timeout=self.timeout_seconds,
                readonly=True,
            )

            try:
                logger.info("Executing query", sql_length=len(sql))
                rows = await conn.fetch(sql)
                result = [dict(row) for row in rows]
                logger.info("Query executed", row_count=len(result))
                return result

            finally:
                await conn.close()

        except asyncpg.exceptions.QueryCanceledError:
            logger.warning("Query timeout exceeded", timeout=self.timeout_seconds)
            raise QueryExecutionError(f"Query exceeded timeout of {self.timeout_seconds} seconds") from None
        except asyncpg.exceptions.PostgresConnectionError as e:
            logger.error("Database connection error", error=str(e))
            raise QueryExecutionError("Failed to connect to database") from e
        except Exception as e:
            logger.error("Query execution error", error=str(e))
            raise QueryExecutionError(f"Query execution failed: {e}") from e

    async def execute_with_schema_check(
        self, sql: str, allowed_tables: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Execute query with additional schema validation."""
        tables = self.validator.extract_tables(sql)

        if allowed_tables:
            for table in tables:
                if table not in allowed_tables:
                    raise QueryExecutionError(f"Table '{table}' is not allowed in this query")

        return await self.execute(sql)


async def execute_query(sql: str) -> list[dict[str, Any]]:
    """Convenience function to execute a query."""
    executor = QueryExecutor()
    return await executor.execute(sql)
