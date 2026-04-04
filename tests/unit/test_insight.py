"""Unit tests for Insight Service"""

from unittest.mock import AsyncMock

import pytest


def test_insight_service_initialization():
    from src.services.insight import InsightService

    service = InsightService()
    assert service.enabled is True


def test_insight_service_disabled():
    from src.services.insight import InsightService

    service = InsightService(enabled=False)
    assert service.enabled is False


def test_create_insight_service():
    from src.services.insight import create_insight_service

    service = create_insight_service()
    assert service.enabled is True


def test_create_insight_service_disabled():
    from src.services.insight import create_insight_service

    service = create_insight_service(enabled=False)
    assert service.enabled is False


def test_format_data_for_prompt_empty():
    from src.services.insight import InsightService

    service = InsightService()
    result = service._format_data_for_prompt([])
    assert result == "Nenhum dado retornado"


def test_format_data_for_prompt_single_row():
    from src.services.insight import InsightService

    service = InsightService()
    data = [{"name": "Product A", "quantity": 100}]
    result = service._format_data_for_prompt(data)
    assert "Product A" in result
    assert "100" in result


def test_format_data_for_prompt_multiple_rows():
    from src.services.insight import InsightService

    service = InsightService()
    data = [
        {"name": "Product A", "quantity": 100},
        {"name": "Product B", "quantity": 200},
    ]
    result = service._format_data_for_prompt(data)
    assert "Product A" in result
    assert "Product B" in result


def test_format_data_for_prompt_truncation():
    from src.services.insight import InsightService

    service = InsightService()
    data = [{"id": i} for i in range(15)]
    result = service._format_data_for_prompt(data)
    assert "+5 registros" in result


@pytest.mark.asyncio
async def test_generate_insight_returns_none_when_disabled():
    from src.services.insight import InsightService

    service = InsightService(enabled=False)
    result = await service.generate_insight(
        question="test",
        sql="SELECT 1",
        data=[{"a": 1}],
    )
    assert result is None


@pytest.mark.asyncio
async def test_generate_insight_returns_none_when_no_data():
    from src.services.insight import InsightService

    service = InsightService()
    result = await service.generate_insight(
        question="test",
        sql="SELECT 1",
        data=[],
    )
    assert result is None


@pytest.mark.asyncio
async def test_generate_insight_success():
    from src.services.insight import InsightService

    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "O produto A representa 50% das vendas totais."

    service = InsightService(llm_manager=mock_llm)
    result = await service.generate_insight(
        question="Quais produtos mais vendem?",
        sql="SELECT product_name, SUM(quantity) FROM sales GROUP BY product_name",
        data=[{"product_name": "A", "total": 100}],
    )

    assert result == "O produto A representa 50% das vendas totais."
    mock_llm.generate.assert_called_once()


@pytest.mark.asyncio
async def test_generate_insight_handles_llm_error():
    from src.services.insight import InsightService

    mock_llm = AsyncMock()
    mock_llm.generate.side_effect = Exception("LLM Error")

    service = InsightService(llm_manager=mock_llm)
    result = await service.generate_insight(
        question="test",
        sql="SELECT 1",
        data=[{"a": 1}],
    )

    assert result is None


def test_suggest_chart_type_returns_none_for_empty_data():
    from src.services.insight import InsightService

    service = InsightService()
    result = service.suggest_chart_type([], "test question")
    assert result is None


def test_suggest_chart_type_line_for_trend():
    from src.services.insight import InsightService

    service = InsightService()
    data = [{"date": "2024-01", "value": 100}]
    result = service.suggest_chart_type(data, "qual a tendência de vendas?")
    assert result == "line"


def test_suggest_chart_type_bar_for_comparison():
    from src.services.insight import InsightService

    service = InsightService()
    data = [{"product": "A", "sales": 100}]
    result = service.suggest_chart_type(data, "comparar produtos")
    assert result == "bar"


def test_suggest_chart_type_pie_for_distribution():
    from src.services.insight import InsightService

    service = InsightService()
    data = [{"region": "Norte", "sales": 100}]
    result = service.suggest_chart_type(data, "distribuição por região")
    assert result == "pie"


def test_suggest_chart_type_default_bar():
    from src.services.insight import InsightService

    service = InsightService()
    data = [{"id": 1, "value": 100}]
    result = service.suggest_chart_type(data, "alguma pergunta")
    assert result == "bar"


def test_suggest_chart_type_table_fallback():
    from src.services.insight import InsightService

    service = InsightService()
    data = [{"id": i, "name": f"Item {i}"} for i in range(20)]
    result = service.suggest_chart_type(data, "listar todos")
    assert result == "table"
