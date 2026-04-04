.PHONY: help install dev test lint typecheck security security-deps check clean run docker-up docker-down

# Cores para output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m # No Color

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Instalar dependências
install: ## Instala dependências principais
	uv sync

install-dev: ## Instala dependências de desenvolvimento
	uv sync --extra dev

install-security: ## Instala ferramentas de segurança
	uv sync --extra security

# Testes
test: ## Roda todos os testes
	pytest tests/unit/ -v

test-coverage: ## Roda testes com coverage
	pytest --cov=src --cov-report=html --cov-report=term

# Linting e formatação
lint: ## Verifica código com ruff
	ruff check .

lint-fix: ## Corrige problemas de lint automaticamente
	ruff check . --fix

format: ## Formata código
	ruff format .
	isort .

# Type checking
typecheck: ## Verifica tipos com mypy
	mypy src/

# Segurança
security: ## Análise estática de segurança (código)
	bandit -r src/ -f screen

security-deps: ## Verifica vulnerabilidades em dependências
	safety check --output=text

pip-audit: ## Auditoria completa de dependências
	pip-audit

# Verificação completa (antes de commit)
check: lint typecheck security test ## Executa todas as verificações

# Limpeza
clean: ## Remove arquivos temporários
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true

# Docker
docker-up: ## Sobe containers Docker (Postgres + Redis)
	docker-compose up -d

docker-down: ## Para containers Docker
	docker-compose down

docker-logs: ## Mostra logs dos containers
	docker-compose logs -f

# Aplicação
run: ## Roda a aplicação em modo desenvolvimento
	uvicorn src.main:app --reload --port 8000

run-prod: ## Roda em produção
	uvicorn src.main:app --host 0.0.0.0 --port 8000

# Development
setup: install-dev install-security ## Setup completo para desenvolvimento
