# AI Data Analyst

**Sistema NL2SQL que converte perguntas em linguagem natural para queries SQL, executa-as de forma segura e retorna resultados com insights automáticos.**

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Stack Tecnológica](#stack-tecnológica)
- [Quick Start](#quick-start)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API Endpoints](#api-endpoints)
- [Segurança](#segurança)
- [Análise de Código](#análise-de-código)
- [Desenvolvimento](#desenvolvimento)

---

## Sobre o Projeto

O **AI Data Analyst** permite que usuários não-técnicos acessem dados de bancos PostgreSQL usando linguagem natural. 

### Problema
- Empresas têm dados em bancos, mas dependem de analistas para consultas
- Queries demoram, decisões são lentas
- Usuários não técnicos não conseguem acessar dados

### Solução
O sistema recebe perguntas em linguagem natural como:
```
"Quais produtos mais vendem no nordeste?"
```

E retorna automaticamente:
- SQL gerado (para transparência)
- Explicação do que foi feito
- Dados tabulares
- Gráfico sugerido
- Insight automático em linguagem natural

---

## Stack Tecnológica

| Camada | Tecnologia |
|--------|------------|
| Backend | Python 3.11+ / FastAPI |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| LLM | OpenAI GPT-4 / Anthropic Claude (abstraído) |
| Frontend | Next.js (em desenvolvimento) |

---

## Quick Start

### Pré-requisitos
- Python 3.11+
- Docker e Docker Compose
- (Opcional) Chaves de API OpenAI/Anthropic

### 1. Clonar e configurar ambiente

```bash
# Clonar repositório
cd AI-DATA-ANALYST

# Criar ambiente virtual e instalar dependências
uv sync

# Copiar configurações
cp .env.example .env
# Editar .env com suas chaves de API
```

### 2. Subir infraestrutura

```bash
# Iniciar Postgres e Redis
docker-compose up -d

# Verificar status
docker-compose ps
```

### 3. Rodar a aplicação

```bash
# Modo desenvolvimento
uv run uvicorn src.main:app --reload --port 8000

# Produção
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 4. Acessar documentação

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## Estrutura do Projeto

```
AI-DATA-ANALYST/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   │   ├── config.py       # Configurações (Pydantic Settings)
│   │   ├── database.py     # Conexão async com PostgreSQL
│   │   └── logging.py      # Logging estruturado
│   ├── models/
│   │   ├── queries.py      # Request/Response models
│   │   └── schema.py       # Modelos de schema do banco
│   ├── services/           # (Implementação futura)
│   │   ├── schema.py       # Extração de metadata
│   │   ├── nl2sql.py       # Conversão NL→SQL via LLM
│   │   ├── validator.py    # Validação de segurança SQL
│   │   ├── executor.py     # Execução de queries
│   │   └── insight.py      # Geração de insights
│   └── utils/
│       └── cache.py        # Cache Redis
├── tests/
│   ├── unit/               # Testes unitários
│   └── integration/        # Testes de integração
├── docker-compose.yml      # Postgres + Redis
├── pyproject.toml          # Dependências Python
└── AGENTS.md              # Guias para desenvolvedores
```

---

## API Endpoints

### Health Check
```http
GET /health
```
Retorna status da aplicação, conexão com banco e Redis.

### Processar Query
```http
POST /api/v1/query
Content-Type: application/json

{
  "question": "Quais são os 10 produtos mais vendidos?"
}
```

**Resposta:**
```json
{
  "sql": "SELECT product_name, SUM(quantity) as total FROM sales GROUP BY product_name ORDER BY total DESC LIMIT 10",
  "explanation": "Agrupei as vendas por produto, somei as quantidades e ordenei decrescente",
  "data": [...],
  "chart_type": "bar",
  "insight": "O produto X representa 34% das vendas totais, indicando alta concentração...",
  "cached": false
}
```

---

## Segurança

O AI Data Analyst implementa múltiplas camadas de segurança:

### 🛡️ Validação SQL
- **Apenas SELECT permitido** — Bloqueia INSERT, UPDATE, DELETE, DROP, etc.
- **AST Parsing** — Usa `sqlparse` para validar estrutura SQL (não só regex)
- **Limite de linhas** — Máximo 1000 registros por query
- **Timeout** — Queries expiram em 3-5 segundos
- **Conexão Read-Only** — Não é possível modificar dados

### 🔒 Boas Práticas
- Nenhuma query SQL é logada com dados sensíveis
- Erros internos não expõem detalhes ao cliente
- Rate limiting previne abuso

### 📋 Ferramentas de Segurança

```bash
# Análise estática de código
bandit -r src/

# Verificar vulnerabilidades em dependências
safety check

# Auditoria completa de dependências
pip-audit
```

---

## Análise de Código

### Lint e Formatação

```bash
# Verificar código
ruff check .

# Corrigir automaticamente
ruff check . --fix

# Formatar código
ruff format .
```

### Type Checking

```bash
# Verificar tipos
mypy src/
```

### Testes

```bash
# Rodar todos os testes
pytest

# Com coverage
pytest --cov=src --cov-report=html
```

### Verificação Completa

```bash
# Executa todas as verificações
ruff check . && mypy src/ && bandit -r src/ && safety check && pytest tests/unit/ -v
```

---

## Desenvolvimento

### Pipeline NL2SQL (Planejado)

```
Usuário → Pergunta NL → Schema → LLM → SQL → Validação → Execução → Insight → Resposta
```

1. **Schema Service** — Extrai metadata do banco (tabelas, colunas, tipos)
2. **NL2SQL Service** — Converte pergunta em SQL usando LLM
3. **SQL Validator** — Valida segurança do SQL gerado
4. **Query Executor** — Executa query com timeout e limite
5. **Insight Generator** — Gera insight analítico via LLM

### Roadmap de Sprints

| Sprint | Foco | Status |
|--------|------|--------|
| 1 | Foundation (FastAPI, config, models) | ✅ Completo |
| 2 | Database Layer (Schema Service) | ⏳ Pendente |
| 3 | NL2SQL Core (LLM, Validator, Executor) | ⏳ Pendente |
| 4 | Caching & Performance | ⏳ Pendente |
| 5 | Insight Generation | ⏳ Pendente |
| 6 | Security Hardening | ⏳ Pendente |

---

## 📄 Licença

MIT License - Use livremente para projetos pessoais e comerciais.

---

## 🤝 Contribuições

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

*AI Data Analyst - Transformando perguntas em insights desde 2024*
