"""Unit tests for exceptions"""



def test_base_exception():
    from src.exceptions import AIDataAnalystError

    err = AIDataAnalystError("Test error", code="TEST_ERROR")
    assert err.message == "Test error"
    assert err.code == "TEST_ERROR"
    assert str(err) == "Test error"


def test_base_exception_default_code():
    from src.exceptions import AIDataAnalystError

    err = AIDataAnalystError("Test error")
    assert err.code == "AI_DATA_ANALYST_ERROR"


def test_schema_extraction_error():
    from src.exceptions import SchemaExtractionError

    err = SchemaExtractionError("Failed to extract schema")
    assert err.message == "Failed to extract schema"
    assert err.code == "SCHEMA_EXTRACTION_ERROR"


def test_database_connection_error():
    from src.exceptions import DatabaseConnectionError

    err = DatabaseConnectionError("Connection failed")
    assert err.message == "Connection failed"
    assert err.code == "DATABASE_CONNECTION_ERROR"


def test_sql_validation_error():
    from src.exceptions import SQLValidationError

    err = SQLValidationError("Invalid SQL")
    assert err.message == "Invalid SQL"
    assert err.code == "SQL_VALIDATION_ERROR"


def test_query_execution_error():
    from src.exceptions import QueryExecutionError

    err = QueryExecutionError("Query timeout")
    assert err.message == "Query timeout"
    assert err.code == "QUERY_EXECUTION_ERROR"


def test_llm_generation_error():
    from src.exceptions import LLMGenerationError

    err = LLMGenerationError("LLM unavailable")
    assert err.message == "LLM unavailable"
    assert err.code == "LLM_GENERATION_ERROR"


def test_cache_error():
    from src.exceptions import CacheError

    err = CacheError("Cache miss")
    assert err.message == "Cache miss"
    assert err.code == "CACHE_ERROR"


def test_rate_limit_error():
    from src.exceptions import RateLimitError

    err = RateLimitError("Rate limit exceeded")
    assert err.message == "Rate limit exceeded"
    assert err.code == "RATE_LIMIT_ERROR"


def test_exception_inheritance():
    from src.exceptions import (
        AIDataAnalystError,
        CacheError,
        DatabaseConnectionError,
        LLMGenerationError,
        QueryExecutionError,
        RateLimitError,
        SchemaExtractionError,
        SQLValidationError,
    )

    assert issubclass(SchemaExtractionError, AIDataAnalystError)
    assert issubclass(DatabaseConnectionError, AIDataAnalystError)
    assert issubclass(SQLValidationError, AIDataAnalystError)
    assert issubclass(QueryExecutionError, AIDataAnalystError)
    assert issubclass(LLMGenerationError, AIDataAnalystError)
    assert issubclass(CacheError, AIDataAnalystError)
    assert issubclass(RateLimitError, AIDataAnalystError)
