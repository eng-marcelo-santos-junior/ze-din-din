# Regras de Negócio — Zé Din Din

## 1. Dinheiro

- Todos os valores são armazenados como **Integer em centavos**.
- Nunca usar `float` para dinheiro.
- `parse_money_to_cents()` aceita formato pt-BR (`1.234,56`) e en (`1234.56`).
- `format_cents_to_money()` sempre formata em pt-BR.

## 2. Família e Isolamento

- Todo usuário deve pertencer a pelo menos uma família para usar o sistema.
- Toda entidade financeira (conta, transação, orçamento, meta, conta a pagar, categoria) possui `family_id`.
- Nenhuma consulta pode retornar dados de família diferente da do usuário autenticado.
- O `@family_required` decorator define `g.current_family` antes de qualquer rota privada.

## 3. Contas Financeiras

- O `current_balance_cents` é atualizado em tempo real a cada transação.
- Criar transação `INCOME` → soma ao saldo.
- Criar transação `EXPENSE` → subtrai do saldo (valor armazenado como negativo).
- Cancelar transação → reverte o efeito no saldo.
- Transações com `status=CANCELED` **não afetam** o saldo.

## 4. Transações

- `amount_cents` é **assinado**: positivo = crédito, negativo = débito.
- Tipos: `INCOME`, `EXPENSE`, `TRANSFER`, `ADJUSTMENT`, `REFUND`.
- Transferência cria **dois** registros com o mesmo `transfer_group_id`.
- Transações canceladas não entram em relatórios, orçamentos ou dashboard.

## 5. Orçamentos

- Um orçamento é criado por (família, categoria, mês, ano).
- Se já existir um orçamento para a mesma combinação, é feito **upsert** (atualiza).
- Saúde do orçamento:
  - `healthy` → realizado < 80% do planejado
  - `warning` → realizado entre 80% e 99%
  - `exceeded` → realizado ≥ 100%
- Transações canceladas não são contabilizadas no realizado.

## 6. Contas a Pagar/Receber

- `PAYABLE`: conta a pagar. Ao pagar, gera transação `EXPENSE`.
- `RECEIVABLE`: conta a receber. Ao receber, gera transação `INCOME`.
- `is_overdue`: calculado em tempo real (sem job), verdadeiro se `PENDING` e vencida.
- Pagar uma conta altera o saldo da conta bancária vinculada imediatamente.

## 7. Metas Financeiras

- Aportes são acumulativos (`current_amount_cents += aporte`).
- Aportes de zero ou negativos são ignorados.
- Quando `current_amount_cents >= target_amount_cents`, status muda para `COMPLETED` automaticamente.
- `monthly_needed`: calcula `(restante / meses_até_target_date)`. Retorna 0 se sem data ou já completada.

## 8. Relatórios

- Todos os relatórios filtram por `family_id`.
- Transações canceladas são excluídas de todos os cálculos.
- Transferências não entram em relatórios de receitas/despesas.
- O fluxo de caixa mostra os últimos N meses (padrão: 12).

## 9. Papéis de Usuário (Roles)

| Role | Permissões |
|------|-----------|
| `OWNER` | Total — gerencia membros, dados e configurações |
| `ADMIN` | Cria/edita tudo, não remove outros admins |
| `MEMBER` | Lança transações, visualiza dashboards |
| `RESTRICTED` | Lança despesas próprias apenas |

## 10. Exclusão vs. Arquivamento

- Preferir arquivar (`is_active = False`) a deletar.
- Exclusões definitivas exigem confirmação modal.
- Transações deletadas têm seu efeito revertido no saldo da conta.
