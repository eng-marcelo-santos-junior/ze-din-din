import pytest
from app.auth.services import register_user
from app.families.services import create_family
from app.accounts.services import (
    create_account, get_account, get_accounts,
    update_account, archive_account, get_total_balance_cents,
)
from app.models.account import Account, AccountType
from app.extensions import db


@pytest.fixture
def user(app_ctx):
    return register_user('Alice', 'alice@test.com', 'senha1234')


@pytest.fixture
def other_user(app_ctx):
    return register_user('Bruno', 'bruno@test.com', 'senha1234')


@pytest.fixture
def family(user):
    return create_family('Família Alice', 'BRL', user.id)


@pytest.fixture
def other_family(other_user):
    return create_family('Família Bruno', 'BRL', other_user.id)


@pytest.fixture
def account(family, user):
    return create_account(
        family_id=family.id,
        owner_user_id=user.id,
        name='Nubank',
        account_type=AccountType.CHECKING,
        initial_balance='1.500,00',
    )


class TestCreateAccount:
    def test_cria_conta_com_dados_corretos(self, family, user):
        acc = create_account(
            family_id=family.id,
            owner_user_id=user.id,
            name='Bradesco',
            account_type=AccountType.SAVINGS,
            initial_balance='2.000,00',
            institution='Bradesco',
        )
        assert acc.id is not None
        assert acc.name == 'Bradesco'
        assert acc.type == AccountType.SAVINGS
        assert acc.institution == 'Bradesco'

    def test_saldo_convertido_para_centavos(self, family, user):
        acc = create_account(
            family_id=family.id,
            owner_user_id=user.id,
            name='Caixa',
            account_type=AccountType.CHECKING,
            initial_balance='1.500,50',
        )
        assert acc.initial_balance_cents == 150050
        assert acc.current_balance_cents == 150050

    def test_saldo_initial_e_current_iguais_na_criacao(self, family, user):
        acc = create_account(
            family_id=family.id,
            owner_user_id=user.id,
            name='Poupança',
            account_type=AccountType.SAVINGS,
            initial_balance='500,00',
        )
        assert acc.initial_balance_cents == acc.current_balance_cents

    def test_saldo_zero_por_padrao(self, family, user):
        acc = create_account(
            family_id=family.id,
            owner_user_id=user.id,
            name='Carteira',
            account_type=AccountType.CASH,
            initial_balance='',
        )
        assert acc.initial_balance_cents == 0
        assert acc.current_balance_cents == 0

    def test_icone_definido_pelo_tipo(self, family, user):
        acc = create_account(
            family_id=family.id,
            owner_user_id=user.id,
            name='Crédito',
            account_type=AccountType.CREDIT_CARD,
            initial_balance='0',
        )
        assert acc.icon == 'bi-credit-card'

    def test_conta_pertence_a_familia(self, family, user):
        acc = create_account(
            family_id=family.id,
            owner_user_id=user.id,
            name='Teste',
            account_type=AccountType.CHECKING,
            initial_balance='0',
        )
        assert acc.family_id == family.id


class TestGetAccount:
    def test_retorna_conta_da_familia(self, account, family):
        found = get_account(account.id, family.id)
        assert found is not None
        assert found.id == account.id

    def test_nao_retorna_conta_de_outra_familia(self, account, other_family):
        found = get_account(account.id, other_family.id)
        assert found is None

    def test_retorna_none_para_id_inexistente(self, family):
        assert get_account(99999, family.id) is None


class TestUpdateAccount:
    def test_atualiza_nome(self, account):
        update_account(
            account,
            name='Nubank Atualizado',
            account_type=account.type,
            initial_balance='1.500,00',
            currency=account.currency,
            institution=account.institution or '',
            color=account.color,
            visibility=account.visibility,
        )
        assert account.name == 'Nubank Atualizado'

    def test_atualiza_saldo_e_ajusta_current(self, account):
        update_account(
            account,
            name=account.name,
            account_type=account.type,
            initial_balance='2.000,00',
            currency=account.currency,
            institution=account.institution or '',
            color=account.color,
            visibility=account.visibility,
        )
        assert account.initial_balance_cents == 200000
        assert account.current_balance_cents == 200000


class TestArchiveAccount:
    def test_arquiva_conta(self, account):
        archive_account(account)
        assert account.is_active is False

    def test_conta_arquivada_nao_aparece_na_listagem(self, account, family):
        archive_account(account)
        accounts = get_accounts(family.id, active_only=True)
        assert account not in accounts


class TestGetAccounts:
    def test_lista_contas_da_familia(self, account, family):
        accounts = get_accounts(family.id)
        assert account in accounts

    def test_nao_lista_contas_de_outra_familia(self, account, other_family):
        accounts = get_accounts(other_family.id)
        # other_family tem no máximo as contas dela própria
        for a in accounts:
            assert a.family_id == other_family.id

    def test_total_saldo_familia(self, family, user):
        create_account(family.id, user.id, 'C1', AccountType.CHECKING, '1.000,00')
        create_account(family.id, user.id, 'C2', AccountType.SAVINGS, '2.000,00')
        total = get_total_balance_cents(family.id)
        assert total == 300000


class TestRotasAccounts:
    def _login(self, client, email, password='senha1234'):
        client.post('/auth/login', data={'email': email, 'password': password})

    def test_lista_exige_login(self, client):
        r = client.get('/accounts', follow_redirects=False)
        assert r.status_code == 302
        assert '/auth/login' in r.headers['Location']

    def test_lista_exige_familia(self, app_ctx, client):
        register_user('Sem Fam', 'semfam@acc.com', 'senha1234')
        self._login(client, 'semfam@acc.com')
        r = client.get('/accounts', follow_redirects=False)
        assert r.status_code == 302
        assert '/families/new' in r.headers['Location']

    def test_lista_retorna_200_com_familia(self, app_ctx, client, family, user):
        self._login(client, 'alice@test.com')
        r = client.get('/accounts')
        assert r.status_code == 200

    def test_criar_conta_via_post(self, app_ctx, client, family, user):
        self._login(client, 'alice@test.com')
        r = client.post('/accounts/new', data={
            'name': 'Conta Teste',
            'type': 'CHECKING',
            'institution': 'Banco X',
            'initial_balance': '500,00',
            'currency': 'BRL',
            'color': '#0d6efd',
            'visibility': 'SHARED',
        }, follow_redirects=False)
        assert r.status_code == 302
        assert '/accounts' in r.headers['Location']

    def test_editar_conta_de_outra_familia_retorna_404(self, app_ctx, client, account, other_family, other_user):
        self._login(client, 'bruno@test.com')
        r = client.get(f'/accounts/{account.id}/edit')
        assert r.status_code == 404
