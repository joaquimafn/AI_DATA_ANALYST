from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import get_settings
from src.core.database import check_database_connection, check_redis_connection
from src.core.logging import get_logger, setup_logging
from src.models.queries import ErrorResponse, HealthResponse, QueryRequest, QueryResponse

settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(
    title="AI Data Analyst",
    description="NL2SQL system that converts natural language queries to SQL",
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next: Any) -> Any:
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception",
        error=str(exc),
        exc_type=type(exc).__name__,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="An internal error occurred. Please try again later.",
            code="INTERNAL_ERROR",
        ).model_dump(),
    )


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    db_ok = await check_database_connection()
    redis_ok = await check_redis_connection()

    return HealthResponse(
        status="healthy" if db_ok and redis_ok else "degraded",
        database=db_ok,
        redis=redis_ok,
    )


@app.post("/api/v1/query", response_model=QueryResponse, tags=["query"])
async def process_query(request: QueryRequest) -> QueryResponse:
    logger.info("Query request received", question=request.question)

    return QueryResponse(
        sql="SELECT 1 as placeholder",
        explanation="This is a placeholder response. Full pipeline coming in Sprint 3.",
        data=[{"placeholder": "data"}],
        cached=False,
    )


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {"message": "AI Data Analyst API", "version": "0.1.0", "docs": "/docs"}


def create_app() -> FastAPI:
    setup_logging()
    return app
