from datetime import date
import pytest

from app.auth.services import register_user
from app.families.services import create_family
from app.accounts.services import create_account
from app.categories.services import get_categories
from app.models.account import AccountType
from app.models.bill import BillStatus, BillType
from app.models.transaction import Transaction
from app.extensions import db
from app.bills.services import (
    create_bill, update_bill, get_bill, get_bills,
    pay_bill, cancel_bill,
)

TODAY = date(2026, 5, 1)
YESTERDAY = date(2026, 4, 30)
NEXT_WEEK = date(2026, 5, 8)


@pytest.fixture
def user(app_ctx):
    return register_user('Eva Lima', 'eva@test.com', 'senha1234')


@pytest.fixture
def other_user(app_ctx):
    return register_user('Fábio Cruz', 'fabio@test.com', 'senha1234')


@pytest.fixture
def family(user):
    return create_family('Família Lima', 'BRL', user.id)


@pytest.fixture
def other_family(other_user):
    return create_family('Família Cruz', 'BRL', other_user.id)


@pytest.fixture
def account(family, user):
    return create_account(family.id, user.id, 'Nubank', AccountType.CHECKING, '5.000,00')


@pytest.fixture
def other_account(other_family, other_user):
    return create_account(other_family.id, other_user.id, 'Itaú', AccountType.CHECKING, '2.000,00')


@pytest.fixture
def expense_cat(family):
    return get_categories(family.id, category_type='EXPENSE')[0]


# ── Criar e atualizar ─────────────────────────────────────────────────────────

class TestCriarConta:
    def test_cria_conta_a_pagar(self, family):
        bill = create_bill(family.id, 'Aluguel', BillType.PAYABLE, '1.200,00', NEXT_WEEK)
        assert bill.id is not None
        assert bill.amount_cents == 120000
        assert bill.type == BillType.PAYABLE
        assert bill.status == BillStatus.PENDING

    def test_cria_conta_a_receber(self, family):
        bill = create_bill(family.id, 'Salário', BillType.RECEIVABLE, '3.000,00', NEXT_WEEK)
        assert bill.type == BillType.RECEIVABLE
        assert bill.amount_cents == 300000

    def test_atualiza_conta(self, family):
        bill = create_bill(family.id, 'Aluguel', BillType.PAYABLE, '1.000,00', NEXT_WEEK)
        update_bill(bill, 'Aluguel atualizado', BillType.PAYABLE, '1.100,00', NEXT_WEEK)
        assert bill.description == 'Aluguel atualizado'
        assert bill.amount_cents == 110000


# ── Propriedades computadas ───────────────────────────────────────────────────

class TestPropriedades:
    def test_is_overdue_vencida(self, family):
        bill = create_bill(family.id, 'Velha', BillType.PAYABLE, '100,00', YESTERDAY)
        assert bill.is_overdue is True

    def test_is_overdue_futura(self, family):
        bill = create_bill(family.id, 'Futura', BillType.PAYABLE, '100,00', NEXT_WEEK)
        assert bill.is_overdue is False

    def test_days_until_due(self, family):
        bill = create_bill(family.id, 'Teste', BillType.PAYABLE, '100,00', NEXT_WEEK)
        assert bill.days_until_due == 7


# ── Pagar conta ───────────────────────────────────────────────────────────────

class TestPagarConta:
    def test_pagar_cria_transacao_despesa(self, family, user, account, expense_cat):
        bill = create_bill(
            family.id, 'Aluguel', BillType.PAYABLE, '1.200,00', NEXT_WEEK,
            account_id=account.id, category_id=expense_cat.id,
        )
        balance_before = account.current_balance_cents
        tx = pay_bill(bill, user.id, account.id, TODAY)
        assert tx is not None
        assert tx.type == 'EXPENSE'
        assert tx.amount_cents == -120000
        assert account.current_balance_cents == balance_before - 120000

    def test_pagar_altera_status_para_paid(self, family, user, account):
        bill = create_bill(family.id, 'Conta', BillType.PAYABLE, '500,00', NEXT_WEEK)
        pay_bill(bill, user.id, account.id, TODAY)
        assert bill.status == BillStatus.PAID

    def test_receber_cria_transacao_receita(self, family, user, account):
        bill = create_bill(family.id, 'Salário', BillType.RECEIVABLE, '3.000,00', NEXT_WEEK)
        balance_before = account.current_balance_cents
        tx = pay_bill(bill, user.id, account.id, TODAY)
        assert tx.type == 'INCOME'
        assert tx.amount_cents == 300000
        assert account.current_balance_cents == balance_before + 300000

    def test_receber_altera_status_para_received(self, family, user, account):
        bill = create_bill(family.id, 'Receita', BillType.RECEIVABLE, '1.000,00', NEXT_WEEK)
        pay_bill(bill, user.id, account.id, TODAY)
        assert bill.status == BillStatus.RECEIVED

    def test_pagamento_usa_data_fornecida(self, family, user, account):
        bill = create_bill(family.id, 'Conta', BillType.PAYABLE, '100,00', NEXT_WEEK)
        tx = pay_bill(bill, user.id, account.id, date(2026, 5, 3))
        assert tx.transaction_date == date(2026, 5, 3)


# ── Cancelar ─────────────────────────────────────────────────────────────────

class TestCancelarConta:
    def test_cancela_conta(self, family):
        bill = create_bill(family.id, 'Para cancelar', BillType.PAYABLE, '200,00', NEXT_WEEK)
        cancel_bill(bill)
        assert bill.status == BillStatus.CANCELED


# ── Isolamento ────────────────────────────────────────────────────────────────

class TestIsolamento:
    def test_nao_acessa_conta_de_outra_familia(self, family, other_family):
        bill = create_bill(family.id, 'Minha conta', BillType.PAYABLE, '100,00', NEXT_WEEK)
        assert get_bill(bill.id, other_family.id) is None

    def test_listagem_isolada(self, family, other_family):
        create_bill(family.id, 'Minha', BillType.PAYABLE, '100,00', NEXT_WEEK)
        create_bill(other_family.id, 'Outra', BillType.PAYABLE, '999,00', NEXT_WEEK)
        bills = get_bills(family.id)
        assert all(b.family_id == family.id for b in bills)
        assert len(bills) == 1


# ── Rotas ─────────────────────────────────────────────────────────────────────

class TestRotasBills:
    def _login(self, client, email):
        client.post('/auth/login', data={'email': email, 'password': 'senha1234'})

    def test_lista_exige_login(self, client):
        r = client.get('/bills', follow_redirects=False)
        assert r.status_code == 302

    def test_lista_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'eva@test.com')
        r = client.get('/bills')
        assert r.status_code == 200

    def test_criar_conta_via_post(self, app_ctx, client, family, user):
        self._login(client, 'eva@test.com')
        r = client.post('/bills/new', data={
            'description': 'Aluguel',
            'type': 'PAYABLE',
            'amount': '1.200,00',
            'due_date': '2026-05-10',
            'account_id': '0',
            'category_id': '0',
        }, follow_redirects=False)
        assert r.status_code == 302

    def test_conta_de_outra_familia_retorna_404(self, app_ctx, client, family, user, other_family, other_user):
        bill = create_bill(family.id, 'Minha', BillType.PAYABLE, '100,00', NEXT_WEEK)
        self._login(client, 'fabio@test.com')
        r = client.get(f'/bills/{bill.id}/edit')
        assert r.status_code == 404
