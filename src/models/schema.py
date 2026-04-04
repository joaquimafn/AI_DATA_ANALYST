from __future__ import annotations

from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    name: str
    data_type: str
    is_nullable: bool = True
    is_primary_key: bool = False
    foreign_key: str | None = None


class TableSchema(BaseModel):
    name: str
    columns: list[ColumnSchema] = Field(default_factory=list)
    row_count: int | None = None

    def get_column(self, column_name: str) -> ColumnSchema | None:
        for col in self.columns:
            if col.name == column_name:
                return col
        return None


class DatabaseSchema(BaseModel):
    tables: list[TableSchema] = Field(default_factory=list)
    version: str | None = None

    def get_table(self, table_name: str) -> TableSchema | None:
        for table in self.tables:
            if table.name == table_name:
                return table
        return None

    def get_table_names(self) -> list[str]:
        return [t.name for t in self.tables]

    def to_prompt_string(self) -> str:
        lines = []
        for table in self.tables:
            col_lines = []
            for col in table.columns:
                nullable = "NULL" if col.is_nullable else "NOT NULL"
                pk = " PK" if col.is_primary_key else ""
                fk = f" FK->{col.foreign_key}" if col.foreign_key else ""
                col_lines.append(f"  - {col.name}: {col.data_type} ({nullable}){pk}{fk}")
            lines.append(f"Table: {table.name}")
            if table.row_count is not None:
                lines.append(f"  Rows: {table.row_count}")
            lines.extend(col_lines)
        return "\n".join(lines)
