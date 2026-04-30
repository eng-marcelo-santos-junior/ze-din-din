Você é um arquiteto de software, product manager e engenheiro full-stack sênior especialista em Python, Flask, PostgreSQL e aplicações web monolíticas bem estruturadas.

Sua missão é desenvolver uma aplicação web de gestão financeira doméstica familiar usando:

- Backend: Flask
- Frontend: HTML, Jinja2, Bootstrap 5, JavaScript básico
- Banco de dados: PostgreSQL
- ORM: SQLAlchemy
- Migrations: Flask-Migrate / Alembic
- Autenticação: Flask-Login
- Formulários: Flask-WTF / WTForms
- Validação: WTForms e validações na camada de serviço
- Testes: Pytest
- Gráficos: Chart.js
- Deploy: Docker, Gunicorn e PostgreSQL

O produto deve ser profissional, moderno, seguro, responsivo e preparado para evolução.

Nome provisório da aplicação: "Zé Din Din".

==================================================
1. OBJETIVO DA APLICAÇÃO
==================================================

Criar um sistema de gestão financeira doméstica familiar.

A aplicação deve permitir que uma família controle:

- Receitas
- Despesas
- Contas bancárias
- Dinheiro em espécie
- Cartões de crédito
- Contas a pagar
- Contas a receber
- Orçamentos mensais
- Categorias de gastos
- Metas financeiras
- Dívidas
- Relatórios
- Fluxo de caixa
- Patrimônio familiar

A aplicação deve ser simples para uso diário, mas organizada o suficiente para gerar análises financeiras úteis.

==================================================
2. PERFIS DE USUÁRIO
==================================================

A aplicação deve ter os seguintes perfis:

1. Administrador da família
   - Cria o grupo familiar
   - Convida membros
   - Gerencia contas, categorias, orçamentos e usuários
   - Visualiza todos os dados financeiros da família

2. Membro da família
   - Registra receitas e despesas
   - Consulta dashboards e relatórios permitidos
   - Acompanha metas e orçamentos

3. Membro restrito
   - Registra despesas próprias
   - Visualiza apenas dados autorizados

==================================================
3. STACK TECNOLÓGICA
==================================================

Use obrigatoriamente:

Backend:
- Python 3.12+
- Flask
- Flask-Login
- Flask-WTF
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt ou Werkzeug Security
- python-dotenv

Frontend:
- HTML5
- CSS3
- Bootstrap 5
- Jinja2 templates
- JavaScript básico
- Chart.js para gráficos

Banco:
- PostgreSQL
- SQLAlchemy ORM
- Alembic para migrations

Testes:
- Pytest
- pytest-flask
- Factory Boy opcional

Deploy:
- Docker
- Docker Compose
- Gunicorn
- PostgreSQL em container para ambiente local

Qualidade:
- Black
- Ruff ou Flake8
- isort
- pre-commit opcional

==================================================
4. ARQUITETURA DO PROJETO
==================================================

Use uma arquitetura modular baseada em Flask Application Factory e Blueprints.

Estrutura sugerida:

project/
  app/
    __init__.py
    config.py
    extensions.py

    auth/
      __init__.py
      routes.py
      forms.py
      services.py

    dashboard/
      __init__.py
      routes.py
      services.py

    families/
      __init__.py
      routes.py
      forms.py
      services.py

    accounts/
      __init__.py
      routes.py
      forms.py
      services.py

    transactions/
      __init__.py
      routes.py
      forms.py
      services.py

    categories/
      __init__.py
      routes.py
      forms.py
      services.py

    budgets/
      __init__.py
      routes.py
      forms.py
      services.py

    bills/
      __init__.py
      routes.py
      forms.py
      services.py

    credit_cards/
      __init__.py
      routes.py
      forms.py
      services.py

    goals/
      __init__.py
      routes.py
      forms.py
      services.py

    reports/
      __init__.py
      routes.py
      services.py

    imports/
      __init__.py
      routes.py
      forms.py
      services.py

    models/
      __init__.py
      user.py
      family.py
      account.py
      category.py
      transaction.py
      budget.py
      bill.py
      credit_card.py
      goal.py
      import_batch.py
      audit_log.py

    repositories/
      user_repository.py
      family_repository.py
      account_repository.py
      transaction_repository.py
      report_repository.py

    templates/
      base.html
      auth/
      dashboard/
      accounts/
      transactions/
      categories/
      budgets/
      bills/
      credit_cards/
      goals/
      reports/
      settings/

    static/
      css/
        main.css
      js/
        main.js
        charts.js
      images/

    utils/
      money.py
      dates.py
      permissions.py
      decorators.py

  migrations/
  tests/
    unit/
    integration/
    e2e/

  .env.example
  requirements.txt
  pyproject.toml
  Dockerfile
  docker-compose.yml
  run.py
  README.md

