"""Unit tests for schema service"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_column_schema_creation():
    from src.models.schema import ColumnSchema

    col = ColumnSchema(
        name="id",
        data_type="integer",
        is_nullable=False,
        is_primary_key=True,
    )
    assert col.name == "id"
    assert col.data_type == "integer"
    assert col.is_nullable is False
    assert col.is_primary_key is True
    assert col.foreign_key is None


def test_column_schema_with_foreign_key():
    from src.models.schema import ColumnSchema

    col = ColumnSchema(
        name="user_id",
        data_type="integer",
        is_nullable=True,
        foreign_key="users.id",
    )
    assert col.foreign_key == "users.id"


def test_table_schema_creation():
    from src.models.schema import ColumnSchema, TableSchema

    table = TableSchema(
        name="users",
        columns=[
            ColumnSchema(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
            ColumnSchema(name="email", data_type="varchar", is_nullable=False),
        ],
        row_count=100,
    )
    assert table.name == "users"
    assert len(table.columns) == 2
    assert table.row_count == 100


def test_table_schema_get_column():
    from src.models.schema import ColumnSchema, TableSchema

    table = TableSchema(
        name="users",
        columns=[
            ColumnSchema(name="id", data_type="integer"),
            ColumnSchema(name="email", data_type="varchar"),
        ],
    )
    col = table.get_column("id")
    assert col is not None
    assert col.name == "id"

    not_found = table.get_column("nonexistent")
    assert not_found is None


def test_database_schema_creation():
    from src.models.schema import ColumnSchema, DatabaseSchema, TableSchema

    schema = DatabaseSchema(
        tables=[
            TableSchema(
                name="users",
                columns=[ColumnSchema(name="id", data_type="integer")],
            ),
        ],
        version="1.0",
    )
    assert len(schema.tables) == 1
    assert schema.version == "1.0"


def test_database_schema_get_table():
    from src.models.schema import ColumnSchema, DatabaseSchema, TableSchema

    schema = DatabaseSchema(
        tables=[
            TableSchema(
                name="users",
                columns=[ColumnSchema(name="id", data_type="integer")],
            ),
            TableSchema(
                name="orders",
                columns=[ColumnSchema(name="id", data_type="integer")],
            ),
        ],
    )

    users = schema.get_table("users")
    assert users is not None
    assert users.name == "users"

    orders = schema.get_table("orders")
    assert orders is not None

    not_found = schema.get_table("nonexistent")
    assert not_found is None


def test_database_schema_get_table_names():
    from src.models.schema import DatabaseSchema, TableSchema

    schema = DatabaseSchema(
        tables=[
            TableSchema(name="users", columns=[]),
            TableSchema(name="orders", columns=[]),
            TableSchema(name="products", columns=[]),
        ],
    )

    names = schema.get_table_names()
    assert names == ["users", "orders", "products"]


def test_database_schema_to_prompt_string():
    from src.models.schema import ColumnSchema, DatabaseSchema, TableSchema

    schema = DatabaseSchema(
        tables=[
            TableSchema(
                name="products",
                columns=[
                    ColumnSchema(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
                    ColumnSchema(name="name", data_type="varchar", is_nullable=False),
                    ColumnSchema(name="price", data_type="decimal", is_nullable=True),
                ],
                row_count=100,
            ),
        ],
    )

    prompt = schema.to_prompt_string()
    assert "Table: products" in prompt
    assert "Rows: 100" in prompt
    assert "id: integer" in prompt
    assert "name: varchar" in prompt
    assert "price: decimal" in prompt
    assert "NOT NULL" in prompt
    assert "PK" in prompt


def test_schema_service_initialization():
    from src.services.schema import SchemaService

    service = SchemaService()
    assert service._schema is None


def test_schema_service_get_prompt_context_empty():
    from src.services.schema import SchemaService

    service = SchemaService()
    context = service.get_prompt_context()
    assert context == ""


def test_clear_schema_cache():
    from src.services.schema import clear_schema_cache

    clear_schema_cache()


def test_get_cached_schema_returns_none_initially():
    from src.services.schema import clear_schema_cache, get_cached_schema

    clear_schema_cache()
    assert get_cached_schema() is None


@pytest.mark.asyncio
async def test_schema_service_get_schema_returns_database_schema():
    from src.services.schema import SchemaService

    mock_schema = MagicMock()
    mock_schema.to_prompt_string.return_value = "mock prompt"

    with patch("src.services.schema.extract_schema", new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = mock_schema

        service = SchemaService()
        result = await service.get_schema()

        assert result == mock_schema
        assert service._schema == mock_schema


@pytest.mark.asyncio
async def test_schema_service_clear_cache():
    from src.services.schema import SchemaService

    mock_schema = MagicMock()

    with patch("src.services.schema.extract_schema", new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = mock_schema

        service = SchemaService()
        await service.get_schema()
        assert service._schema is not None

        service.clear_cache()
        assert service._schema is None
