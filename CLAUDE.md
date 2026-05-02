# Zé Din Din — Development Guide

## Project Overview

Zé Din Din é uma aplicação web de gestão financeira doméstica familiar. Ele permite acompanhar o fluxo financeiro de todos os membros da familia por meio de Dashboard. Ele usa Python, Flask, Bootstrap, Postgress.

### OBJETIVO DA APLICAÇÃO

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

## Stack tecnologica

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

## REGRAS DE NEGÓCIO

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

## MVP

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

## CRITÉRIOS DE ACEITE

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

## CUIDADOS IMPORTANTES

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

Nunca permitir:

- Consulta sem family_id
- Usuário acessar dados de outra família
- Senha em texto puro
- Uso de float para dinheiro
- Exposição de variáveis sensíveis

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
- Usar Application Factory em app/__init__.py
- Registrar Blueprints por domínio
- Separar rotas, formulários, services e models
- Não colocar regra de negócio diretamente nas rotas
- Usar services para regras financeiras
- Usar repositories para consultas mais complexas
- Usar templates Jinja2 com herança de layout
- Usar Bootstrap para responsividade
- Usuário não autenticado não pode acessar áreas privadas
- Senhas nunca devem ser armazenadas em texto puro
- Usar password hash seguro

## INTERFACE E EXPERIÊNCIA DO USUÁRIO

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

## Orientação de Desenvolvimento
 O projeto será construido em sprints. 

1. Sprint 1 — Setup inicial
2. Sprint 2 — Autenticação
3. Sprint 3 — Banco e família
4. Sprint 4 — Contas e categorias
5. Sprint 5 — Transações
6. Sprint 6 — Dashboard
7. Sprint 7 — Orçamentos, contas a pagar e metas
8. Sprint 8 — Relatórios
9. Sprint 9 — Testes, segurança e qualidade
10. Sprint 10 — Refinamento visual e entrega do MVP

Depois da implementação de cada sprint, crie um arquivo chamado relatorio_desenvolvimento_sprint_[numero da sprint] e apresente:

- Resumo do que foi criado
- Estrutura de pastas
- Principais comandos para rodar
- Como executar migrations
- Como rodar testes
- Próximos passos recomendados


## Documentation

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

Quando finalizar a sprint:

1. Update `README.md` with the new feature in the feature list.
2. Update `CLAUDE.md` if the change affects development workflow, core principles, or architecture.