Padrões obrigatórios:

- Usar Application Factory em app/__init__.py
- Registrar Blueprints por domínio
- Separar rotas, formulários, services e models
- Não colocar regra de negócio diretamente nas rotas
- Usar services para regras financeiras
- Usar repositories para consultas mais complexas
- Usar templates Jinja2 com herança de layout
- Usar Bootstrap para responsividade

==================================================
5. REQUISITOS FUNCIONAIS
==================================================

--------------------------------------------------
5.1 Autenticação
--------------------------------------------------

Implementar:

- Cadastro de usuário
- Login
- Logout
- Recuperação de senha, se possível
- Hash seguro de senha
- Proteção de rotas privadas
- Sessão com Flask-Login

Telas:

- /login
- /register
- /logout
- /forgot-password

Regras:

- Usuário não autenticado não pode acessar áreas privadas
- Senhas nunca devem ser armazenadas em texto puro
- Usar password hash seguro

--------------------------------------------------
5.2 Família
--------------------------------------------------

Implementar grupo familiar.

Funcionalidades:

- Criar família no primeiro acesso
- Editar dados da família
- Convidar membros
- Definir papéis dos membros
- Listar membros
- Remover membro
- Controlar permissões por família

Campos da família:

- id
- name
- currency
- created_by
- created_at
- updated_at

Campos do membro:

- id
- family_id
- user_id
- role
- status
- created_at

Roles:

- OWNER
- ADMIN
- MEMBER
- RESTRICTED

--------------------------------------------------
5.3 Dashboard
--------------------------------------------------

Criar dashboard principal com:

- Saldo total
- Receitas do mês
- Despesas do mês
- Resultado do mês
- Total em contas
- Total em cartões
- Contas próximas do vencimento
- Orçamento usado
- Gastos por categoria
- Receitas versus despesas por mês
- Evolução do saldo

Usar:

- Cards Bootstrap
- Chart.js para gráficos
- Filtros por período

Rota:

- /dashboard

--------------------------------------------------
5.4 Contas Financeiras
--------------------------------------------------

Permitir cadastro de contas:

- Conta corrente
- Conta poupança
- Dinheiro físico
- Carteira digital
- Investimento
- Cartão de crédito

Campos:

- id
- family_id
- owner_user_id
- name
- type
- institution
- initial_balance_cents
- current_balance_cents
- currency
- color
- icon
- is_active
- visibility
- created_at
- updated_at

Funcionalidades:

- Criar conta
- Editar conta
- Arquivar conta
- Ver saldo
- Ver extrato
- Transferir entre contas

Rotas:

- /accounts
- /accounts/new
- /accounts/<id>/edit
- /accounts/<id>/statement

--------------------------------------------------
5.5 Categorias
--------------------------------------------------

Criar categorias para receitas e despesas.

Categorias padrão de receita:

- Salário
- Freelance
- Investimentos
- Reembolso
- Outros

Categorias padrão de despesa:

- Alimentação
- Moradia
- Transporte
- Saúde
- Educação
- Lazer
- Mercado
- Energia
- Água
- Internet
- Assinaturas
- Cartão de crédito
- Impostos
- Pets
- Outros

Campos:

- id
- family_id
- parent_id
- name
- type
- color
- icon
- is_default
- is_active
- created_at
- updated_at

Funcionalidades:

- Criar categoria
- Editar categoria
- Arquivar categoria
- Criar subcategoria
- Filtrar por tipo

Rotas:

- /categories
- /categories/new
- /categories/<id>/edit

--------------------------------------------------
5.6 Transações
--------------------------------------------------

Permitir lançamento de:

- Receita
- Despesa
- Transferência
- Ajuste
- Estorno

Campos:

- id
- family_id
- account_id
- category_id
- user_id
- type
- description
- amount_cents
- transaction_date
- competence_date
- status
- payment_method
- notes
- transfer_group_id
- installment_group_id
- recurring_rule_id
- created_at
- updated_at

Funcionalidades:

- Criar transação
- Editar transação
- Excluir transação
- Duplicar transação
- Marcar como paga
- Marcar como recebida
- Filtrar transações
- Buscar por descrição
- Exportar CSV
- Criar transferência entre contas
- Criar despesa parcelada
- Criar transação recorrente

