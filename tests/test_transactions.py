from datetime import date
import pytest

from app.auth.services import register_user
from app.families.services import create_family
from app.accounts.services import create_account, get_account
from app.categories.services import get_categories
from app.transactions.services import (
    create_transaction, update_transaction, delete_transaction,
    duplicate_transaction, mark_as_paid, create_transfer,
    get_transaction, get_transactions, TransactionFilters,
)
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.account import AccountType
from app.extensions import db


TODAY = date(2026, 4, 30)


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def user(app_ctx):
    return register_user('Eva Santos', 'eva@test.com', 'senha1234')


@pytest.fixture
def other_user(app_ctx):
    return register_user('Felipe Ramos', 'felipe@test.com', 'senha1234')


@pytest.fixture
def family(user):
    return create_family('Família Santos', 'BRL', user.id)


@pytest.fixture
def other_family(other_user):
    return create_family('Família Ramos', 'BRL', other_user.id)


@pytest.fixture
def account(family, user):
    return create_account(family.id, user.id, 'Nubank', AccountType.CHECKING, '1.000,00')


@pytest.fixture
def account2(family, user):
    return create_account(family.id, user.id, 'Poupança', AccountType.SAVINGS, '500,00')


@pytest.fixture
def cat_expense(family):
    cats = get_categories(family.id, category_type='EXPENSE')
    return cats[0]


@pytest.fixture
def cat_income(family):
    cats = get_categories(family.id, category_type='INCOME')
    return cats[0]


def _make_income(family, user, account, amount='200,00', desc='Salário', tx_date=None):
    return create_transaction(
        family_id=family.id, user_id=user.id, account_id=account.id,
        tx_type=TransactionType.INCOME, description=desc,
        amount_str=amount, transaction_date=tx_date or TODAY,
        status=TransactionStatus.RECEIVED,
    )


def _make_expense(family, user, account, amount='150,00', desc='Mercado', tx_date=None):
    return create_transaction(
        family_id=family.id, user_id=user.id, account_id=account.id,
        tx_type=TransactionType.EXPENSE, description=desc,
        amount_str=amount, transaction_date=tx_date or TODAY,
        status=TransactionStatus.PAID,
    )


# ── Criação e saldo ──────────────────────────────────────────────────────────

class TestCreateTransaction:
    def test_receita_aumenta_saldo(self, family, user, account):
        balance_before = account.current_balance_cents
        _make_income(family, user, account, '200,00')
        assert account.current_balance_cents == balance_before + 20000

    def test_despesa_reduz_saldo(self, family, user, account):
        balance_before = account.current_balance_cents
        _make_expense(family, user, account, '150,00')
        assert account.current_balance_cents == balance_before - 15000

    def test_amount_cents_positivo_para_receita(self, family, user, account):
        tx = _make_income(family, user, account, '100,00')
        assert tx.amount_cents == 10000

    def test_amount_cents_negativo_para_despesa(self, family, user, account):
        tx = _make_expense(family, user, account, '100,00')
        assert tx.amount_cents == -10000

    def test_cancelada_nao_altera_saldo(self, family, user, account):
        balance_before = account.current_balance_cents
        create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Cancelada',
            amount_str='500,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED,
        )
        assert account.current_balance_cents == balance_before

    def test_transacao_pertence_a_familia(self, family, user, account):
        tx = _make_expense(family, user, account)
        assert tx.family_id == family.id

    def test_display_amount_positivo(self, family, user, account):
        tx = _make_expense(family, user, account, '300,00')
        assert tx.display_amount_cents == 30000


# ── Update ───────────────────────────────────────────────────────────────────

