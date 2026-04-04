from __future__ import annotations

import re

import sqlparse
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import DML, Keyword

from src.core.config import get_settings
from src.core.logging import get_logger
from src.exceptions import SQLValidationError

logger = get_logger(__name__)

BLOCKED_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "GRANT",
    "REVOKE",
    "EXEC",
    "EXECUTE",
    "CALL",
    "INTO",
    "OUTFILE",
    "DUMPFILE",
    "LOAD_FILE",
    "INFORMATION_SCHEMA",
    "PG_CATALOG",
]

BLOCKED_PATTERNS = [
    r";\s*\w+",
    r"UNION\s+(ALL\s+)?SELECT",
    r"--.*$",
    r"/\*.*\*/",
    r"'\s*OR\s+'1'\s*=\s*'1",
    r"'\s*OR\s*'1'\s*=\s*'1",
    r"'\s*;\s*DROP\s+",
]

MAX_QUERY_LENGTH = 5000


class SQLValidator:
    """Validates SQL queries for security and correctness."""

    def __init__(self, max_rows: int | None = None) -> None:
        settings = get_settings()
        self.max_rows = max_rows or settings.max_rows_limit
        self.blocked_keywords = [kw.upper() for kw in BLOCKED_KEYWORDS]
        self.blocked_patterns = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in BLOCKED_PATTERNS]

    def validate(self, sql: str) -> tuple[bool, str]:
        """Validate SQL query. Returns (is_valid, message)."""
        try:
            if not sql or not sql.strip():
                return False, "Empty SQL query"

            if len(sql) > MAX_QUERY_LENGTH:
                return False, f"Query too long (max {MAX_QUERY_LENGTH} characters)"

            normalized_sql = sql.strip()

            if self._contains_blocked_keyword(normalized_sql):
                return False, "Query contains blocked keyword"

            if self._matches_blocked_pattern(normalized_sql):
                return False, "Query contains suspicious pattern"

            if not self._is_valid_select_statement(normalized_sql):
                return False, "Only SELECT statements are allowed"

            if not self._has_valid_structure(normalized_sql):
                return False, "Invalid SQL structure"

            if not self._has_limit_or_appropriate_size(normalized_sql):
                return False, f"Query must have LIMIT clause (max {self.max_rows} rows)"

            return True, "SQL query is valid"

        except Exception as e:
            logger.error("SQL validation error", error=str(e))
            return False, f"SQL validation failed: {e}"

    def _contains_blocked_keyword(self, sql: str) -> bool:
        sql_upper = sql.upper()
        for keyword in self.blocked_keywords:
            pattern = r"\b" + keyword + r"\b"
            if re.search(pattern, sql_upper):
                logger.warning("Blocked keyword found", keyword=keyword)
                return True
        return False

    def _matches_blocked_pattern(self, sql: str) -> bool:
        for pattern in self.blocked_patterns:
            if pattern.search(sql):
                logger.warning("Blocked pattern matched", pattern=str(pattern))
                return True
        return False

    def _is_valid_select_statement(self, sql: str) -> bool:
        parsed = sqlparse.parse(sql)
        if not parsed:
            return False

        for statement in parsed:
            statement_type = statement.get_type()  # type: ignore[no-untyped-call]
            if statement_type != "SELECT":
                if statement_type == "UNKNOWN":
                    first_token = statement.token_first(skip_ws=True, skip_cm=True)  # type: ignore[no-untyped-call]
                    if first_token and first_token.ttype == DML:
                        if first_token.value.upper() != "SELECT":
                            logger.warning("Non-SELECT DML statement", type=statement_type)
                            return False
                else:
                    logger.warning("Non-SELECT statement", type=statement_type)
                    return False

        return True

    def _has_valid_structure(self, sql: str) -> bool:
        parsed = sqlparse.parse(sql)
        if not parsed or len(parsed) > 1:
            return False

        statement = parsed[0]
        if not statement.token_first(skip_ws=True, skip_cm=True):  # type: ignore[no-untyped-call]
            return False

        return True

    def _has_limit_or_appropriate_size(self, sql: str) -> bool:
        sql_upper = sql.upper()
        has_limit = re.search(r"\bLIMIT\b", sql_upper)

        if not has_limit:
            return False

        limit_match = re.search(r"\bLIMIT\s+(\d+)", sql_upper)
        if limit_match:
            limit_value = int(limit_match.group(1))
            if limit_value > self.max_rows:
                logger.warning("LIMIT exceeds max rows", limit=limit_value, max=self.max_rows)
                return False

        return True

    def add_limit_if_missing(self, sql: str) -> str:
        """Add LIMIT clause if missing."""
        if not re.search(r"\bLIMIT\b", sql.upper()):
            return f"{sql.rstrip(';')} LIMIT {self.max_rows}"
        return sql

    def extract_tables(self, sql: str) -> list[str]:
        """Extract table names from SQL query."""
        tables = []
        parsed = sqlparse.parse(sql)

        for statement in parsed:
            from_seen = False
            for token in statement.tokens:
                if from_seen and token.ttype is Keyword:
                    from_seen = False
                    continue
                if token.ttype is Keyword and token.value.upper() in (
                    "FROM",
                    "JOIN",
                    "INNER JOIN",
                    "LEFT JOIN",
                    "RIGHT JOIN",
                    "OUTER JOIN",
                ):
                    from_seen = True
                    continue
                if from_seen:
                    if isinstance(token, Identifier):
                        tables.append(token.get_real_name())  # type: ignore[no-untyped-call]
                    elif isinstance(token, IdentifierList):
                        for identifier in token.get_identifiers():  # type: ignore[no-untyped-call]
                            tables.append(identifier.get_real_name())
                    elif token.ttype is not Keyword:
                        name = token.value.strip()
                        if name and name not in (",", "ON"):
                            name = name.strip("\"'`")
                            if name:
                                tables.append(name)
                    from_seen = False

        return list(set(tables))

    def extract_columns(self, sql: str) -> list[str]:
        """Extract column names from SELECT clause."""
        columns = []
        parsed = sqlparse.parse(sql)

        for statement in parsed:
            select_seen = False
            in_select = True

            for token in statement.tokens:
                if token.ttype is Keyword and token.value.upper() in (
                    "FROM",
                    "WHERE",
                    "GROUP",
                    "HAVING",
                    "ORDER",
                    "LIMIT",
                ):
                    in_select = False

                if in_select and select_seen:
                    if isinstance(token, Identifier):
                        columns.append(token.get_real_name())  # type: ignore[no-untyped-call]
                    elif token.ttype not in (None, DML, Keyword) and token.value.strip() not in (",", "*"):
                        col_name = token.value.strip().strip(",")
                        if col_name and col_name != "*":
                            columns.append(col_name)

                if token.ttype is DML and token.value.upper() == "SELECT":
                    select_seen = True

        return columns


def validate_sql(sql: str) -> str:
    """Validate SQL and raise exception if invalid."""
    validator = SQLValidator()
    is_valid, message = validator.validate(sql)
    if not is_valid:
        logger.warning("SQL validation failed", sql=sql[:100], message=message)
        raise SQLValidationError(message)
    return sql
