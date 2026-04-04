"""Unit tests for models"""

import pytest


def test_query_request_valid():
    from src.models.queries import QueryRequest

    req = QueryRequest(question="What are the top selling products?")
    assert req.question == "What are the top selling products?"
    assert req.context is None


def test_query_request_with_context():
    from src.models.queries import QueryRequest

    req = QueryRequest(question="Show sales", context={"year": 2024})
    assert req.context == {"year": 2024}


def test_query_request_too_short():
    from pydantic import ValidationError

    from src.models.queries import QueryRequest

    with pytest.raises(ValidationError):
        QueryRequest(question="Hi")


def test_query_request_too_long():
    from pydantic import ValidationError

    from src.models.queries import QueryRequest

    with pytest.raises(ValidationError):
        QueryRequest(question="x" * 501)


def test_query_response_defaults():
    from src.models.queries import QueryResponse

    resp = QueryResponse(sql="SELECT 1", explanation="Test query")
    assert resp.sql == "SELECT 1"
    assert resp.cached is False
    assert resp.data is None
    assert resp.chart_type is None
    assert resp.insight is None


def test_error_response():
    from src.models.queries import ErrorResponse

    err = ErrorResponse(error="Test error", code="TEST_ERROR")
    assert err.error == "Test error"
    assert err.code == "TEST_ERROR"
    assert err.details is None


def test_health_response():
    from src.models.queries import HealthResponse

    health = HealthResponse(status="healthy", database=True, redis=True)
    assert health.status == "healthy"
    assert health.database is True
    assert health.redis is True
    assert health.version == "0.1.0"


def test_table_schema_get_table(sample_schema):
    table = sample_schema.get_table("products")
    assert table is not None
    assert table.name == "products"
    assert len(table.columns) == 4


def test_table_schema_get_table_not_found(sample_schema):
    table = sample_schema.get_table("nonexistent")
    assert table is None


def test_database_schema_to_prompt_string(sample_schema):
    prompt = sample_schema.to_prompt_string()
    assert "Table: products" in prompt
    assert "Table: orders" in prompt
    assert "id: integer" in prompt
    assert "name: varchar" in prompt


def test_database_schema_get_table_names(sample_schema):
    names = sample_schema.get_table_names()
    assert names == ["products", "orders"]
