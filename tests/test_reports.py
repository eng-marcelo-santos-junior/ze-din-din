from datetime import date
import pytest

from app.auth.services import register_user
from app.families.services import create_family
from app.accounts.services import create_account
from app.categories.services import get_categories
from app.budgets.services import create_budget
from app.models.account import AccountType
from app.models.transaction import TransactionType, TransactionStatus
from app.transactions.services import create_transaction
from app.reports.services import (
    get_monthly_cash_flow,
    get_expenses_by_category,
    get_expenses_by_member,
    get_budget_vs_actual,
    get_biggest_expenses,
    get_net_worth_summary,
)

TODAY = date(2026, 5, 1)


@pytest.fixture
def user(app_ctx):
    return register_user('Laura Matos', 'laura@test.com', 'senha1234')


@pytest.fixture
def other_user(app_ctx):
    return register_user('Renato Braga', 'renato@test.com', 'senha1234')


@pytest.fixture
def family(user):
    return create_family('Família Matos', 'BRL', user.id)


@pytest.fixture
def other_family(other_user):
    return create_family('Família Braga', 'BRL', other_user.id)


@pytest.fixture
def account(family, user):
    return create_account(family.id, user.id, 'Banco', AccountType.CHECKING, '10.000,00')


@pytest.fixture
def other_account(other_family, other_user):
    return create_account(other_family.id, other_user.id, 'Banco', AccountType.CHECKING, '5.000,00')


@pytest.fixture
def expense_cat(family):
    return get_categories(family.id, category_type='EXPENSE')[0]


@pytest.fixture
def expense_cat2(family):
    return get_categories(family.id, category_type='EXPENSE')[1]


@pytest.fixture
def income_cat(family):
    return get_categories(family.id, category_type='INCOME')[0]


# ── Fluxo de caixa ────────────────────────────────────────────────────────────

class TestFluxoDeCaixa:
    def test_retorna_lista_com_num_meses(self, family):
        result = get_monthly_cash_flow(family.id, num_months=6)
        assert len(result) == 6

    def test_meses_vazios_sao_zero(self, family):
        result = get_monthly_cash_flow(family.id, num_months=3)
        for row in result:
            assert row['income_cents'] == 0
            assert row['expense_cents'] == 0
            assert row['result_cents'] == 0

    def test_receita_aparece_no_mes_correto(self, family, user, account, income_cat):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.INCOME, description='Salário',
            amount_str='3.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=income_cat.id,
        )
        result = get_monthly_cash_flow(family.id, num_months=1)
        assert result[-1]['income_cents'] == 300000
        assert result[-1]['expense_cents'] == 0

    def test_despesa_aparece_no_mes_correto(self, family, user, account, expense_cat):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Aluguel',
            amount_str='1.500,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        result = get_monthly_cash_flow(family.id, num_months=1)
        assert result[-1]['expense_cents'] == 150000
        assert result[-1]['income_cents'] == 0

    def test_resultado_liquido_correto(self, family, user, account, income_cat, expense_cat):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.INCOME, description='Renda',
            amount_str='5.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=income_cat.id,
        )
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Gasto',
            amount_str='2.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        result = get_monthly_cash_flow(family.id, num_months=1)
        assert result[-1]['result_cents'] == 300000

    def test_cancelada_nao_entra_no_fluxo(self, family, user, account, expense_cat):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Cancelada',
            amount_str='999,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED, category_id=expense_cat.id,
        )
        result = get_monthly_cash_flow(family.id, num_months=1)
        assert result[-1]['expense_cents'] == 0

    def test_tem_label_correto(self, family):
        result = get_monthly_cash_flow(family.id, num_months=1)
        assert result[-1]['label'] == 'Mai/26'

    def test_isolamento_por_familia(self, family, other_family, user, other_user,
                                    account, other_account, income_cat):
        other_income_cat = get_categories(other_family.id, category_type='INCOME')[0]
        create_transaction(
            family_id=other_family.id, user_id=other_user.id, account_id=other_account.id,
            tx_type=TransactionType.INCOME, description='Salário outra família',
            amount_str='9.999,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=other_income_cat.id,
        )
        result = get_monthly_cash_flow(family.id, num_months=1)
        assert result[-1]['income_cents'] == 0


# ── Despesas por categoria ────────────────────────────────────────────────────

