from __future__ import annotations

from typing import Any

from src.core.logging import get_logger
from src.services.llm import LLMManager, create_llm_manager

logger = get_logger(__name__)

INSIGHT_SYSTEM_PROMPT = """Você é um analista de dados especialista.
Analise os resultados de queries SQL e forneça insights de negócio claros e acionáveis.
Suas análises devem ser:
- Concisas (máximo 3-4 frases)
- Focadas em padrões e tendências
- Acionáveis quando possível
- Em português brasileiro
"""

INSIGHT_GENERATION_PROMPT = """Analise os seguintes dados e forneça um insight de negócio.

Pergunta original: {question}
Query SQL executada: {sql}
Dados retornados: {data}

Forneça um insight que:
1. Identifique o principal padrão/tendência nos dados
2. Quantifique quando possível (ex: "representa X% do total")
3. Sugira uma ação de negócio se aplicável

Insight em português brasileiro (máximo 2-3 frases):"""


class InsightService:
    """Service for generating insights from query results."""

    def __init__(
        self,
        llm_manager: LLMManager | None = None,
        enabled: bool = True,
    ) -> None:
        self.llm = llm_manager or create_llm_manager()
        self.enabled = enabled

    def _format_data_for_prompt(self, data: list[dict[str, Any]]) -> str:
        """Format query data for the prompt."""
        if not data:
            return "Nenhum dado retornado"

        if len(data) > 10:
            preview = data[:10]
            formatted = ", ".join(str(row) for row in preview)
            return f"{formatted}... (+{len(data) - 10} registros)"

        return ", ".join(str(row) for row in data)

    async def generate_insight(
        self,
        question: str,
        sql: str,
        data: list[dict[str, Any]],
    ) -> str | None:
        """Generate an insight from query results."""
        if not self.enabled:
            logger.debug("Insight generation disabled")
            return None

        if not data:
            logger.debug("No data to generate insight from")
            return None

        try:
            formatted_data = self._format_data_for_prompt(data)

            prompt = INSIGHT_GENERATION_PROMPT.format(
                question=question,
                sql=sql,
                data=formatted_data,
            )

            logger.info("Generating insight", question=question[:50])

            insight = await self.llm.generate(
                prompt=prompt,
                system_prompt=INSIGHT_SYSTEM_PROMPT,
            )

            logger.info("Insight generated successfully")
            return insight.strip()

        except Exception as e:
            logger.warning("Insight generation failed", error=str(e))
            return None

    def suggest_chart_type(
        self,
        data: list[dict[str, Any]],
        question: str,
    ) -> str | None:
        """Suggest an appropriate chart type based on data and question."""
        if not data:
            return None

        question_lower = question.lower()
        data_keys = list(data[0].keys()) if data else []

        has_numeric = any(isinstance(data[0].get(k), (int, float)) for k in data_keys)

        if any(word in question_lower for word in ["tendência", "evolução", "crescimento", "ao longo"]):
            return "line"

        if any(word in question_lower for word in ["comparar", "comparação", "diferença"]):
            return "bar"

        if any(word in question_lower for word in ["distribuição", "composição", "percentual"]):
            return "pie"

        if has_numeric and len(data) <= 10:
            return "bar"

        return "table"


def create_insight_service(enabled: bool = True) -> InsightService:
    """Factory function to create an InsightService."""
    return InsightService(enabled=enabled)
