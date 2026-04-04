from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=500)
    context: dict[str, Any] | None = None


class QueryResponse(BaseModel):
    sql: str
    explanation: str
    data: list[dict[str, Any]] | None = None
    chart_type: str | None = None
    insight: str | None = None
    cached: bool = False


class ErrorResponse(BaseModel):
    error: str
    code: str
    details: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: str
    database: bool
    redis: bool
    version: str = "0.1.0"
