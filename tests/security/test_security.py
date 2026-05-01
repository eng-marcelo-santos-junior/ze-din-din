"""Testes de segurança — isolamento, proteção de rotas e senhas."""
from datetime import date
import pytest

from app.auth.services import register_user
from app.families.services import create_family
from app.accounts.services import create_account
from app.categories.services import get_categories
from app.transactions.services import create_transaction, get_transaction
from app.goals.services import create_goal, get_goal
from app.bills.services import create_bill, get_bill
from app.budgets.services import create_budget, get_budget
from app.models.account import AccountType
from app.models.transaction import TransactionType, TransactionStatus
from app.models.bill import BillType
from app.utils.permissions import user_has_access_to_family

TODAY = date(2026, 5, 1)
TARGET = date(2027, 5, 1)


@pytest.fixture
def user_a(app_ctx):
    return register_user('Alice Silva', 'alice@test.com', 'senha1234')


@pytest.fixture
def user_b(app_ctx):
    return register_user('Bruno Costa', 'bruno@test.com', 'senha1234')


@pytest.fixture
def family_a(user_a):
    return create_family('Família Alice', 'BRL', user_a.id)


@pytest.fixture
def family_b(user_b):
    return create_family('Família Bruno', 'BRL', user_b.id)


@pytest.fixture
def account_a(family_a, user_a):
    return create_account(family_a.id, user_a.id, 'Conta Alice', AccountType.CHECKING, '5.000,00')


@pytest.fixture
def account_b(family_b, user_b):
    return create_account(family_b.id, user_b.id, 'Conta Bruno', AccountType.CHECKING, '5.000,00')


@pytest.fixture
def expense_cat_a(family_a):
    return get_categories(family_a.id, category_type='EXPENSE')[0]


@pytest.fixture
def expense_cat_b(family_b):
    return get_categories(family_b.id, category_type='EXPENSE')[0]


# ── Proteção de rotas (login obrigatório) ─────────────────────────────────────

class TestRotasExigemLogin:
    PRIVATE_ROUTES = [
        '/dashboard',
        '/transactions',
        '/accounts',
        '/categories',
        '/budgets',
        '/bills',
        '/goals',
        '/reports',
        '/reports/cash-flow',
        '/reports/categories',
        '/reports/budget',
        '/reports/biggest-expenses',
        '/reports/net-worth',
        '/families/members',
        '/families/settings',
    ]

    @pytest.mark.parametrize('route', PRIVATE_ROUTES)
    def test_rota_privada_redireciona_sem_login(self, client, route):
        r = client.get(route, follow_redirects=False)
        assert r.status_code == 302, f"Rota {route} deveria redirecionar sem login"

    def test_rota_de_login_acessivel_sem_autenticacao(self, client):
        r = client.get('/auth/login')
        assert r.status_code == 200

    def test_rota_de_registro_acessivel_sem_autenticacao(self, client):
        r = client.get('/auth/register')
        assert r.status_code == 200


# ── Isolamento por família (nível de serviço) ─────────────────────────────────

class TestIsolamentoServico:
    def test_transacao_nao_acessivel_por_outra_familia(
            self, family_a, family_b, user_a, account_a, expense_cat_a):
        tx = create_transaction(
            family_id=family_a.id, user_id=user_a.id, account_id=account_a.id,
            tx_type=TransactionType.EXPENSE, description='Gasto A',
            amount_str='100,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat_a.id,
        )
        assert get_transaction(tx.id, family_b.id) is None

    def test_meta_nao_acessivel_por_outra_familia(self, family_a, family_b):
        g = create_goal(family_a.id, 'Meta A', '10.000,00')
        assert get_goal(g.id, family_b.id) is None

    def test_conta_a_pagar_nao_acessivel_por_outra_familia(self, family_a, family_b):
        bill = create_bill(family_a.id, 'Conta A', BillType.PAYABLE, '500,00', TARGET)
        assert get_bill(bill.id, family_b.id) is None

    def test_orcamento_nao_acessivel_por_outra_familia(
            self, family_a, family_b, expense_cat_a):
        b = create_budget(family_a.id, expense_cat_a.id, 5, 2026, '1.000,00')
        assert get_budget(b.id, family_b.id) is None


# ── Isolamento por família (nível HTTP) ───────────────────────────────────────

class TestIsolamentoHTTP:
    def _login(self, client, email):
        client.post('/auth/login', data={'email': email, 'password': 'senha1234'})

    def test_usuario_b_nao_acessa_meta_de_a(
            self, client, family_a, family_b, user_a, user_b):
        goal = create_goal(family_a.id, 'Meta de A', '5.000,00')
        self._login(client, 'bruno@test.com')
        r = client.get(f'/goals/{goal.id}/edit')
        assert r.status_code == 404

    def test_usuario_b_nao_acessa_conta_a_pagar_de_a(
            self, client, family_a, family_b, user_a, user_b):
        bill = create_bill(family_a.id, 'Conta de A', BillType.PAYABLE, '200,00', TARGET)
        self._login(client, 'bruno@test.com')
        r = client.get(f'/bills/{bill.id}/edit')
        assert r.status_code == 404

    def test_usuario_b_nao_acessa_transacao_de_a(
            self, client, family_a, family_b, user_a, user_b,
            account_a, expense_cat_a):
        tx = create_transaction(
            family_id=family_a.id, user_id=user_a.id, account_id=account_a.id,
            tx_type=TransactionType.EXPENSE, description='Gasto privado',
            amount_str='100,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat_a.id,
        )
        self._login(client, 'bruno@test.com')
        r = client.get(f'/transactions/{tx.id}/edit')
        assert r.status_code == 404

    def test_usuario_b_nao_acessa_conta_bancaria_de_a(
            self, client, family_a, family_b, user_a, user_b, account_a):
        self._login(client, 'bruno@test.com')
        r = client.get(f'/accounts/{account_a.id}/edit')
        assert r.status_code == 404


# ── Segurança de senhas ───────────────────────────────────────────────────────

class TestSegurancaSenha:
    def test_senha_nunca_armazenada_em_texto_puro(self, app_ctx):
        u = register_user('Seguro User', 'seguro@test.com', 'minha_senha_secreta')
        assert u.password_hash != 'minha_senha_secreta'

    def test_hash_nao_e_vazio(self, app_ctx):
        u = register_user('Hash User', 'hashtest@test.com', 'senha')
        assert len(u.password_hash) > 30

    def test_check_password_funciona(self, app_ctx):
        u = register_user('Check User', 'check@test.com', 'correta')
        assert u.check_password('correta') is True
        assert u.check_password('errada') is False

    def test_dois_usuarios_mesma_senha_hashes_diferentes(self, app_ctx):
        u1 = register_user('User 1', 'u1@test.com', 'mesmasenha')
        u2 = register_user('User 2', 'u2@test.com', 'mesmasenha')
        assert u1.password_hash != u2.password_hash


# ── Helper de permissões ──────────────────────────────────────────────────────

class TestPermissionsHelper:
    def test_membro_tem_acesso_a_propria_familia(self, family_a, user_a):
        assert user_has_access_to_family(user_a.id, family_a.id) is True

    def test_nao_membro_nao_tem_acesso(self, family_a, user_b):
        assert user_has_access_to_family(user_b.id, family_a.id) is False

    def test_usuario_inexistente_nao_tem_acesso(self, family_a):
        assert user_has_access_to_family(99999, family_a.id) is False