Rotas:

- /transactions
- /transactions/new
- /transactions/<id>/edit
- /transactions/<id>/delete

Regras:

- Valores monetários devem ser salvos em centavos como inteiro
- Não usar float para dinheiro
- Receitas aumentam saldo da conta
- Despesas reduzem saldo da conta
- Transferências reduzem uma conta e aumentam outra
- Toda transação deve ter family_id
- O usuário só pode acessar transações da própria família
- Transações canceladas não entram nos relatórios

--------------------------------------------------
5.7 Orçamentos
--------------------------------------------------

Permitir criação de orçamento mensal por categoria.

Campos:

- id
- family_id
- category_id
- month
- year
- planned_amount_cents
- created_at
- updated_at

Funcionalidades:

- Criar orçamento
- Editar orçamento
- Comparar planejado versus realizado
- Mostrar percentual usado
- Alertar orçamento excedido
- Copiar orçamento do mês anterior

Rotas:

- /budgets
- /budgets/new
- /budgets/<id>/edit

--------------------------------------------------
5.8 Contas a Pagar e Receber
--------------------------------------------------

Permitir controle de compromissos financeiros.

Campos:

- id
- family_id
- account_id
- category_id
- description
- amount_cents
- due_date
- type
- status
- recurrence_rule_id
- created_at
- updated_at

Tipos:

- PAYABLE
- RECEIVABLE

Status:

- PENDING
- PAID
- RECEIVED
- OVERDUE
- CANCELED

Funcionalidades:

- Criar conta a pagar
- Criar conta a receber
- Listar vencidas
- Listar próximas do vencimento
- Marcar como pago
- Marcar como recebido
- Gerar transação ao pagar ou receber

Rotas:

- /bills
- /bills/new
- /bills/<id>/edit
- /bills/<id>/pay

--------------------------------------------------
5.9 Cartões de Crédito
--------------------------------------------------

Funcionalidades:

- Criar cartão
- Definir limite
- Definir dia de fechamento
- Definir dia de vencimento
- Registrar compra no cartão
- Registrar compra parcelada
- Agrupar compras por fatura
- Fechar fatura
- Pagar fatura
- Mostrar limite usado
- Mostrar limite disponível

Regras:

- Compra no cartão não reduz saldo da conta imediatamente
- O saldo da conta só reduz quando a fatura é paga
- Parcelas devem aparecer nos meses corretos
- Fatura deve respeitar fechamento e vencimento

Rotas:

- /credit-cards
- /credit-cards/new
- /credit-cards/<id>
- /credit-cards/<id>/invoices

--------------------------------------------------
5.10 Metas Financeiras
--------------------------------------------------

Permitir criar metas como:

- Reserva de emergência
- Viagem
- Compra de veículo
- Reforma
- Quitação de dívida
- Investimento

Campos:

- id
- family_id
- name
- target_amount_cents
- current_amount_cents
- target_date
- account_id
- status
- created_at
- updated_at

Funcionalidades:

- Criar meta
- Editar meta
- Atualizar progresso
- Associar aporte
- Mostrar percentual concluído
- Estimar valor mensal necessário

Rotas:

- /goals
- /goals/new
- /goals/<id>/edit

--------------------------------------------------
5.11 Relatórios
--------------------------------------------------

Criar relatórios:

- Receitas por mês
- Despesas por mês
- Despesas por categoria
- Despesas por membro
- Fluxo de caixa mensal
- Evolução de saldo
- Orçamento planejado versus realizado
- Maiores despesas
- Gastos recorrentes
- Dívidas
- Patrimônio líquido

Rotas:

- /reports
- /reports/cash-flow
- /reports/categories
- /reports/budget
- /reports/net-worth

Usar:

- Tabelas Bootstrap
- Gráficos Chart.js
- Filtros por período, conta, categoria e membro

--------------------------------------------------
5.12 Importação CSV
--------------------------------------------------

Implementar importação básica de CSV.

Funcionalidades:

- Upload de arquivo CSV
- Preview antes da importação
- Mapeamento de colunas
- Validação de dados
- Detecção simples de duplicidade
- Confirmação antes de importar
- Registro do lote importado

Rotas:

- /imports
- /imports/new
- /imports/preview
- /imports/confirm

==================================================
6. MODELAGEM DE BANCO DE DADOS
==================================================

Criar models SQLAlchemy para:

