# Arquitetura — Zé Din Din

## Visão Geral

Aplicação Flask monolítica com arquitetura modular por domínio.

## Padrões

- **Application Factory**: `create_app()` em `app/__init__.py`
- **Blueprints por domínio**: auth, dashboard, families, accounts, transactions, categories, budgets, bills, credit_cards, goals, reports, imports
- **Camadas**: routes → services → repositories → models
- **Models centralizados**: `app/models/`
- **Utils compartilhados**: `app/utils/`

## Fluxo de uma requisição

```
HTTP Request
    │
    ▼
Flask Blueprint Route (routes.py)
    │
    ▼
Service Layer (services.py)   ← regras de negócio
    │
    ▼
Repository Layer (repositories/)   ← queries SQLAlchemy
    │
    ▼
Model / Database (models/ + PostgreSQL)
    │
    ▼
Response → Jinja2 Template
```

## Regras de segurança

- Toda rota privada usa `@login_required`
- Todo acesso a dados financeiros valida `family_id`
- Valores monetários armazenados em **centavos (Integer)**
- Senhas com hash via `werkzeug.security`
- CSRF habilitado globalmente via Flask-WTF
