# Database — Zé Din Din

## Tecnologia

- **PostgreSQL 16**
- **ORM**: Flask-SQLAlchemy 3.x
- **Migrations**: Flask-Migrate / Alembic

## Convenções

| Regra | Detalhe |
|-------|---------|
| Valores monetários | Sempre `Integer` em centavos (ex: R$ 1.234,56 → `123456`) |
| Nunca usar `Float` | Evita erros de arredondamento em dinheiro |
| Timestamps | `created_at` e `updated_at` em todas as tabelas financeiras |
| Soft delete | Preferir `is_active = False` a deletar registros |
| Isolamento | Toda tabela financeira possui `family_id` com FK e índice |

## Tabelas

### `users`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | Integer PK | |
| name | String(100) | |
| email | String(150) UNIQUE | |
| password_hash | String(256) | Hash PBKDF2-SHA256 |
| is_active | Boolean | Soft delete |
| created_at / updated_at | DateTime | |

### `families`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | Integer PK | |
| name | String(100) | Nome da família |
| currency | String(3) | ISO 4217 (ex: BRL) |
| created_by | FK → users | Criador/owner inicial |

### `family_members`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | Integer PK | |
| family_id | FK → families | |
| user_id | FK → users | |
| role | String(12) | OWNER, ADMIN, MEMBER, RESTRICTED |
| status | String(10) | ACTIVE, INACTIVE, INVITED |

### `accounts`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | Integer PK | |
| family_id | FK → families | Índice |
| owner_user_id | FK → users | |
| name | String(100) | |
| type | String(20) | CHECKING, SAVINGS, CASH, WALLET, INVESTMENT, CREDIT_CARD |
| initial_balance_cents | Integer | Saldo inicial em centavos |
| current_balance_cents | Integer | Saldo atual (atualizado em tempo real) |
| currency | String(3) | |
| is_active | Boolean | |

### `categories`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | Integer PK | |
| family_id | FK → families | Índice |
| parent_id | FK → categories | Subcategorias |
| name | String(100) | |
| type | String(10) | INCOME ou EXPENSE |
| color | String(7) | Hex (#RRGGBB) |
| is_default | Boolean | Criadas automaticamente na família |
| is_active | Boolean | |

### `transactions`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | Integer PK | |
| family_id | FK → families | Índice |
| account_id | FK → accounts | Índice |
| category_id | FK → categories | Índice, nullable |
| user_id | FK → users | Quem lançou |
| type | String(12) | INCOME, EXPENSE, TRANSFER, ADJUSTMENT, REFUND |
| description | String(200) | |
| amount_cents | Integer | **Assinado**: positivo=crédito, negativo=débito |
| transaction_date | Date | Índice |
| status | String(10) | PENDING, PAID, RECEIVED, CANCELED |
| transfer_group_id | String(36) | UUID que agrupa duas pernas de transferência |

### `budgets`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | Integer PK | |
| family_id | FK → families | Índice |
| category_id | FK → categories | |
| month | Integer | 1–12 |
| year | Integer | |
| planned_amount_cents | Integer | Sempre positivo |
| **UniqueConstraint** | (family_id, category_id, month, year) | Upsert automático |

### `bills`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | Integer PK | |
| family_id | FK → families | Índice composto com due_date |
| account_id | FK → accounts | Nullable |
| category_id | FK → categories | Nullable |
| description | String(200) | |
| amount_cents | Integer | Sempre positivo |
| due_date | Date | Vencimento |
| type | String(12) | PAYABLE ou RECEIVABLE |
| status | String(10) | PENDING, PAID, RECEIVED, OVERDUE, CANCELED |

### `goals`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | Integer PK | |
| family_id | FK → families | Índice |
| name | String(200) | |
| target_amount_cents | Integer | Valor-alvo |
| current_amount_cents | Integer | Acumulado via aportes |
| target_date | Date | Nullable |
| status | String(10) | ACTIVE, COMPLETED, CANCELED |

## Índices

```sql
-- transactions
INDEX transactions_family_id
INDEX transactions_account_id
INDEX transactions_category_id
INDEX transactions_transaction_date

-- accounts
INDEX accounts_family_id

-- categories
INDEX categories_family_id

-- budgets
INDEX budgets_family_id
INDEX budgets_family_month_year (family_id, month, year)

-- bills
INDEX bills_family_id
INDEX bills_family_due_date (family_id, due_date)

-- goals
INDEX goals_family_id
```

## Relacionamentos principais

```
User 1──* FamilyMember *──1 Family
Family 1──* Account
Family 1──* Category
Family 1──* Transaction
Family 1──* Budget
Family 1──* Bill
Family 1──* Goal
Account 1──* Transaction
Category 1──* Transaction
Category 1──* Budget
```