- User
- Family
- FamilyMember
- Account
- Category
- Transaction
- Budget
- Bill
- CreditCard
- CreditCardInvoice
- Goal
- ImportBatch
- AuditLog
- Tag
- TransactionTag

Usar PostgreSQL.

Regras de modelagem:

- Todas as tabelas financeiras devem ter family_id
- Valores monetários devem ser Integer em centavos
- Datas devem usar Date ou DateTime com timezone quando necessário
- Criar índices para consultas frequentes
- Criar relacionamentos SQLAlchemy corretamente
- Usar constraints onde fizer sentido
- Usar created_at e updated_at

Índices importantes:

- transactions.family_id
- transactions.account_id
- transactions.category_id
- transactions.transaction_date
- accounts.family_id
- categories.family_id
- budgets.family_id, month, year
- bills.family_id, due_date

==================================================
7. SEGURANÇA
==================================================

Implementar:

- Proteção de rotas com login_required
- Controle de permissão por família
- Verificação de family_id em todas as consultas
- CSRF protection com Flask-WTF
- Hash seguro de senha
- Validação no backend
- Sanitização de entradas
- Mensagens de erro seguras
- Proteção contra acesso indevido a dados de outra família

Criar decorators ou helpers como:

- @login_required
- @family_required
- @role_required("ADMIN")
- user_has_access_to_family(user_id, family_id)

Nunca permitir:

- Consulta sem family_id
- Usuário acessar dados de outra família
- Senha em texto puro
- Uso de float para dinheiro
- Exposição de variáveis sensíveis

==================================================
8. INTERFACE E EXPERIÊNCIA DO USUÁRIO
==================================================

Usar Bootstrap 5.

Criar layout com:

- Navbar superior
- Sidebar no desktop
- Menu responsivo no mobile
- Cards financeiros
- Tabelas responsivas
- Formulários limpos
- Botões claros
- Badges de status
- Alertas com Bootstrap
- Modais de confirmação
- Toasts ou flash messages
- Estados vazios
- Loading simples quando necessário

Páginas devem ter:

- Título claro
- Breadcrumb opcional
- Botão principal de ação
- Filtros quando necessário
- Paginação em listas grandes

Estilo visual:

- Moderno
- Minimalista
- Familiar
- Confiável
- Responsivo

Sugestão de cores:

- Verde para saldo positivo
- Vermelho para despesas ou alertas
- Azul para informações
- Amarelo para atenção
- Cinza claro para fundos

==================================================
9. REGRAS DE NEGÓCIO
==================================================

Implementar com cuidado:

1. Uma família pode ter vários usuários.
2. Um usuário pode futuramente participar de várias famílias.
3. Toda transação pertence a uma família.
4. Toda conta pertence a uma família.
5. Toda categoria pertence a uma família.
6. Receitas aumentam saldo.
7. Despesas reduzem saldo.
8. Transferências criam dois movimentos relacionados.
9. Cartão de crédito não reduz saldo bancário no momento da compra.
10. Pagamento da fatura reduz saldo da conta bancária.
11. Orçamento compara planejado versus realizado.
12. Transações canceladas não entram em relatórios.
13. Valores devem ser armazenados em centavos.
14. Relatórios devem ignorar dados de outras famílias.
15. Exclusões críticas devem pedir confirmação.
16. Preferir arquivar registros em vez de excluir definitivamente.

==================================================
10. TESTES
==================================================

Criar testes com Pytest.

Testes unitários:

- Conversão de dinheiro para centavos
- Criação de receita
- Criação de despesa
- Atualização de saldo
- Transferência entre contas
- Cálculo de orçamento
- Cálculo de fatura
- Permissão por família

Testes de integração:

- Cadastro de usuário
- Login
- Criação de família
- Criação de conta
- Criação de transação
- Listagem de dashboard
- Filtros de transações

Testes de segurança:

- Usuário não pode acessar dados de outra família
- Rotas privadas exigem login
- CSRF ativo nos formulários
- Usuário restrito não pode executar ações administrativas

==================================================
11. MVP
==================================================

A primeira versão deve conter:

- Cadastro
- Login
- Logout
- Criação de família
- Cadastro de contas
- Cadastro de categorias
- Cadastro de receitas
- Cadastro de despesas
- Lista de transações
- Dashboard básico
- Orçamento mensal
- Contas a pagar
- Metas simples
- Relatórios básicos
- Testes principais
- Docker Compose com Flask e PostgreSQL

Não implementar no MVP:

- Open Finance
- IA avançada
- Aplicativo mobile nativo
- OCR
- Notificações push
- Integração automática com bancos

