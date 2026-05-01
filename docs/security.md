# Segurança — Zé Din Din

## Autenticação

- **Flask-Login** gerencia sessões de usuário.
- **Werkzeug** `generate_password_hash` com `pbkdf2:sha256` — senhas nunca em texto puro.
- `@login_required` protege todas as rotas privadas.
- Redirect para `/auth/login` em qualquer acesso não autenticado.

## Autorização por Família

- `@family_required` decorator carrega e valida a família do usuário em `g.current_family`.
- Todo serviço recebe `family_id` explicitamente — nunca infere da sessão sozinho.
- Funções `get_*` retornam `None` (não 403) quando o recurso não pertence à família: a rota chama `abort(404)`.
- `user_has_access_to_family(user_id, family_id)` → helper em `app/utils/permissions.py`.

## Proteção CSRF

- **Flask-WTF** com `CSRFProtect` ativado para toda a aplicação.
- Todos os formulários WTForms incluem `{{ form.hidden_tag() }}`.
- Modais que submetem via POST incluem `{{ csrf_token() }}` manualmente.
- Em ambiente de testes, `WTF_CSRF_ENABLED = False`.

## Isolamento de Dados

Checklist de isolamento por camada:

| Camada | Mecanismo |
|--------|-----------|
| Serviços | Toda query filtra por `family_id` |
| Rotas | `abort(404)` quando `get_*(id, family_id)` retorna `None` |
| Templates | Só exibem dados já filtrados pela rota |
| ORM | Relacionamentos usam `lazy='dynamic'` para evitar load acidental |

## Boas Práticas

- Senhas com mínimo de 8 caracteres (validado no form `RegisterForm`).
- Variáveis de ambiente para segredos — nunca no código fonte.
- `SECRET_KEY` obrigatória em produção (diferente do padrão de dev).
- `DEBUG = False` em produção.
- Queries parametrizadas via SQLAlchemy — sem SQL concatenado.

## Checklist de Revisão

- [ ] Nenhuma rota privada sem `@login_required`
- [ ] Nenhuma rota com dados sensíveis sem `@family_required`
- [ ] Nenhum `family_id` implícito (sempre passado explicitamente)
- [ ] Nenhum `float` para dinheiro
- [ ] Nenhuma senha em texto puro
- [ ] CSRF ativo em todos os formulários POST
- [ ] `SECRET_KEY` diferente de `dev-secret-key` em produção
