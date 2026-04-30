import pytest
from app.auth.services import register_user
from app.families.services import create_family, get_members, get_user_membership
from app.models.family import Family, FamilyMember, FamilyRole, FamilyMemberStatus
from app.extensions import db


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def user(app_ctx):
    return register_user('Alice Souza', 'alice@test.com', 'senha1234')


@pytest.fixture
def other_user(app_ctx):
    return register_user('Bruno Lima', 'bruno@test.com', 'senha1234')


@pytest.fixture
def family_with_owner(user):
    return create_family('Família Souza', 'BRL', user.id)


# ── Testes de serviço ──────────────────────────────────────────────────────────

class TestCreateFamily:
    def test_cria_familia_com_dados_corretos(self, user):
        family = create_family('Família Silva', 'BRL', user.id)
        assert family.id is not None
        assert family.name == 'Família Silva'
        assert family.currency == 'BRL'
        assert family.created_by == user.id

    def test_criador_vira_owner(self, user):
        family = create_family('Família Testes', 'BRL', user.id)
        membership = get_user_membership(user.id, family.id)
        assert membership is not None
        assert membership.role == FamilyRole.OWNER
        assert membership.status == FamilyMemberStatus.ACTIVE

    def test_familia_persistida_no_banco(self, user):
        family = create_family('Família DB', 'USD', user.id)
        found = db.session.get(Family, family.id)
        assert found is not None
        assert found.name == 'Família DB'
        assert found.currency == 'USD'

    def test_membership_persistida_no_banco(self, user):
        family = create_family('Família Mem', 'BRL', user.id)
        members = get_members(family.id)
        assert len(members) == 1
        assert members[0].user_id == user.id

    def test_nome_com_espacos_extras_e_limpo(self, user):
        family = create_family('  Família Espaço  ', 'BRL', user.id)
        assert family.name == 'Família Espaço'


class TestGetCurrentFamily:
    def test_usuario_com_familia_retorna_familia(self, user, family_with_owner):
        from app.utils.families import get_current_family
        family = get_current_family(user)
        assert family is not None
        assert family.id == family_with_owner.id

    def test_usuario_sem_familia_retorna_none(self, other_user):
        from app.utils.families import get_current_family
        family = get_current_family(other_user)
        assert family is None

    def test_usuario_nao_autenticado_retorna_none(self):
        from app.utils.families import get_current_family
        from unittest.mock import MagicMock
        anon = MagicMock()
        anon.is_authenticated = False
        assert get_current_family(anon) is None


class TestUserHasAccessToFamily:
    def test_membro_tem_acesso(self, user, family_with_owner):
        from app.utils.families import user_has_access_to_family
        assert user_has_access_to_family(user.id, family_with_owner.id) is True

    def test_nao_membro_nao_tem_acesso(self, other_user, family_with_owner):
        from app.utils.families import user_has_access_to_family
        assert user_has_access_to_family(other_user.id, family_with_owner.id) is False

    def test_membro_removido_nao_tem_acesso(self, user, family_with_owner):
        from app.utils.families import user_has_access_to_family
        membership = get_user_membership(user.id, family_with_owner.id)
        membership.status = FamilyMemberStatus.REMOVED
        db.session.commit()
        assert user_has_access_to_family(user.id, family_with_owner.id) is False


# ── Testes de rota ─────────────────────────────────────────────────────────────

class TestRotasFamilia:
    def _login(self, client, email, password='senha1234'):
        client.post('/auth/login', data={'email': email, 'password': password})

    def test_pagina_nova_familia_retorna_200(self, app_ctx, client):
        register_user('Visitante', 'visitante@test.com', 'senha1234')
        self._login(client, 'visitante@test.com')
        response = client.get('/families/new')
        assert response.status_code == 200

    def test_usuario_nao_autenticado_redireciona_para_login(self, client):
        response = client.get('/families/new', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']

    def test_criar_familia_via_post_redireciona_para_dashboard(self, app_ctx, client):
        register_user('Criador', 'criador@test.com', 'senha1234')
        self._login(client, 'criador@test.com')
        response = client.post('/families/new', data={
            'name': 'Família Teste',
            'currency': 'BRL',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/dashboard' in response.headers['Location']

    def test_usuario_com_familia_redireciona_de_families_new_para_dashboard(self, app_ctx, client, user, family_with_owner):
        self._login(client, 'alice@test.com')
        response = client.get('/families/new', follow_redirects=False)
        assert response.status_code == 302
        assert '/dashboard' in response.headers['Location']

    def test_pagina_members_exige_familia_ativa(self, app_ctx, client):
        register_user('Sem Fam', 'semfam@test.com', 'senha1234')
        self._login(client, 'semfam@test.com')
        response = client.get('/families/members', follow_redirects=False)
        assert response.status_code == 302
        assert '/families/new' in response.headers['Location']

    def test_pagina_members_retorna_200_com_familia(self, app_ctx, client, user, family_with_owner):
        self._login(client, 'alice@test.com')
        response = client.get('/families/members')
        assert response.status_code == 200
        assert 'Souza'.encode() in response.data

    def test_usuario_nao_acessa_familia_alheia(self, app_ctx, client, user, family_with_owner, other_user):
        create_family('Família Lima', 'BRL', other_user.id)
        self._login(client, 'alice@test.com')
        response = client.get('/families/members')
        assert response.status_code == 200
        assert 'Souza'.encode() in response.data
        assert 'Lima'.encode() not in response.data

    def test_settings_exige_familia_ativa(self, app_ctx, client):
        register_user('Sem Fam2', 'semfam2@test.com', 'senha1234')
        self._login(client, 'semfam2@test.com')
        response = client.get('/families/settings', follow_redirects=False)
        assert response.status_code == 302
        assert '/families/new' in response.headers['Location']

    def test_dashboard_com_familia_retorna_200(self, app_ctx, client, user, family_with_owner):
        self._login(client, 'alice@test.com')
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert 'Souza'.encode() in response.data