class TestDespesasPorCategoria:
    def test_retorna_vazio_sem_despesas(self, family):
        result = get_expenses_by_category(family.id)
        assert result == []

    def test_soma_despesas_por_categoria(self, family, user, account, expense_cat, expense_cat2):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Gasto A',
            amount_str='1.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Gasto B',
            amount_str='500,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat2.id,
        )
        result = get_expenses_by_category(family.id)
        assert len(result) == 2
        totals = {r['name']: r['total_cents'] for r in result}
        assert totals[expense_cat.name] == 100000
        assert totals[expense_cat2.name] == 50000

    def test_percentual_soma_100(self, family, user, account, expense_cat, expense_cat2):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Gasto A',
            amount_str='3.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Gasto B',
            amount_str='1.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat2.id,
        )
        result = get_expenses_by_category(family.id)
        total_pct = sum(r['pct'] for r in result)
        assert total_pct == 100

    def test_cancelada_nao_entra(self, family, user, account, expense_cat):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Cancelada',
            amount_str='9.000,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED, category_id=expense_cat.id,
        )
        result = get_expenses_by_category(family.id)
        assert result == []

    def test_filtro_por_data(self, family, user, account, expense_cat):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Gasto antigo',
            amount_str='1.000,00', transaction_date=date(2026, 1, 10),
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Gasto maio',
            amount_str='500,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        result = get_expenses_by_category(family.id, start_date=date(2026, 5, 1))
        assert len(result) == 1
        assert result[0]['total_cents'] == 50000

    def test_isolamento_por_familia(self, family, other_family, user, other_user,
                                    account, other_account, expense_cat):
        other_exp_cat = get_categories(other_family.id, category_type='EXPENSE')[0]
        create_transaction(
            family_id=other_family.id, user_id=other_user.id, account_id=other_account.id,
            tx_type=TransactionType.EXPENSE, description='Despesa outra família',
            amount_str='5.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=other_exp_cat.id,
        )
        result = get_expenses_by_category(family.id)
        assert result == []


# ── Orçamento vs. realizado ───────────────────────────────────────────────────

class TestOrcamentoVsRealizado:
    def test_retorna_vazio_sem_orcamento(self, family):
        result = get_budget_vs_actual(family.id, 5, 2026)
        assert result == []

    def test_compara_planejado_com_realizado(self, family, user, account, expense_cat):
        create_budget(family.id, expense_cat.id, 5, 2026, '1.000,00')
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Gasto',
            amount_str='600,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        result = get_budget_vs_actual(family.id, 5, 2026)
        assert len(result) == 1
        assert result[0]['budget'].planned_amount_cents == 100000
        assert result[0]['realized_cents'] == 60000
        assert result[0]['pct'] == 60
        assert result[0]['health'] == 'healthy'

    def test_isolamento_por_familia(self, family, other_family, expense_cat):
        other_exp_cat = get_categories(other_family.id, category_type='EXPENSE')[0]
        create_budget(other_family.id, other_exp_cat.id, 5, 2026, '500,00')
        result = get_budget_vs_actual(family.id, 5, 2026)
        assert result == []


# ── Maiores despesas ──────────────────────────────────────────────────────────

class TestMaioresDespesas:
    def test_retorna_vazio_sem_despesas(self, family):
        result = get_biggest_expenses(family.id)
        assert result == []

    def test_ordenadas_por_valor_desc(self, family, user, account, expense_cat):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Pequena',
            amount_str='100,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Grande',
            amount_str='5.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Média',
            amount_str='1.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        result = get_biggest_expenses(family.id)
        amounts = [abs(tx.amount_cents) for tx in result]
        assert amounts == sorted(amounts, reverse=True)

    def test_respeita_limite(self, family, user, account, expense_cat):
        for i in range(5):
            create_transaction(
                family_id=family.id, user_id=user.id, account_id=account.id,
                tx_type=TransactionType.EXPENSE, description=f'Gasto {i}',
                amount_str='100,00', transaction_date=TODAY,
                status=TransactionStatus.PAID, category_id=expense_cat.id,
            )
        result = get_biggest_expenses(family.id, limit=3)
        assert len(result) == 3

    def test_cancelada_nao_entra(self, family, user, account, expense_cat):
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Cancelada',
            amount_str='9.999,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED, category_id=expense_cat.id,
        )
        result = get_biggest_expenses(family.id)
        assert result == []

    def test_filtro_por_conta(self, family, user, account, expense_cat):
        second_account = create_account(family.id, user.id, 'Outra', AccountType.CHECKING, '0')
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Na conta principal',
            amount_str='1.000,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=second_account.id,
            tx_type=TransactionType.EXPENSE, description='Na segunda conta',
            amount_str='999,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=expense_cat.id,
        )
        result = get_biggest_expenses(family.id, account_id=account.id)
        assert len(result) == 1
        assert result[0].description == 'Na conta principal'

    def test_isolamento_por_familia(self, family, other_family, user, other_user,
                                    account, other_account, expense_cat):
        other_exp_cat = get_categories(other_family.id, category_type='EXPENSE')[0]
        create_transaction(
            family_id=other_family.id, user_id=other_user.id, account_id=other_account.id,
            tx_type=TransactionType.EXPENSE, description='Despesa outra família',
            amount_str='99.999,00', transaction_date=TODAY,
            status=TransactionStatus.PAID, category_id=other_exp_cat.id,
        )
        result = get_biggest_expenses(family.id)
        assert result == []


