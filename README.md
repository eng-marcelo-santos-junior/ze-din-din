# Zé Din Din 💰

Aplicação web de gestão financeira doméstica familiar.

## Objetivo

Permitir que famílias controlem receitas, despesas, contas bancárias, cartões de crédito, orçamentos, metas financeiras e relatórios em um só lugar.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12, Flask 3.1 |
| Autenticação | Flask-Login |
| Formulários | Flask-WTF / WTForms |
| ORM | Flask-SQLAlchemy |
| Migrações | Flask-Migrate / Alembic |
| Banco | PostgreSQL 16 |
| Frontend | Bootstrap 5.3, Jinja2 |
| Gráficos | Chart.js 4 |
| Deploy | Docker, Docker Compose, Gunicorn |
| Testes | Pytest, pytest-flask |

## Pré-requisitos

- Docker e Docker Compose instalados
- (Opcional) Python 3.12+ para desenvolvimento local

## Como rodar com Docker Compose

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd ze-din-din

# 2. Copie e configure o .env
cp .env.example .env

# 3. Suba os containers
docker compose up -d

# 4. Execute as migrations
docker compose exec web flask db upgrade

# 5. Acesse no navegador
# http://localhost:5000
```

## Configurar o .env

```bash
cp .env.example .env
```

Edite o `.env` com suas configurações:

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `FLASK_CONFIG` | Ambiente (`development`, `production`) | `development` |
| `SECRET_KEY` | Chave secreta da sessão | Altere obrigatoriamente |
| `DATABASE_URL` | URL do PostgreSQL | postgresql://zedindin:zedindin@localhost:5432/zedindin_dev |

## Como rodar migrations

```bash
# Inicializar (apenas na primeira vez, sem Docker):
flask db init

# Gerar uma nova migration:
make migration msg="descricao da mudanca"
# ou:
docker compose exec web flask db migrate -m "descricao"

# Aplicar migrations:
make migrate
# ou:
docker compose exec web flask db upgrade
```

## Como rodar testes

```bash
make test
# ou:
docker compose exec web pytest -v

# Com cobertura:
make test-cov
```

## Comandos úteis

```bash
make build      # Rebuild dos containers
make up         # Sobe containers em background
make down       # Para containers
make logs       # Logs do container web
make shell      # Flask shell interativo
make psql       # psql no banco de desenvolvimento
make lint       # Verifica qualidade do código
make format     # Formata código com black + isort
```

## Estrutura do projeto

```
ze-din-din/
├── app/
│   ├── __init__.py         # Application Factory
│   ├── config.py           # Configurações por ambiente
│   ├── extensions.py       # Extensões Flask (db, login, csrf...)
│   ├── main/               # Blueprint público (home)
│   ├── auth/               # Autenticação (Sprint 2)
│   ├── dashboard/          # Dashboard principal (Sprint 2)
│   ├── families/           # Gestão de família (Sprint 2)
│   ├── accounts/           # Contas financeiras (Sprint 3)
│   ├── transactions/       # Transações (Sprint 3)
│   ├── categories/         # Categorias (Sprint 3)
│   ├── models/             # Models SQLAlchemy centralizados
│   ├── repositories/       # Queries complexas
│   ├── utils/              # Helpers (money, dates, permissions)
│   ├── templates/          # Templates Jinja2
│   └── static/             # CSS, JS, imagens
├── migrations/             # Alembic migrations
├── tests/                  # Testes Pytest
├── docs/                   # Documentação técnica
├── docker/
│   └── init.sql            # Cria banco de teste
├── run.py                  # Entry point Flask
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Regras de negócio principais

- Valores monetários armazenados em **centavos (Integer)** — nunca float
- Toda entidade financeira possui `family_id`
- Usuários só acessam dados da própria família
- Roles de membros: `OWNER`, `ADMIN`, `MEMBER`, `RESTRICTED`

## Sprints

| Sprint | Escopo | Status |
|--------|--------|--------|
| 1 | Setup inicial, Docker, estrutura base | ✅ Concluído |
| 2 | Autenticação (cadastro, login, logout, recuperação) | ✅ Concluído |
| 3 | Banco e família (modelos, família, membros, roles) | ✅ Concluído |
| 4 | Contas financeiras e categorias | ✅ Concluído |
| 5 | Transações com controle de saldo em tempo real | ✅ Concluído |
| 6 | Dashboard financeiro com cards, gráficos e filtros | ✅ Concluído |
| 7 | Orçamentos, contas a pagar e metas | ✅ Concluído |
| 8 | Relatórios financeiros com exportação CSV | ✅ Concluído |
| 9 | Testes, segurança e qualidade | 🔜 |
| 10 | Refinamento visual e entrega MVP | 🔜 |
