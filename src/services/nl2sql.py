from __future__ import annotations

from typing import Any

from src.core.audit import AuditContext
from src.core.config import get_settings
from src.core.logging import get_logger
from src.exceptions import SQLValidationError
from src.models.schema import DatabaseSchema
from src.services.executor import QueryExecutor
from src.services.insight import InsightService, create_insight_service
from src.services.llm import LLMManager, create_llm_manager
from src.services.schema import SchemaService
from src.services.validator import SQLValidator
from src.utils.cache import CacheService, generate_cache_key

logger = get_logger(__name__)

SQL_GENERATION_PROMPT = """You are a SQL generator for a PostgreSQL database.

Rules:
- Only generate SELECT statements
- Never modify data (no INSERT, UPDATE, DELETE, DROP, etc.)
- Use only the tables and columns provided in the schema
- Always add LIMIT clause (max {max_rows} rows)
- Use proper JOIN syntax with aliases
- Wrap table and column names in double quotes if they contain special characters

Schema:
{schema}

User question:
{question}

Generate SQL query:"""

SQL_EXPLANATION_PROMPT = """Explain the following SQL query in simple terms, as if explaining to a non-technical business user.
Focus on WHAT the query returns, not the technical details.

SQL: {sql}

Explanation:"""


class NL2SQLService:
    """Service that converts natural language to SQL."""

    def __init__(
        self,
        llm_manager: LLMManager | None = None,
        schema_service: SchemaService | None = None,
        insight_service: InsightService | None = None,
        cache_enabled: bool = True,
    ) -> None:
        self.llm = llm_manager or create_llm_manager()
        self.schema_service = schema_service or SchemaService()
        self.insight_service = insight_service or create_insight_service()
        self.validator = SQLValidator()
        self.executor = QueryExecutor()
        self.cache_enabled = cache_enabled
        self.cache = CacheService(prefix="nl2sql") if cache_enabled else None
        settings = get_settings()
        self.cache_ttl = settings.cache_ttl_seconds

    async def _get_cached_result(self, question: str) -> dict[str, Any] | None:
        if not self.cache:
            return None

        cache_key = generate_cache_key(
            "nl2sql",
            question,
            prefix="nl2sql",
        )
        cached = await self.cache.get_json(cache_key)
        if cached:
            logger.info("Returning cached result", question=question[:50])
            cached["cached"] = True
        return cached

    async def _cache_result(self, question: str, result: dict[str, Any]) -> None:
        if not self.cache:
            return

        cache_key = generate_cache_key(
            "nl2sql",
            question,
            prefix="nl2sql",
        )
        await self.cache.set_json(cache_key, result, self.cache_ttl)
        logger.debug("Result cached", question=question[:50])

    async def generate_sql(self, question: str, schema: DatabaseSchema) -> str:
        """Generate SQL from a natural language question."""
        prompt = SQL_GENERATION_PROMPT.format(
            schema=schema.to_prompt_string(),
            question=question,
            max_rows=self.validator.max_rows,
        )

        system_prompt = "You are a SQL expert. Generate only SQL, no explanations."

        sql = await self.llm.generate(prompt, system_prompt)
        sql = sql.strip()

        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        sql = sql.strip()

        logger.info("Generated SQL", sql=sql[:100])
        return sql

    async def explain_sql(self, sql: str) -> str:
        """Generate explanation for SQL query."""
        prompt = SQL_EXPLANATION_PROMPT.format(sql=sql)
        explanation = await self.llm.generate(prompt)
        return explanation.strip()

    async def validate_sql(self, sql: str) -> tuple[bool, str]:
        """Validate generated SQL."""
        return self.validator.validate(sql)

    async def execute_sql(self, sql: str) -> list[dict[str, Any]]:
        """Execute validated SQL and return results."""
        is_valid, message = self.validator.validate(sql)
        if not is_valid:
            raise SQLValidationError(f"Invalid SQL: {message}")

        sql = self.validator.add_limit_if_missing(sql)

        with AuditContext(query=sql) as audit_ctx:
            result = await self.executor.execute(sql)
            audit_ctx.set_result(result)
            return result

    async def process_question(self, question: str) -> dict[str, Any]:
        """Process a natural language question end-to-end."""
        logger.info("Processing question", question=question)

        cached_result = await self._get_cached_result(question)
        if cached_result:
            return cached_result

        schema = await self.schema_service.get_schema()

        sql = await self.generate_sql(question, schema)

        is_valid, validation_message = await self.validate_sql(sql)
        if not is_valid:
            result = {
                "question": question,
                "sql": sql,
                "explanation": None,
                "data": None,
                "insight": None,
                "chart_type": None,
                "error": validation_message,
                "cached": False,
            }
            await self._cache_result(question, result)
            return result

        explanation = await self.explain_sql(sql)

        try:
            data = await self.execute_sql(sql)
        except Exception as e:
            logger.error("Query execution failed", error=str(e))
            error_result: dict[str, Any] = {
                "question": question,
                "sql": sql,
                "explanation": explanation,
                "data": None,
                "insight": None,
                "chart_type": None,
                "error": str(e),
                "cached": False,
            }
            await self._cache_result(question, error_result)
            return error_result

        insight = await self.insight_service.generate_insight(
            question=question,
            sql=sql,
            data=data,
        )

        chart_type = self.insight_service.suggest_chart_type(
            data=data,
            question=question,
        )

        success_result: dict[str, Any] = {
            "question": question,
            "sql": sql,
            "explanation": explanation,
            "data": data,
            "insight": insight,
            "chart_type": chart_type,
            "error": None,
            "cached": False,
        }

        await self._cache_result(question, success_result)

        return success_result