class TestUpdateTransaction:
    def test_editar_valor_recalcula_saldo(self, family, user, account):
        tx = _make_expense(family, user, account, '100,00')
        balance_after_create = account.current_balance_cents
        update_transaction(
            tx, account_id=account.id, tx_type=TransactionType.EXPENSE,
            description='Mercado', amount_str='200,00',
            transaction_date=TODAY, status=TransactionStatus.PAID,
        )
        assert account.current_balance_cents == balance_after_create - 10000

    def test_cancelar_transacao_reverte_saldo(self, family, user, account):
        tx = _make_expense(family, user, account, '100,00')
        balance_after = account.current_balance_cents
        update_transaction(
            tx, account_id=account.id, tx_type=TransactionType.EXPENSE,
            description=tx.description, amount_str='100,00',
            transaction_date=TODAY, status=TransactionStatus.CANCELED,
        )
        assert account.current_balance_cents == balance_after + 10000

    def test_alterar_tipo_recalcula_saldo(self, family, user, account):
        tx = _make_expense(family, user, account, '100,00')
        balance = account.current_balance_cents
        update_transaction(
            tx, account_id=account.id, tx_type=TransactionType.INCOME,
            description=tx.description, amount_str='100,00',
            transaction_date=TODAY, status=TransactionStatus.RECEIVED,
        )
        # Was -10000 (expense deducted), now +10000 (income added): delta = +20000
        assert account.current_balance_cents == balance + 20000


# ── Delete ───────────────────────────────────────────────────────────────────

class TestDeleteTransaction:
    def test_excluir_receita_reverte_saldo(self, family, user, account):
        tx = _make_income(family, user, account, '300,00')
        balance_after = account.current_balance_cents
        delete_transaction(tx)
        assert account.current_balance_cents == balance_after - 30000

    def test_excluir_despesa_reverte_saldo(self, family, user, account):
        tx = _make_expense(family, user, account, '200,00')
        balance_after = account.current_balance_cents
        delete_transaction(tx)
        assert account.current_balance_cents == balance_after + 20000

    def test_transacao_removida_do_banco(self, family, user, account):
        tx = _make_expense(family, user, account)
        tx_id = tx.id
        delete_transaction(tx)
        assert db.session.get(Transaction, tx_id) is None

    def test_excluir_cancelada_nao_altera_saldo(self, family, user, account):
        balance = account.current_balance_cents
        tx = create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='C',
            amount_str='100,00', transaction_date=TODAY,
            status=TransactionStatus.CANCELED,
        )
        delete_transaction(tx)
        assert account.current_balance_cents == balance


# ── Transferência ─────────────────────────────────────────────────────────────

class TestTransfer:
    def test_transferencia_movimenta_duas_contas(self, family, user, account, account2):
        bal1_before = account.current_balance_cents
        bal2_before = account2.current_balance_cents
        create_transfer(
            family_id=family.id, user_id=user.id,
            from_account_id=account.id, to_account_id=account2.id,
            amount_str='300,00', description='Transferência teste',
            transaction_date=TODAY,
        )
        assert account.current_balance_cents == bal1_before - 30000
        assert account2.current_balance_cents == bal2_before + 30000

    def test_transferencia_compartilha_group_id(self, family, user, account, account2):
        out_tx, in_tx = create_transfer(
            family_id=family.id, user_id=user.id,
            from_account_id=account.id, to_account_id=account2.id,
            amount_str='100,00', description='Transfer', transaction_date=TODAY,
        )
        assert out_tx.transfer_group_id is not None
        assert out_tx.transfer_group_id == in_tx.transfer_group_id

    def test_transferencia_is_transfer_property(self, family, user, account, account2):
        out_tx, in_tx = create_transfer(
            family_id=family.id, user_id=user.id,
            from_account_id=account.id, to_account_id=account2.id,
            amount_str='100,00', description='TF', transaction_date=TODAY,
        )
        assert out_tx.is_transfer is True
        assert in_tx.is_transfer is True


# ── Isolamento ────────────────────────────────────────────────────────────────

class TestIsolamento:
    def test_transacao_nao_acessivel_por_outra_familia(self, family, user, account, other_family):
        tx = _make_expense(family, user, account)
        found = get_transaction(tx.id, other_family.id)
        assert found is None

    def test_listagem_isolada_por_familia(self, family, user, account, other_family, other_user):
        _make_expense(family, user, account)
        other_account = create_account(other_family.id, other_user.id, 'Outro', AccountType.CHECKING, '0')
        create_transaction(
            family_id=other_family.id, user_id=other_user.id,
            account_id=other_account.id, tx_type=TransactionType.EXPENSE,
            description='Despesa outra família', amount_str='50,00', transaction_date=TODAY,
        )
        page = get_transactions(family.id)
        for tx in page.items:
            assert tx.family_id == family.id


# ── Duplicar / Marcar como pago ───────────────────────────────────────────────

