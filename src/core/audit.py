from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AuditEntry:
    timestamp: str
    query: str
    success: bool
    duration_ms: float
    user_ip: str | None = None
    error: str | None = None
    rows_returned: int | None = None
    cached: bool = False
    request_id: str | None = None


class AuditLogger:
    """Logger for audit trails of SQL query executions."""

    def __init__(self) -> None:
        self.logger = get_logger("audit")

    def log_query(
        self,
        query: str,
        success: bool,
        duration_ms: float,
        user_ip: str | None = None,
        error: str | None = None,
        rows_returned: int | None = None,
        cached: bool = False,
        request_id: str | None = None,
    ) -> None:
        entry = AuditEntry(
            timestamp=datetime.utcnow().isoformat(),
            query=self._sanitize_query(query),
            success=success,
            duration_ms=duration_ms,
            user_ip=user_ip,
            error=error,
            rows_returned=rows_returned,
            cached=cached,
            request_id=request_id,
        )

        if success:
            self.logger.info(
                "SQL query executed",
                **asdict(entry),
            )
        else:
            self.logger.warning(
                "SQL query failed",
                **asdict(entry),
            )

    def _sanitize_query(self, query: str) -> str:
        sensitive_keywords = ["password", "secret", "token", "api_key", "apikey"]
        sanitized = query
        for keyword in sensitive_keywords:
            if keyword.lower() in sanitized.lower():
                sanitized = f"[REDACTED - contains '{keyword}']"
                break
        return sanitized


_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


class AuditContext:
    """Context manager for timing and logging query execution."""

    def __init__(
        self,
        query: str,
        user_ip: str | None = None,
        request_id: str | None = None,
    ) -> None:
        self.query = query
        self.user_ip = user_ip
        self.request_id = request_id
        self.start_time: float = 0
        self.success: bool = False
        self.error: str | None = None
        self.rows_returned: int | None = None
        self.cached: bool = False

    def __enter__(self) -> AuditContext:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        duration_ms = (time.perf_counter() - self.start_time) * 1000

        if exc_type is not None:
            self.success = False
            self.error = str(exc_val) if exc_val else "Unknown error"
        else:
            self.success = True

        audit_logger = get_audit_logger()
        audit_logger.log_query(
            query=self.query,
            success=self.success,
            duration_ms=duration_ms,
            user_ip=self.user_ip,
            error=self.error,
            rows_returned=self.rows_returned,
            cached=self.cached,
            request_id=self.request_id,
        )

    def set_result(self, rows: list[Any], cached: bool = False) -> None:
        self.rows_returned = len(rows) if rows else 0
        self.cached = cached
