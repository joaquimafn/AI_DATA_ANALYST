"""Test fixtures and configuration"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from src.main import app

    return TestClient(app)


@pytest.fixture
def sample_schema():
    from src.models.schema import ColumnSchema, DatabaseSchema, TableSchema

    return DatabaseSchema(
        tables=[
            TableSchema(
                name="products",
                columns=[
                    ColumnSchema(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
                    ColumnSchema(name="name", data_type="varchar", is_nullable=False),
                    ColumnSchema(name="price", data_type="decimal"),
                    ColumnSchema(name="category", data_type="varchar"),
                ],
                row_count=100,
            ),
            TableSchema(
                name="orders",
                columns=[
                    ColumnSchema(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
                    ColumnSchema(name="product_id", data_type="integer", foreign_key="products.id"),
                    ColumnSchema(name="quantity", data_type="integer"),
                    ColumnSchema(name="region", data_type="varchar"),
                ],
                row_count=500,
            ),
        ],
        version="1.0",
    )
