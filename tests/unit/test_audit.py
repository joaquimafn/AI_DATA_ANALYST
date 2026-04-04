"""Unit tests for Audit Logger"""

from unittest.mock import patch

from src.core.audit import AuditContext, AuditEntry, AuditLogger, get_audit_logger


def test_audit_logger_initialization():
    logger = AuditLogger()
    assert logger.logger is not None


def test_get_audit_logger_singleton():
    logger1 = get_audit_logger()
    logger2 = get_audit_logger()
    assert logger1 is logger2


def test_audit_entry_creation():
    entry = AuditEntry(
        timestamp="2024-01-01T00:00:00",
        query="SELECT * FROM users",
        success=True,
        duration_ms=100.5,
    )
    assert entry.query == "SELECT * FROM users"
    assert entry.success is True
    assert entry.duration_ms == 100.5


def test_audit_entry_with_all_fields():
    entry = AuditEntry(
        timestamp="2024-01-01T00:00:00",
        query="SELECT * FROM users",
        success=False,
        duration_ms=100.5,
        user_ip="192.168.1.1",
        error="Connection timeout",
        rows_returned=0,
        cached=False,
        request_id="req-123",
    )
    assert entry.error == "Connection timeout"
    assert entry.user_ip == "192.168.1.1"


def test_sanitize_query_removes_password():
    logger = AuditLogger()
    query = "SELECT * FROM users WHERE password = 'secret123'"
    sanitized = logger._sanitize_query(query)
    assert sanitized == "[REDACTED - contains 'password']"


def test_sanitize_query_removes_api_key():
    logger = AuditLogger()
    query = "SELECT * FROM config WHERE api_key = 'key-123'"
    sanitized = logger._sanitize_query(query)
    assert sanitized == "[REDACTED - contains 'api_key']"


def test_sanitize_query_preserves_normal_query():
    logger = AuditLogger()
    query = "SELECT id, name FROM products WHERE active = true"
    sanitized = logger._sanitize_query(query)
    assert sanitized == query


def test_sanitize_query_case_insensitive():
    logger = AuditLogger()
    query = "SELECT * FROM config WHERE PASSWORD = 'secret'"
    sanitized = logger._sanitize_query(query)
    assert "[REDACTED" in sanitized


def test_log_query_success():
    logger = AuditLogger()

    with patch.object(logger.logger, "info") as mock_info:
        logger.log_query(
            query="SELECT 1",
            success=True,
            duration_ms=50.0,
        )
        mock_info.assert_called_once()
        call_args = mock_info.call_args[1]
        assert call_args["success"] is True
        assert call_args["query"] == "SELECT 1"


def test_log_query_failure():
    logger = AuditLogger()

    with patch.object(logger.logger, "warning") as mock_warning:
        logger.log_query(
            query="SELECT 1",
            success=False,
            duration_ms=50.0,
            error="Connection refused",
        )
        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[1]
        assert call_args["success"] is False
        assert call_args["error"] == "Connection refused"


class TestAuditContext:
    def test_context_manager_initialization(self):
        ctx = AuditContext(query="SELECT 1")
        assert ctx.query == "SELECT 1"
        assert ctx.success is False

    def test_context_manager_sets_duration_on_exit(self):
        ctx = AuditContext(query="SELECT 1")

        with patch("src.core.audit.get_audit_logger") as mock_get_logger:
            mock_logger = AuditLogger()
            mock_get_logger.return_value = mock_logger

            with patch.object(mock_logger, "log_query"):
                import time

                with ctx:
                    time.sleep(0.01)

        assert ctx.start_time > 0

    def test_context_manager_logs_on_exception(self):
        ctx = AuditContext(query="SELECT 1")

        with patch("src.core.audit.get_audit_logger") as mock_get_logger:
            mock_logger = AuditLogger()
            mock_get_logger.return_value = mock_logger

            with patch.object(mock_logger, "log_query"):
                try:
                    with ctx:
                        raise ValueError("Test error")
                except ValueError:
                    pass

        assert ctx.success is False
        assert ctx.error == "Test error"

    def test_set_result(self):
        ctx = AuditContext(query="SELECT 1")
        ctx.set_result([{"a": 1}, {"a": 2}])
        assert ctx.rows_returned == 2
        assert ctx.cached is False

    def test_set_result_with_cached(self):
        ctx = AuditContext(query="SELECT 1")
        ctx.set_result([{"a": 1}], cached=True)
        assert ctx.rows_returned == 1
        assert ctx.cached is True