# ── Patrimônio líquido ────────────────────────────────────────────────────────

class TestPatrimonioLiquido:
    def test_sem_contas_tudo_zero(self, family):
        summary = get_net_worth_summary(family.id)
        assert summary['accounts'] == []
        assert summary['total_assets'] == 0
        assert summary['total_liabilities'] == 0
        assert summary['net_worth'] == 0

    def test_calcula_patrimonio_positivo(self, family, user):
        create_account(family.id, user.id, 'Conta A', AccountType.CHECKING, '5.000,00')
        create_account(family.id, user.id, 'Conta B', AccountType.SAVINGS, '3.000,00')
        summary = get_net_worth_summary(family.id)
        assert summary['net_worth'] == 800000
        assert summary['total_assets'] == 800000
        assert summary['total_liabilities'] == 0

    def test_separa_ativos_e_passivos(self, family, user, account, expense_cat):
        from app.extensions import db
        from app.models.account import Account
        neg_account = create_account(family.id, user.id, 'Cartão', AccountType.CREDIT_CARD, '0')
        neg_account.current_balance_cents = -200000
        db.session.commit()
        summary = get_net_worth_summary(family.id)
        assert summary['total_liabilities'] == 200000
        assert summary['total_assets'] == account.current_balance_cents

    def test_isolamento_por_familia(self, family, other_family, other_user):
        create_account(other_family.id, other_user.id, 'Conta outra', AccountType.CHECKING, '50.000,00')
        summary = get_net_worth_summary(family.id)
        assert summary['accounts'] == []
        assert summary['net_worth'] == 0


# ── Rotas ─────────────────────────────────────────────────────────────────────

class TestRotasReports:
    def _login(self, client, email):
        client.post('/auth/login', data={'email': email, 'password': 'senha1234'})

    def test_index_exige_login(self, client):
        r = client.get('/reports', follow_redirects=False)
        assert r.status_code == 302

    def test_cash_flow_exige_login(self, client):
        r = client.get('/reports/cash-flow', follow_redirects=False)
        assert r.status_code == 302

    def test_categories_exige_login(self, client):
        r = client.get('/reports/categories', follow_redirects=False)
        assert r.status_code == 302

    def test_index_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'laura@test.com')
        r = client.get('/reports')
        assert r.status_code == 200

    def test_cash_flow_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'laura@test.com')
        r = client.get('/reports/cash-flow')
        assert r.status_code == 200

    def test_categories_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'laura@test.com')
        r = client.get('/reports/categories')
        assert r.status_code == 200

    def test_budget_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'laura@test.com')
        r = client.get('/reports/budget')
        assert r.status_code == 200

    def test_biggest_expenses_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'laura@test.com')
        r = client.get('/reports/biggest-expenses')
        assert r.status_code == 200

    def test_net_worth_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'laura@test.com')
        r = client.get('/reports/net-worth')
        assert r.status_code == 200

    def test_cash_flow_export_retorna_csv(self, app_ctx, client, family, user):
        self._login(client, 'laura@test.com')
        r = client.get('/reports/cash-flow/export')
        assert r.status_code == 200
        assert 'text/csv' in r.content_type

    def test_categories_export_retorna_csv(self, app_ctx, client, family, user):
        self._login(client, 'laura@test.com')
        r = client.get('/reports/categories/export')
        assert r.status_code == 200
        assert 'text/csv' in r.content_type

    def test_budget_export_retorna_csv(self, app_ctx, client, family, user):
        self._login(client, 'laura@test.com')
        r = client.get('/reports/budget/export')
        assert r.status_code == 200
        assert 'text/csv' in r.content_type

    def test_biggest_expenses_export_retorna_csv(self, app_ctx, client, family, user):
        self._login(client, 'laura@test.com')
        r = client.get('/reports/biggest-expenses/export')
        assert r.status_code == 200
        assert 'text/csv' in r.content_type

    def test_cash_flow_com_filtro_meses(self, app_ctx, client, family, user):
        self._login(client, 'laura@test.com')
        r = client.get('/reports/cash-flow?months=6')
        assert r.status_code == 200
