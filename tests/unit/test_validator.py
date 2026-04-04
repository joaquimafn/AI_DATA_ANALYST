"""Unit tests for SQL validator"""

import pytest

from src.exceptions import SQLValidationError


def test_validator_allows_valid_select():
    from src.services.validator import SQLValidator

    validator = SQLValidator(max_rows=100)
    is_valid, message = validator.validate("SELECT * FROM users WHERE id = 1 LIMIT 10")
    assert is_valid is True
    assert "valid" in message.lower()


def test_validator_blocks_drop():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    is_valid, message = validator.validate("DROP TABLE users")
    assert is_valid is False
    assert "blocked" in message.lower() or "not" in message.lower()


def test_validator_blocks_delete():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    is_valid, message = validator.validate("DELETE FROM users WHERE id = 1")
    assert is_valid is False


def test_validator_blocks_insert():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    is_valid, message = validator.validate("INSERT INTO users (name) VALUES ('test')")
    assert is_valid is False


def test_validator_blocks_update():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    is_valid, message = validator.validate("UPDATE users SET name = 'test'")
    assert is_valid is False


def test_validator_requires_limit():
    from src.services.validator import SQLValidator

    validator = SQLValidator(max_rows=100)
    is_valid, message = validator.validate("SELECT * FROM users")
    assert is_valid is False
    assert "LIMIT" in message


def test_validator_allows_limit():
    from src.services.validator import SQLValidator

    validator = SQLValidator(max_rows=100)
    is_valid, message = validator.validate("SELECT * FROM users LIMIT 50")
    assert is_valid is True


def test_validator_rejects_limit_exceeding_max():
    from src.services.validator import SQLValidator

    validator = SQLValidator(max_rows=100)
    is_valid, message = validator.validate("SELECT * FROM users LIMIT 200")
    assert is_valid is False


def test_validator_rejects_empty_query():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    is_valid, message = validator.validate("")
    assert is_valid is False
    assert "empty" in message.lower()


def test_validator_rejects_sql_injection_attempt():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    is_valid, message = validator.validate("SELECT * FROM users; DROP TABLE users;")
    assert is_valid is False


def test_validator_rejects_union_select():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    is_valid, message = validator.validate("SELECT * FROM users UNION SELECT * FROM admins")
    assert is_valid is False


def test_validator_blocks_information_schema():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    is_valid, message = validator.validate("SELECT * FROM information_schema.tables")
    assert is_valid is False


def test_validator_add_limit_if_missing():
    from src.services.validator import SQLValidator

    validator = SQLValidator(max_rows=1000)
    sql = validator.add_limit_if_missing("SELECT * FROM users")
    assert "LIMIT 1000" in sql


def test_validator_does_not_add_duplicate_limit():
    from src.services.validator import SQLValidator

    validator = SQLValidator(max_rows=1000)
    sql = validator.add_limit_if_missing("SELECT * FROM users LIMIT 50")
    assert sql.count("LIMIT") == 1


def test_validate_sql_raises_exception():
    from src.services.validator import validate_sql

    with pytest.raises(SQLValidationError):
        validate_sql("DROP TABLE users")


def test_validate_sql_returns_sql_when_valid():
    from src.services.validator import validate_sql

    result = validate_sql("SELECT * FROM users LIMIT 10")
    assert result == "SELECT * FROM users LIMIT 10"


def test_validator_allows_complex_join():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    sql = """
        SELECT u.name, o.order_date, o.total
        FROM users u
        INNER JOIN orders o ON u.id = o.user_id
        WHERE o.total > 100
        LIMIT 50
    """
    is_valid, _ = validator.validate(sql)
    assert is_valid is True


def test_validator_allows_aggregates():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    sql = "SELECT COUNT(*), SUM(total) FROM orders GROUP BY user_id LIMIT 100"
    is_valid, _ = validator.validate(sql)
    assert is_valid is True


def test_validator_allows_subquery():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    sql = "SELECT * FROM (SELECT id, name FROM users) AS subq LIMIT 10"
    is_valid, _ = validator.validate(sql)
    assert is_valid is True


def test_validator_blocks_multiple_statements():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    is_valid, _ = validator.validate("SELECT 1; SELECT 2")
    assert is_valid is False


def test_validator_respects_max_query_length():
    from src.services.validator import SQLValidator

    validator = SQLValidator()
    long_query = "SELECT " + "a" * 10000
    is_valid, message = validator.validate(long_query)
    assert is_valid is False
    assert "too long" in message.lower()
