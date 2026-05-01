from datetime import date
import pytest

from app.auth.services import register_user
from app.families.services import create_family
from app.accounts.services import create_account
from app.categories.services import get_categories
from app.transactions.services import create_transaction
from app.models.transaction import TransactionType, TransactionStatus
from app.models.account import AccountType
from app.budgets.services import (
    create_budget, update_budget, delete_budget,
    get_budget, get_budget_overview, copy_previous_month_budget,
)

TODAY = date(2026, 5, 1)


@pytest.fixture
def user(app_ctx):
    return register_user('Carla Melo', 'carla@test.com', 'senha1234')


@pytest.fixture
def other_user(app_ctx):
    return register_user('Daniel Faria', 'daniel@test.com', 'senha1234')


@pytest.fixture
def family(user):
    return create_family('Família Melo', 'BRL', user.id)


@pytest.fixture
def other_family(other_user):
    return create_family('Família Faria', 'BRL', other_user.id)


@pytest.fixture
def account(family, user):
    return create_account(family.id, user.id, 'Banco', AccountType.CHECKING, '5.000,00')


@pytest.fixture
def expense_cat(family):
    return get_categories(family.id, category_type='EXPENSE')[0]


@pytest.fixture
def expense_cat2(family):
    return get_categories(family.id, category_type='EXPENSE')[1]


# ── Criar e persistir ─────────────────────────────────────────────────────────

class TestCriarOrcamento:
    def test_cria_orcamento(self, family, expense_cat):
        b = create_budget(family.id, expense_cat.id, 5, 2026, '1.000,00')
        assert b.id is not None
        assert b.planned_amount_cents == 100000
        assert b.month == 5
        assert b.year == 2026
        assert b.family_id == family.id

    def test_upsert_existente(self, family, expense_cat):
        b1 = create_budget(family.id, expense_cat.id, 5, 2026, '500,00')
        b2 = create_budget(family.id, expense_cat.id, 5, 2026, '800,00')
        assert b1.id == b2.id
        assert b2.planned_amount_cents == 80000

    def test_atualiza_valor(self, family, expense_cat):
        b = create_budget(family.id, expense_cat.id, 5, 2026, '500,00')
        update_budget(b, '1.200,00')
        assert b.planned_amount_cents == 120000

    def test_deleta_orcamento(self, family, expense_cat):
        b = create_budget(family.id, expense_cat.id, 5, 2026, '500,00')
        budget_id = b.id
        delete_budget(b)
        assert get_budget(budget_id, family.id) is None


# ── Overview: planejado vs. realizado ─────────────────────────────────────────

class TestOverview:
    def test_overview_vazio(self, family):
        result = get_budget_overview(family.id, 5, 2026)
        assert result == []

    def test_overview_sem_despesas(self, family, expense_cat):
        create_budget(family.id, expense_cat.id, 5, 2026, '1.000,00')
        overview = get_budget_overview(family.id, 5, 2026)
        assert len(overview) == 1
        item = overview[0]
        assert item['realized_cents'] == 0
        assert item['pct'] == 0
        assert item['health'] == 'healthy'

    def test_orcamento_saudavel(self, family, user, account, expense_cat):
        create_budget(family.id, expense_cat.id, 5, 2026, '1.000,00')
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Compra',
            amount_str='600,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        item = get_budget_overview(family.id, 5, 2026)[0]
        assert item['realized_cents'] == 60000
        assert item['pct'] == 60
        assert item['health'] == 'healthy'

    def test_orcamento_atencao(self, family, user, account, expense_cat):
        create_budget(family.id, expense_cat.id, 5, 2026, '1.000,00')
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Gasto',
            amount_str='850,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        item = get_budget_overview(family.id, 5, 2026)[0]
        assert item['health'] == 'warning'

    def test_orcamento_excedido(self, family, user, account, expense_cat):
        create_budget(family.id, expense_cat.id, 5, 2026, '500,00')
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Grande gasto',
            amount_str='600,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        item = get_budget_overview(family.id, 5, 2026)[0]
        assert item['health'] == 'exceeded'
        assert item['pct'] >= 100

    def test_cancelada_nao_conta_no_realizado(self, family, user, account, expense_cat):
        create_budget(family.id, expense_cat.id, 5, 2026, '1.000,00')
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Cancelada',
            amount_str='800,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED, category_id=expense_cat.id,
        )
        item = get_budget_overview(family.id, 5, 2026)[0]
        assert item['realized_cents'] == 0


# ── Copiar mês anterior ───────────────────────────────────────────────────────

class TestCopiarMesAnterior:
    def test_copia_orcamentos(self, family, expense_cat, expense_cat2):
        create_budget(family.id, expense_cat.id, 4, 2026, '1.000,00')
        create_budget(family.id, expense_cat2.id, 4, 2026, '500,00')
        copied = copy_previous_month_budget(family.id, 5, 2026)
        assert copied == 2
        overview = get_budget_overview(family.id, 5, 2026)
        assert len(overview) == 2

    def test_nao_duplica_existentes(self, family, expense_cat):
        create_budget(family.id, expense_cat.id, 4, 2026, '1.000,00')
        create_budget(family.id, expense_cat.id, 5, 2026, '900,00')
        copied = copy_previous_month_budget(family.id, 5, 2026)
        assert copied == 0

    def test_mes_anterior_vazio(self, family):
        copied = copy_previous_month_budget(family.id, 5, 2026)
        assert copied == 0

    def test_copia_janeiro_pega_dezembro_anterior(self, family, expense_cat):
        create_budget(family.id, expense_cat.id, 12, 2025, '1.000,00')
        copied = copy_previous_month_budget(family.id, 1, 2026)
        assert copied == 1


# ── Isolamento por família ────────────────────────────────────────────────────

class TestIsolamento:
    def test_nao_acessa_orcamento_de_outra_familia(self, family, other_family, expense_cat):
        b = create_budget(family.id, expense_cat.id, 5, 2026, '1.000,00')
        assert get_budget(b.id, other_family.id) is None

    def test_overview_isolada(self, family, other_family, expense_cat):
        create_budget(family.id, expense_cat.id, 5, 2026, '1.000,00')
        result = get_budget_overview(other_family.id, 5, 2026)
        assert result == []


# ── Rotas ─────────────────────────────────────────────────────────────────────

class TestRotasBudgets:
    def _login(self, client, email):
        client.post('/auth/login', data={'email': email, 'password': 'senha1234'})

    def test_lista_exige_login(self, client):
        r = client.get('/budgets', follow_redirects=False)
        assert r.status_code == 302

    def test_lista_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'carla@test.com')
        r = client.get('/budgets')
        assert r.status_code == 200

    def test_criar_orcamento(self, app_ctx, client, family, user, expense_cat):
        self._login(client, 'carla@test.com')
        r = client.post('/budgets/new', data={
            'category_id': str(expense_cat.id),
            'month': '5',
            'year': '2026',
            'planned_amount': '1.000,00',
        }, follow_redirects=False)
        assert r.status_code == 302
