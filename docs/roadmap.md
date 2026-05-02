# Roadmap — Zé Din Din

## Status atual (MVP v1.0)

Sprints concluídas:

| Sprint | Módulo | Status |
|--------|--------|--------|
| 1 | Setup inicial, Docker, estrutura Flask | ✅ |
| 2 | Autenticação (register, login, logout) | ✅ |
| 3 | Família e membros | ✅ |
| 4 | Contas financeiras e categorias | ✅ |
| 5 | Transações com controle de saldo em tempo real | ✅ |
| 6 | Dashboard com gráficos e filtros | ✅ |
| 7 | Orçamentos, contas a pagar/receber e metas | ✅ |
| 8 | Relatórios financeiros com exportação CSV | ✅ |
| 9 | Testes, segurança e qualidade | ✅ |

## Próximos passos — v1.1

### Sprint 10 — Refinamento visual e entrega MVP

- [ ] Responsividade mobile (menu hamburger, cards responsivos)
- [ ] Paginação nas listas de transações e bills
- [ ] Estados de loading e feedback visual aprimorado
- [ ] Validação client-side nos formulários
- [ ] Revisão de acessibilidade (ARIA labels, contrast)

## Backlog — v2.0

### Cartões de Crédito

- Modelo `CreditCard` com limite, dia de fechamento e vencimento
- Modelo `CreditCardInvoice` para faturas
- Compras parceladas com geração automática das parcelas
- Pagamento de fatura gera transação na conta bancária

### Importação CSV

- Upload de extrato bancário (Nubank, BB, Bradesco)
- Preview antes de confirmar
- Mapeamento de colunas configurável
- Detecção de duplicidade

### Convidar Membros

- Convite por e-mail
- Link de aceite com expiração
- Definição de role no convite

### Notificações

- Alertas de bills próximas do vencimento
- Alerta de orçamento excedido
- Resumo semanal via e-mail

### Open Finance (v3.0)

- Integração com APIs bancárias (Belvo, Pluggy)
- Sincronização automática de transações
- Categorização automática com IA

### IA e Insights (v3.0)

- Previsão de gastos baseada em histórico
- Sugestão automática de categoria
- Análise de padrões de consumo
- Recomendações personalizadas de economia

## Débitos técnicos

| Item | Prioridade |
|------|-----------|
| Migrar `datetime.utcnow()` para `datetime.now(UTC)` | Baixa |
| Adicionar paginação em transactions e bills | Média |
| Implementar roles MEMBER e RESTRICTED nas rotas | Média |
| Adicionar rate limiting no login | Alta |
| Configurar Redis para sessões em produção | Alta |
| Adicionar testes E2E com Playwright ou Selenium | Baixa |
