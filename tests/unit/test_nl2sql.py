"""Unit tests for NL2SQL service"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_nl2sql_service_initialization():
    from src.services.nl2sql import NL2SQLService

    service = NL2SQLService()
    assert service.llm is not None
    assert service.schema_service is not None
    assert service.validator is not None
    assert service.executor is not None


def test_nl2sql_service_with_custom_dependencies():
    from src.services.nl2sql import NL2SQLService

    llm = MagicMock()
    schema = MagicMock()
    service = NL2SQLService(llm_manager=llm, schema_service=schema)

    assert service.llm is llm
    assert service.schema_service is schema


@pytest.mark.asyncio
async def test_nl2sql_generate_sql():
    from src.models.schema import DatabaseSchema, TableSchema
    from src.services.nl2sql import NL2SQLService

    mock_schema = DatabaseSchema(
        tables=[
            TableSchema(
                name="users",
                columns=[],
            )
        ]
    )

    service = NL2SQLService()

    with patch.object(service.schema_service, "get_schema", new_callable=AsyncMock) as mock_get_schema:
        mock_get_schema.return_value = mock_schema

        with patch.object(service.llm, "generate", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "SELECT * FROM users LIMIT 100"

            sql = await service.generate_sql("Show all users", mock_schema)

            assert "SELECT" in sql.upper()
            assert "users" in sql.lower()


@pytest.mark.asyncio
async def test_nl2sql_explain_sql():
    from src.services.nl2sql import NL2SQLService

    service = NL2SQLService()

    with patch.object(service.llm, "generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = "This query shows all users"

        explanation = await service.explain_sql("SELECT * FROM users")

        assert "users" in explanation.lower()


@pytest.mark.asyncio
async def test_nl2sql_validate_sql_valid():
    from src.services.nl2sql import NL2SQLService

    service = NL2SQLService()
    is_valid, message = await service.validate_sql("SELECT * FROM users LIMIT 10")

    assert is_valid is True


@pytest.mark.asyncio
async def test_nl2sql_validate_sql_invalid():
    from src.services.nl2sql import NL2SQLService

    service = NL2SQLService()
    is_valid, message = await service.validate_sql("DROP TABLE users")

    assert is_valid is False


@pytest.mark.asyncio
async def test_nl2sql_process_question_success():
    from src.models.schema import ColumnSchema, DatabaseSchema, TableSchema
    from src.services.nl2sql import NL2SQLService

    mock_schema = DatabaseSchema(
        tables=[
            TableSchema(
                name="users",
                columns=[
                    ColumnSchema(name="id", data_type="integer"),
                    ColumnSchema(name="name", data_type="varchar"),
                ],
            )
        ]
    )

    service = NL2SQLService()

    with patch.object(service.schema_service, "get_schema", new_callable=AsyncMock) as mock_get_schema:
        mock_get_schema.return_value = mock_schema

        with patch.object(service.llm, "generate", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "SELECT * FROM users LIMIT 100"

            with patch.object(service.executor, "execute", new_callable=AsyncMock) as mock_execute:
                mock_execute.return_value = [{"id": 1, "name": "John"}]

                result = await service.process_question("Show all users")

                assert result["question"] == "Show all users"
                assert "SELECT" in result["sql"]
                assert result["error"] is None
                assert result["data"] == [{"id": 1, "name": "John"}]


@pytest.mark.asyncio
async def test_nl2sql_process_question_invalid_sql():
    from src.models.schema import DatabaseSchema
    from src.services.nl2sql import NL2SQLService

    mock_schema = DatabaseSchema(tables=[])

    service = NL2SQLService()

    with patch.object(service.schema_service, "get_schema", new_callable=AsyncMock) as mock_get_schema:
        mock_get_schema.return_value = mock_schema

        with patch.object(service.llm, "generate", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "DROP TABLE users"

            result = await service.process_question("Delete all users")

            assert result["error"] is not None
            assert "Invalid SQL" in result["error"] or "blocked" in result["error"].lower()


@pytest.mark.asyncio
async def test_nl2sql_process_question_execution_error():
    from src.models.schema import ColumnSchema, DatabaseSchema, TableSchema
    from src.services.nl2sql import NL2SQLService

    mock_schema = DatabaseSchema(
        tables=[
            TableSchema(
                name="users",
                columns=[ColumnSchema(name="id", data_type="integer")],
            )
        ]
    )

    llm = MagicMock()
    schema_service = MagicMock()

    service = NL2SQLService(llm_manager=llm, schema_service=schema_service)

    with patch.object(service.schema_service, "get_schema", new_callable=AsyncMock) as mock_get_schema:
        mock_get_schema.return_value = mock_schema

        with patch.object(service.llm, "generate", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "SELECT * FROM users LIMIT 100"

            with patch.object(service.executor, "execute", new_callable=AsyncMock) as mock_execute:
                mock_execute.side_effect = Exception("Connection failed")

                result = await service.process_question("Show all users")

                assert result["error"] is not None
                assert "Connection failed" in result["error"]