==================================================
12. DOCKER E AMBIENTE LOCAL
==================================================

Criar:

- Dockerfile
- docker-compose.yml
- .env.example
- requirements.txt

O docker-compose deve conter:

- Serviço web Flask
- Serviço PostgreSQL
- Volume persistente para banco

Variáveis de ambiente:

- FLASK_APP
- FLASK_ENV
- SECRET_KEY
- DATABASE_URL
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

Comandos esperados:

- flask db init
- flask db migrate
- flask db upgrade
- flask run
- pytest

==================================================
13. DOCUMENTAÇÃO
==================================================

Criar documentação:

- README.md
- docs/architecture.md
- docs/database.md
- docs/business-rules.md
- docs/deploy.md
- docs/roadmap.md

README deve explicar:

- Objetivo do projeto
- Stack usada
- Como rodar localmente
- Como configurar .env
- Como subir com Docker
- Como rodar migrations
- Como rodar testes
- Estrutura de pastas
- Principais regras de negócio

==================================================
14. ORDEM DE EXECUÇÃO
==================================================

Execute o desenvolvimento nesta ordem:

1. Criar estrutura inicial Flask
2. Configurar Application Factory
3. Configurar extensões
4. Configurar PostgreSQL
5. Configurar SQLAlchemy
6. Configurar Flask-Migrate
7. Criar models principais
8. Criar migrations
9. Criar autenticação
10. Criar layout base com Bootstrap
11. Criar módulo de família
12. Criar módulo de contas
13. Criar módulo de categorias
14. Criar módulo de transações
15. Criar dashboard
16. Criar orçamento
17. Criar contas a pagar
18. Criar metas
19. Criar relatórios básicos
20. Criar testes
21. Criar Dockerfile e docker-compose
22. Criar documentação
23. Revisar segurança
24. Revisar responsividade
25. Entregar resumo final

==================================================
15. CRITÉRIOS DE ACEITE
==================================================

A aplicação será considerada pronta quando:

1. Usuário conseguir se cadastrar.
2. Usuário conseguir fazer login.
3. Usuário conseguir criar uma família.
4. Usuário conseguir criar contas financeiras.
5. Usuário conseguir criar categorias.
6. Usuário conseguir lançar receitas.
7. Usuário conseguir lançar despesas.
8. Dashboard mostrar saldo, receitas e despesas corretamente.
9. Usuário conseguir filtrar transações.
10. Usuário conseguir criar orçamento mensal.
11. Usuário conseguir criar contas a pagar.
12. Usuário conseguir criar metas.
13. Relatórios básicos funcionarem.
14. Dados financeiros forem armazenados em centavos.
15. Usuário não conseguir acessar dados de outra família.
16. Rotas privadas estiverem protegidas.
17. Testes principais estiverem passando.
18. Projeto rodar com Docker Compose.
19. README estiver completo.
20. Código estiver organizado por módulos.

==================================================
16. CUIDADOS IMPORTANTES
==================================================

Não faça:

- Não usar float para dinheiro.
- Não colocar regra de negócio diretamente nas rotas.
- Não acessar dados sem validar family_id.
- Não deixar rotas privadas sem login_required.
- Não armazenar senha sem hash.
- Não misturar HTML complexo diretamente nas rotas.
- Não criar arquivos gigantes.
- Não ignorar testes de permissão.
- Não expor secrets no repositório.

Faça:

- Use Blueprints.
- Use Application Factory.
- Use SQLAlchemy models bem definidos.
- Use Flask-Migrate.
- Use Bootstrap 5.
- Use templates reutilizáveis.
- Use services para regras financeiras.
- Use helpers para dinheiro e datas.
- Use Pytest.
- Use Docker.
- Use paginação.
- Use flash messages.
- Use confirmação antes de exclusões.

==================================================
17. RESULTADO ESPERADO
==================================================

Ao final, entregue:

- Aplicação Flask funcional
- Interface Bootstrap responsiva
- Banco PostgreSQL modelado
- Migrations configuradas
- Autenticação funcionando
- Gestão de família funcionando
- Contas, categorias e transações funcionando
- Dashboard básico funcionando
- Relatórios básicos funcionando
- Testes principais
- Docker Compose
- README completo
- Documentação técnica

Depois da implementação crie um arquivo chamado relatorio_desenvolvimento_sprint_[numero da sprint] e apresente:

- Resumo do que foi criado
- Estrutura de pastas
- Principais comandos para rodar
- Como executar migrations
- Como rodar testes
- Próximos passos recomendados