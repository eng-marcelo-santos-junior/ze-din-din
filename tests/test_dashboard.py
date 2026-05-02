from datetime import date
import pytest

from app.auth.services import register_user
from app.families.services import create_family
from app.accounts.services import create_account
from app.categories.services import get_categories
from app.transactions.services import create_transaction
from app.models.transaction import TransactionType, TransactionStatus
from app.models.account import AccountType
from app.dashboard.services import (
    DashboardFilters,
    get_total_balance,
    get_month_income,
    get_month_expenses,
    get_month_result,
    get_month_transaction_count,
    get_expenses_by_category,
    get_income_vs_expense_by_month,
    get_recent_transactions,
    get_top_expense_category,
)

TODAY = date(2026, 5, 1)
FILTERS = DashboardFilters(month=5, year=2026)
OTHER_MONTH = DashboardFilters(month=4, year=2026)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def user(app_ctx):
    return register_user('Ana Lima', 'ana@test.com', 'senha1234')


@pytest.fixture
def other_user(app_ctx):
    return register_user('Bruno Costa', 'bruno@test.com', 'senha1234')


@pytest.fixture
def family(user):
    return create_family('Família Lima', 'BRL', user.id)


@pytest.fixture
def other_family(other_user):
    return create_family('Família Costa', 'BRL', other_user.id)


@pytest.fixture
def account(family, user):
    return create_account(family.id, user.id, 'Nubank', AccountType.CHECKING, '1.000,00')


@pytest.fixture
def account2(family, user):
    return create_account(family.id, user.id, 'Poupança', AccountType.SAVINGS, '500,00')


@pytest.fixture
def other_account(other_family, other_user):
    return create_account(other_family.id, other_user.id, 'Itaú', AccountType.CHECKING, '800,00')


def _income(family, user, account, amount='2.000,00', tx_date=None):
    return create_transaction(
        family_id=family.id, user_id=user.id, account_id=account.id,
        tx_type=TransactionType.INCOME, description='Salário',
        amount_str=amount, transaction_date=tx_date or TODAY,
        status=TransactionStatus.RECEIVED,
    )


def _expense(family, user, account, amount='500,00', desc='Mercado', tx_date=None):
    return create_transaction(
        family_id=family.id, user_id=user.id, account_id=account.id,
        tx_type=TransactionType.EXPENSE, description=desc,
        amount_str=amount, transaction_date=tx_date or TODAY,
        status=TransactionStatus.PAID,
    )


# ── Saldo Total ───────────────────────────────────────────────────────────────

class TestSaldoTotal:
    def test_soma_contas_ativas(self, family, user, account):
        assert get_total_balance(family.id) == 100000  # R$ 1.000,00

    def test_duas_contas(self, family, user, account, account2):
        assert get_total_balance(family.id) == 150000  # 1.000 + 500

    def test_zero_sem_contas(self, family):
        assert get_total_balance(family.id) == 0

    def test_nao_mistura_familias(self, family, user, account, other_family, other_user, other_account):
        assert get_total_balance(family.id) == 100000
        assert get_total_balance(other_family.id) == 80000


# ── Receitas do Mês ───────────────────────────────────────────────────────────

class TestReceitasMes:
    def test_calcula_corretamente(self, family, user, account):
        _income(family, user, account, '3.000,00')
        assert get_month_income(family.id, FILTERS) == 300000

    def test_soma_multiplas_receitas(self, family, user, account):
        _income(family, user, account, '1.000,00')
        _income(family, user, account, '500,00')
        assert get_month_income(family.id, FILTERS) == 150000

    def test_zero_sem_receitas(self, family, user, account):
        assert get_month_income(family.id, FILTERS) == 0

    def test_ignora_outro_mes(self, family, user, account):
        _income(family, user, account, '3.000,00', tx_date=date(2026, 4, 1))
        assert get_month_income(family.id, FILTERS) == 0

    def test_filtra_por_conta(self, family, user, account, account2):
        _income(family, user, account, '1.000,00')
        _income(family, user, account2, '2.000,00')
        f = DashboardFilters(month=5, year=2026, account_id=account.id)
        assert get_month_income(family.id, f) == 100000


# ── Despesas do Mês ───────────────────────────────────────────────────────────

class TestDespesasMes:
    def test_calcula_corretamente(self, family, user, account):
        _expense(family, user, account, '500,00')
        assert get_month_expenses(family.id, FILTERS) == 50000

    def test_retorna_valor_positivo(self, family, user, account):
        _expense(family, user, account, '1.200,00')
        assert get_month_expenses(family.id, FILTERS) > 0

    def test_zero_sem_despesas(self, family, user, account):
        assert get_month_expenses(family.id, FILTERS) == 0

    def test_ignora_outro_mes(self, family, user, account):
        _expense(family, user, account, '500,00', tx_date=date(2026, 4, 1))
        assert get_month_expenses(family.id, FILTERS) == 0


# ── Resultado do Mês ──────────────────────────────────────────────────────────

class TestResultadoMes:
    def test_resultado_positivo(self, family, user, account):
        _income(family, user, account, '3.000,00')
        _expense(family, user, account, '1.000,00')
        assert get_month_result(family.id, FILTERS) == 200000

    def test_resultado_negativo(self, family, user, account):
        _expense(family, user, account, '2.000,00')
        assert get_month_result(family.id, FILTERS) == -200000

    def test_resultado_zero(self, family, user, account):
        _income(family, user, account, '1.000,00')
        _expense(family, user, account, '1.000,00')
        assert get_month_result(family.id, FILTERS) == 0


