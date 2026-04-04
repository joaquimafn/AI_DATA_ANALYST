"""Unit tests for core config"""


def test_settings_default_values():
    from src.core.config import Settings

    settings = Settings()
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
    assert settings.cache_ttl_seconds == 3600
    assert settings.query_timeout_seconds == 5
    assert settings.max_rows_limit == 1000
    assert settings.rate_limit_per_minute == 60


def test_settings_rate_limit_default():
    from src.core.config import Settings

    settings = Settings()
    assert settings.rate_limit_per_minute == 60


def test_settings_computed_database_url():
    from src.core.config import Settings

    settings = Settings()
    assert "postgresql+asyncpg://" in settings.computed_database_url
    assert "ai_analyst" in settings.computed_database_url
