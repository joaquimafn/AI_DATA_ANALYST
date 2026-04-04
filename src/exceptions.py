class AIDataAnalystError(Exception):
    """Base exception for AI Data Analyst."""

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code or "AI_DATA_ANALYST_ERROR"
        super().__init__(self.message)


class SchemaExtractionError(AIDataAnalystError):
    """Raised when schema extraction from database fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="SCHEMA_EXTRACTION_ERROR")


class DatabaseConnectionError(AIDataAnalystError):
    """Raised when database connection fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="DATABASE_CONNECTION_ERROR")


class SQLValidationError(AIDataAnalystError):
    """Raised when SQL fails security validation."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="SQL_VALIDATION_ERROR")


class QueryExecutionError(AIDataAnalystError):
    """Raised when query execution fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="QUERY_EXECUTION_ERROR")


class LLMGenerationError(AIDataAnalystError):
    """Raised when LLM generation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="LLM_GENERATION_ERROR")


class CacheError(AIDataAnalystError):
    """Raised when cache operations fail."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CACHE_ERROR")


class RateLimitError(AIDataAnalystError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="RATE_LIMIT_ERROR")
