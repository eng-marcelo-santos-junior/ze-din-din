"""Testes de integração: fluxo completo do usuário.

Testa a jornada end-to-end: cadastro → família → conta → categorias → transação → dashboard.
"""
from datetime import date
import pytest

from app.auth.services import register_user, authenticate
from app.families.services import create_family
from app.accounts.services import create_account, get_account
from app.categories.services import get_categories, create_category
from app.transactions.services import create_transaction, get_transactions, TransactionFilters
from app.models.account import AccountType
from app.models.category import CategoryType
from app.models.transaction import TransactionType, TransactionStatus

TODAY = date(2026, 5, 1)


@pytest.fixture
def user(app_ctx):
    return register_user('Joana Alves', 'joana@test.com', 'senha1234')


@pytest.fixture
def family(user):
    return create_family('Família Alves', 'BRL', user.id)


@pytest.fixture
def account(family, user):
    return create_account(family.id, user.id, 'Banco do Brasil', AccountType.CHECKING, '5.000,00')


@pytest.fixture
def expense_cat(family):
    return get_categories(family.id, category_type='EXPENSE')[0]


@pytest.fixture
def income_cat(family):
    return get_categories(family.id, category_type='INCOME')[0]


# ── Autenticação ──────────────────────────────────────────────────────────────

class TestFluxoAutenticacao:
    def test_registra_usuario(self, app_ctx):
        u = register_user('Teste User', 'teste@example.com', 'senha1234')
        assert u.id is not None
        assert u.email == 'teste@example.com'

    def test_senha_armazenada_como_hash(self, app_ctx):
        u = register_user('Hash User', 'hash@example.com', 'senha1234')
        assert u.password_hash != 'senha1234'
        assert len(u.password_hash) > 20

    def test_autentica_usuario_valido(self, app_ctx):
        register_user('Auth User', 'auth@example.com', 'senha1234')
        u = authenticate('auth@example.com', 'senha1234')
        assert u is not None

    def test_rejeita_senha_errada(self, app_ctx):
        register_user('Wrong Pass', 'wrong@example.com', 'correta')
        assert authenticate('wrong@example.com', 'errada') is None

    def test_rejeita_email_inexistente(self, app_ctx):
        assert authenticate('naoexiste@example.com', 'qualquer') is None


# ── Família ───────────────────────────────────────────────────────────────────

class TestFluxoFamilia:
    def test_cria_familia(self, user, app_ctx):
        f = create_family('Família Teste', 'BRL', user.id)
        assert f.id is not None
        assert f.name == 'Família Teste'

    def test_usuario_vira_owner_da_familia(self, family, user):
        from app.families.services import get_members
        from app.models.family import FamilyRole
        members = get_members(family.id)
        assert any(m.user_id == user.id and m.role == FamilyRole.OWNER for m in members)


# ── Contas ────────────────────────────────────────────────────────────────────

class TestFluxoConta:
    def test_cria_conta_com_saldo_inicial(self, family, user, app_ctx):
        acc = create_account(family.id, user.id, 'Poupança', AccountType.SAVINGS, '1.500,00')
        assert acc.initial_balance_cents == 150000
        assert acc.current_balance_cents == 150000

    def test_conta_pertence_a_familia(self, account, family):
        assert account.family_id == family.id

    def test_get_account_com_family_errada_retorna_none(self, account, family):
        assert get_account(account.id, family.id + 99) is None


# ── Categorias ────────────────────────────────────────────────────────────────

class TestFluxoCategorias:
    def test_familia_tem_categorias_padrao(self, family, app_ctx):
        cats = get_categories(family.id)
        assert len(cats) > 0

    def test_categorias_separadas_por_tipo(self, family, app_ctx):
        expense_cats = get_categories(family.id, category_type='EXPENSE')
        income_cats = get_categories(family.id, category_type='INCOME')
        assert len(expense_cats) > 0
        assert len(income_cats) > 0
        assert all(c.type == 'EXPENSE' for c in expense_cats)
        assert all(c.type == 'INCOME' for c in income_cats)

    def test_cria_categoria_customizada(self, family, app_ctx):
        cat = create_category(family.id, 'Academia', CategoryType.EXPENSE, '#ff5500')
        assert cat.id is not None
        assert cat.name == 'Academia'


# ── Transações ────────────────────────────────────────────────────────────────

class TestFluxoTransacoes:
    def test_receita_aumenta_saldo(self, family, user, account, income_cat):
        balance_before = account.current_balance_cents
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.INCOME, description='Salário',
            amount_str='3.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=income_cat.id,
        )
        assert account.current_balance_cents == balance_before + 300000

    def test_despesa_reduz_saldo(self, family, user, account, expense_cat):
        balance_before = account.current_balance_cents
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Aluguel',
            amount_str='1.200,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        assert account.current_balance_cents == balance_before - 120000

    def test_cancelada_nao_altera_saldo(self, family, user, account, expense_cat):
        balance_before = account.current_balance_cents
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Cancelada',
            amount_str='500,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED, category_id=expense_cat.id,
        )
        assert account.current_balance_cents == balance_before

    def test_filtro_por_tipo(self, family, user, account, income_cat, expense_cat):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.INCOME, description='Renda',
            amount_str='3.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=income_cat.id,
        )
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Gasto',
            amount_str='1.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        filters = TransactionFilters(type=TransactionType.INCOME)
        pagination = get_transactions(family.id, filters=filters)
        assert all(tx.type == TransactionType.INCOME for tx in pagination.items)

    def test_transferencia_entre_contas(self, family, user, account):
        from app.transactions.services import create_transfer
        second = create_account(family.id, user.id, 'Poupança', AccountType.SAVINGS, '0')
        from_balance = account.current_balance_cents
        to_balance = second.current_balance_cents
        create_transfer(
            family_id=family.id, user_id=user.id,
            from_account_id=account.id, to_account_id=second.id,
            amount_str='1.000,00', description='Transferência',
            transaction_date=TODAY,
        )
        assert account.current_balance_cents == from_balance - 100000
        assert second.current_balance_cents == to_balance + 100000


# ── Jornada completa via HTTP ─────────────────────────────────────────────────

class TestJornadaHTTP:
    def test_cadastro_login_e_acesso_ao_dashboard(self, client):
        # 1. Cadastro (confirm_password é o nome real do campo no RegisterForm)
        client.post('/auth/register', data={
            'name': 'João Oliveira',
            'email': 'joao@example.com',
            'password': 'senha1234',
            'confirm_password': 'senha1234',
        }, follow_redirects=True)

        # 2. Criar família (usuário já logado após cadastro)
        client.post('/families/new', data={
            'name': 'Família Oliveira',
            'currency': 'BRL',
        }, follow_redirects=True)

        # 3. Dashboard acessível
        r = client.get('/dashboard')
        assert r.status_code == 200