# ── Transações Canceladas ─────────────────────────────────────────────────────

class TestTransacoesCanceladas:
    def test_cancelada_nao_entra_nas_receitas(self, family, user, account):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.INCOME, description='Cancelada',
            amount_str='1.000,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED,
        )
        assert get_month_income(family.id, FILTERS) == 0

    def test_cancelada_nao_entra_nas_despesas(self, family, user, account):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Cancelada',
            amount_str='1.000,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED,
        )
        assert get_month_expenses(family.id, FILTERS) == 0

    def test_cancelada_nao_conta_no_total(self, family, user, account):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Cancelada',
            amount_str='1.000,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED,
        )
        assert get_month_transaction_count(family.id, FILTERS) == 0

    def test_cancelada_nao_aparece_nas_categorias(self, family, user, account):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Cancelada',
            amount_str='500,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED,
        )
        cats = get_expenses_by_category(family.id, FILTERS)
        assert cats == []


# ── Isolamento por Família ────────────────────────────────────────────────────

class TestIsolamentoPorFamilia:
    def test_receita_nao_mistura_familias(
        self, family, user, account, other_family, other_user, other_account
    ):
        _income(family, user, account, '2.000,00')
        _income(other_family, other_user, other_account, '9.999,00')
        assert get_month_income(family.id, FILTERS) == 200000

    def test_despesa_nao_mistura_familias(
        self, family, user, account, other_family, other_user, other_account
    ):
        _expense(family, user, account, '300,00')
        _expense(other_family, other_user, other_account, '9.999,00')
        assert get_month_expenses(family.id, FILTERS) == 30000

    def test_saldo_nao_mistura_familias(
        self, family, user, account, other_family, other_user, other_account
    ):
        assert get_total_balance(family.id) == 100000
        assert get_total_balance(other_family.id) == 80000

    def test_categorias_nao_misturam_familias(
        self, family, user, account, other_family, other_user, other_account
    ):
        _expense(family, user, account, '200,00', desc='Mercado')
        _expense(other_family, other_user, other_account, '999,00', desc='Carro')
        cats = get_expenses_by_category(family.id, FILTERS)
        total = sum(c['total_cents'] for c in cats)
        assert total == 20000

    def test_recentes_nao_misturam_familias(
        self, family, user, account, other_family, other_user, other_account
    ):
        _expense(family, user, account, '100,00')
        _expense(other_family, other_user, other_account, '999,00')
        txs = get_recent_transactions(family.id)
        assert all(tx.family_id == family.id for tx in txs)


# ── Despesas por Categoria e Top Categoria ────────────────────────────────────

class TestDespesasPorCategoria:
    def test_agrupa_por_categoria(self, family, user, account):
        cats = get_categories(family.id, category_type='EXPENSE')
        cat1, cat2 = cats[0], cats[1]
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='A',
            amount_str='300,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=cat1.id,
        )
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='B',
            amount_str='100,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=cat2.id,
        )
        result = get_expenses_by_category(family.id, FILTERS)
        assert len(result) == 2
        assert all(c['total_cents'] > 0 for c in result)

    def test_top_categoria_maior_gasto(self, family, user, account):
        cats = get_categories(family.id, category_type='EXPENSE')
        cat1, cat2 = cats[0], cats[1]
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Grande',
            amount_str='1.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=cat1.id,
        )
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Pequena',
            amount_str='100,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=cat2.id,
        )
        top = get_top_expense_category(family.id, FILTERS)
        assert top is not None
        assert top['total_cents'] == 100000

    def test_top_categoria_none_sem_despesas(self, family):
        top = get_top_expense_category(family.id, FILTERS)
        assert top is None


# ── Últimas Transações e Histórico ────────────────────────────────────────────

class TestUltimasTransacoes:
    def test_retorna_lista(self, family, user, account):
        _expense(family, user, account)
        txs = get_recent_transactions(family.id)
        assert len(txs) >= 1

    def test_limite_respeitado(self, family, user, account):
        for i in range(15):
            _expense(family, user, account, '10,00', desc=f'Tx {i}')
        txs = get_recent_transactions(family.id, limit=10)
        assert len(txs) == 10

    def test_canceladas_nao_aparecem(self, family, user, account):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Cancelada',
            amount_str='100,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED,
        )
        txs = get_recent_transactions(family.id)
        assert all(tx.status != TransactionStatus.CANCELED for tx in txs)


# ── Rota do Dashboard ─────────────────────────────────────────────────────────

class TestRotaDashboard:
    def _login(self, client, email, password='senha1234'):
        client.post('/auth/login', data={'email': email, 'password': password})

    def test_rota_exige_login(self, client):
        r = client.get('/dashboard', follow_redirects=False)
        assert r.status_code == 302
        assert '/auth/login' in r.headers['Location']

    def test_rota_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'ana@test.com')
        r = client.get('/dashboard')
        assert r.status_code == 200

    def test_filtro_mes_ano(self, app_ctx, client, family, user):
        self._login(client, 'ana@test.com')
        r = client.get('/dashboard?month=3&year=2026')
        assert r.status_code == 200

    def test_filtro_conta(self, app_ctx, client, family, user, account):
        self._login(client, 'ana@test.com')
        r = client.get(f'/dashboard?account_id={account.id}')
        assert r.status_code == 200