class TestDuplicateAndMarkPaid:
    def test_duplicar_cria_nova_transacao(self, family, user, account):
        tx = _make_expense(family, user, account, '100,00')
        copy = duplicate_transaction(tx, date(2026, 5, 1))
        assert copy.id != tx.id
        assert copy.description == tx.description
        assert copy.status == TransactionStatus.PENDING

    def test_duplicar_afeta_saldo(self, family, user, account):
        tx = _make_expense(family, user, account, '100,00')
        bal = account.current_balance_cents
        duplicate_transaction(tx, TODAY)
        assert account.current_balance_cents == bal - 10000

    def test_marcar_pendente_como_pago(self, family, user, account):
        tx = create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.EXPENSE, description='Pendente',
            amount_str='50,00', transaction_date=TODAY,
            status=TransactionStatus.PENDING,
        )
        mark_as_paid(tx)
        assert tx.status == TransactionStatus.PAID

    def test_marcar_receita_pendente_como_recebida(self, family, user, account):
        tx = create_transaction(
            family_id=family.id, user_id=user.id, account_id=account.id,
            tx_type=TransactionType.INCOME, description='Receita pendente',
            amount_str='50,00', transaction_date=TODAY,
            status=TransactionStatus.PENDING,
        )
        mark_as_paid(tx)
        assert tx.status == TransactionStatus.RECEIVED


# ── Filtros ──────────────────────────────────────────────────────────────────

class TestFiltros:
    def test_filtro_por_tipo(self, family, user, account):
        _make_income(family, user, account)
        _make_expense(family, user, account)
        result = get_transactions(family.id, filters=TransactionFilters(type='INCOME'))
        assert all(tx.type == 'INCOME' for tx in result.items)

    def test_filtro_por_periodo(self, family, user, account):
        _make_expense(family, user, account, tx_date=date(2026, 1, 15))
        _make_expense(family, user, account, tx_date=date(2026, 3, 10))
        filters = TransactionFilters(
            start_date=date(2026, 3, 1), end_date=date(2026, 3, 31)
        )
        result = get_transactions(family.id, filters=filters)
        assert all(tx.transaction_date.month == 3 for tx in result.items)

    def test_filtro_por_descricao(self, family, user, account):
        _make_expense(family, user, account, desc='Supermercado Pão de Açúcar')
        _make_expense(family, user, account, desc='Farmácia')
        result = get_transactions(family.id, filters=TransactionFilters(search='Supermercado'))
        assert all('Supermercado' in tx.description for tx in result.items)

    def test_filtro_por_conta(self, family, user, account, account2):
        _make_expense(family, user, account)
        _make_expense(family, user, account2)
        result = get_transactions(family.id, filters=TransactionFilters(account_id=account.id))
        assert all(tx.account_id == account.id for tx in result.items)


# ── Rotas ────────────────────────────────────────────────────────────────────

class TestRotasTransactions:
    def _login(self, client, email, password='senha1234'):
        client.post('/auth/login', data={'email': email, 'password': password})

    def test_lista_exige_login(self, client):
        r = client.get('/transactions', follow_redirects=False)
        assert r.status_code == 302
        assert '/auth/login' in r.headers['Location']

    def test_lista_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'eva@test.com')
        r = client.get('/transactions')
        assert r.status_code == 200

    def test_criar_despesa_via_post(self, app_ctx, client, family, user, account):
        self._login(client, 'eva@test.com')
        r = client.post('/transactions/new', data={
            'type': 'EXPENSE',
            'description': 'Padaria',
            'amount': '25,00',
            'transaction_date': '2026-04-30',
            'account_id': str(account.id),
            'category_id': '0',
            'status': 'PAID',
            'payment_method': '',
            'notes': '',
        }, follow_redirects=False)
        assert r.status_code == 302
        assert '/transactions' in r.headers['Location']

    def test_transacao_de_outra_familia_retorna_404(self, app_ctx, client, family, user, account, other_family, other_user):
        tx = _make_expense(family, user, account)
        self._login(client, 'felipe@test.com')
        r = client.get(f'/transactions/{tx.id}/edit')
        assert r.status_code == 404

    def test_pagina_transferencia_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'eva@test.com')
        r = client.get('/transactions/transfer')
        assert r.status_code == 200
