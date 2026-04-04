from __future__ import annotations

import re

import asyncpg

from src.core.config import get_settings
from src.core.logging import get_logger
from src.exceptions import SchemaExtractionError
from src.models.schema import ColumnSchema, DatabaseSchema, TableSchema

logger = get_logger(__name__)

_cached_schema: DatabaseSchema | None = None

VALID_IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _is_valid_identifier(name: str) -> bool:
    return bool(VALID_IDENTIFIER_PATTERN.match(name)) and len(name) <= 63


async def extract_table_columns(conn: asyncpg.Connection, table_name: str) -> list[ColumnSchema]:
    query = """
        SELECT
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            CASE WHEN pk.column_name IS NOT NULL THEN TRUE ELSE FALSE END as is_primary_key,
            fk.foreign_key
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = $1
                AND tc.constraint_type = 'PRIMARY KEY'
        ) pk ON c.column_name = pk.column_name
        LEFT JOIN (
            SELECT
                kcu.column_name,
                ccu.table_name || '.' || ccu.column_name as foreign_key
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_name = $1
                AND tc.constraint_type = 'FOREIGN KEY'
        ) fk ON c.column_name = fk.column_name
        WHERE c.table_name = $1
        ORDER BY c.ordinal_position
    """
    rows = await conn.fetch(query, table_name)

    columns = []
    for row in rows:
        columns.append(
            ColumnSchema(
                name=row["column_name"],
                data_type=row["data_type"],
                is_nullable=row["is_nullable"] == "YES",
                is_primary_key=row["is_primary_key"],
                foreign_key=row["foreign_key"],
            )
        )
    return columns


async def extract_table_row_count(conn: asyncpg.Connection, table_name: str) -> int | None:
    if not _is_valid_identifier(table_name):
        logger.warning("Invalid table name for row count", table=table_name)
        return None

    try:
        query = f'SELECT COUNT(*) FROM "{table_name}"'  # nosec
        count_raw = await conn.fetchval(query)
        return int(count_raw) if count_raw is not None else None
    except Exception:
        return None


async def extract_schema(force_refresh: bool = False) -> DatabaseSchema:
    global _cached_schema

    if _cached_schema is not None and not force_refresh:
        logger.info("Returning cached schema")
        return _cached_schema

    settings = get_settings()
    schema = DatabaseSchema(tables=[], version="1.0")

    try:
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
            timeout=10,
        )

        try:
            tables_query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            table_names = await conn.fetch(tables_query)

            for table_row in table_names:
                table_name = table_row["table_name"]
                logger.info("Extracting schema for table", table=table_name)

                columns = await extract_table_columns(conn, table_name)
                row_count = await extract_table_row_count(conn, table_name)

                table_schema = TableSchema(
                    name=table_name,
                    columns=columns,
                    row_count=row_count,
                )
                schema.tables.append(table_schema)

            schema.version = "1.0"
            _cached_schema = schema
            logger.info("Schema extraction completed", table_count=len(schema.tables))

        finally:
            await conn.close()

    except Exception as e:
        logger.error("Schema extraction failed", error=str(e))
        raise SchemaExtractionError(f"Failed to extract database schema: {e}") from e

    return schema


def get_cached_schema() -> DatabaseSchema | None:
    return _cached_schema


def clear_schema_cache() -> None:
    global _cached_schema
    _cached_schema = None
    logger.info("Schema cache cleared")


class SchemaService:
    """Service for managing database schema information."""

    def __init__(self) -> None:
        self._schema: DatabaseSchema | None = None

    async def get_schema(self, force_refresh: bool = False) -> DatabaseSchema:
        self._schema = await extract_schema(force_refresh=force_refresh)
        return self._schema

    async def get_table_schema(self, table_name: str) -> TableSchema | None:
        if self._schema is None:
            await self.get_schema()

        if self._schema is None:
            return None

        return self._schema.get_table(table_name)

    def get_prompt_context(self) -> str:
        if self._schema is None:
            return ""

        return self._schema.to_prompt_string()

    def clear_cache(self) -> None:
        clear_schema_cache()
        self._schema = None
