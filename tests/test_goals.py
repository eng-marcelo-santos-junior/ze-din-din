from datetime import date
import pytest

from app.auth.services import register_user
from app.families.services import create_family
from app.accounts.services import create_account
from app.models.account import AccountType
from app.models.goal import GoalStatus
from app.goals.services import (
    create_goal, update_goal, get_goal, get_goals,
    contribute_to_goal, cancel_goal,
)

TODAY = date(2026, 5, 1)
TARGET = date(2027, 5, 1)


@pytest.fixture
def user(app_ctx):
    return register_user('Gabi Nunes', 'gabi@test.com', 'senha1234')


@pytest.fixture
def other_user(app_ctx):
    return register_user('Hugo Prado', 'hugo@test.com', 'senha1234')


@pytest.fixture
def family(user):
    return create_family('Família Nunes', 'BRL', user.id)


@pytest.fixture
def other_family(other_user):
    return create_family('Família Prado', 'BRL', other_user.id)


@pytest.fixture
def account(family, user):
    return create_account(family.id, user.id, 'Poupança', AccountType.SAVINGS, '0')


# ── Criar meta ────────────────────────────────────────────────────────────────

class TestCriarMeta:
    def test_cria_meta(self, family):
        g = create_goal(family.id, 'Reserva de emergência', '10.000,00', TARGET)
        assert g.id is not None
        assert g.target_amount_cents == 1000000
        assert g.current_amount_cents == 0
        assert g.status == GoalStatus.ACTIVE
        assert g.target_date == TARGET

    def test_cria_meta_sem_data(self, family):
        g = create_goal(family.id, 'Viagem', '5.000,00')
        assert g.target_date is None
        assert g.status == GoalStatus.ACTIVE

    def test_atualiza_meta(self, family):
        g = create_goal(family.id, 'Carro', '30.000,00', TARGET)
        update_goal(g, 'Carro novo', '35.000,00', TARGET)
        assert g.name == 'Carro novo'
        assert g.target_amount_cents == 3500000


# ── Progresso e aporte ────────────────────────────────────────────────────────

class TestProgresso:
    def test_progress_pct_zero(self, family):
        g = create_goal(family.id, 'Meta', '10.000,00')
        assert g.progress_pct == 0

    def test_progress_pct_50(self, family):
        g = create_goal(family.id, 'Meta', '10.000,00')
        contribute_to_goal(g, '5.000,00')
        assert g.progress_pct == 50

    def test_progress_pct_100(self, family):
        g = create_goal(family.id, 'Meta', '1.000,00')
        contribute_to_goal(g, '1.000,00')
        assert g.progress_pct == 100

    def test_aporte_aumenta_valor(self, family):
        g = create_goal(family.id, 'Meta', '10.000,00')
        contribute_to_goal(g, '1.000,00')
        assert g.current_amount_cents == 100000

    def test_aporte_zero_ignorado(self, family):
        g = create_goal(family.id, 'Meta', '10.000,00')
        contribute_to_goal(g, '0')
        assert g.current_amount_cents == 0

    def test_multiplos_aportes(self, family):
        g = create_goal(family.id, 'Meta', '10.000,00')
        contribute_to_goal(g, '2.000,00')
        contribute_to_goal(g, '3.000,00')
        assert g.current_amount_cents == 500000


# ── Conclusão automática ──────────────────────────────────────────────────────

class TestConclusao:
    def test_conclui_ao_atingir_meta(self, family):
        g = create_goal(family.id, 'Meta', '1.000,00')
        contribute_to_goal(g, '1.000,00')
        assert g.status == GoalStatus.COMPLETED

    def test_conclui_ao_exceder_meta(self, family):
        g = create_goal(family.id, 'Meta', '1.000,00')
        contribute_to_goal(g, '1.500,00')
        assert g.status == GoalStatus.COMPLETED

    def test_nao_conclui_antes_da_meta(self, family):
        g = create_goal(family.id, 'Meta', '10.000,00')
        contribute_to_goal(g, '9.999,00')
        assert g.status == GoalStatus.ACTIVE


# ── Cancelar ─────────────────────────────────────────────────────────────────

class TestCancelar:
    def test_cancela_meta(self, family):
        g = create_goal(family.id, 'Meta', '5.000,00')
        cancel_goal(g)
        assert g.status == GoalStatus.CANCELED


# ── Aporte mensal sugerido ────────────────────────────────────────────────────

class TestAporteMensal:
    def test_retorna_zero_sem_data(self, family):
        g = create_goal(family.id, 'Sem data', '10.000,00')
        assert g.monthly_needed == 0

    def test_calcula_aporte(self, family):
        g = create_goal(family.id, 'Com data', '12.000,00', date(2027, 5, 1))
        # 12 months * R$ 1.000 = R$ 12.000
        assert g.monthly_needed == 100000

    def test_sem_restante(self, family):
        g = create_goal(family.id, 'Meta', '1.000,00', TARGET)
        contribute_to_goal(g, '1.000,00')
        assert g.monthly_needed == 0


# ── Isolamento ────────────────────────────────────────────────────────────────

class TestIsolamento:
    def test_nao_acessa_meta_de_outra_familia(self, family, other_family):
        g = create_goal(family.id, 'Minha meta', '10.000,00')
        assert get_goal(g.id, other_family.id) is None

    def test_listagem_isolada(self, family, other_family):
        create_goal(family.id, 'Minha', '10.000,00')
        create_goal(other_family.id, 'Outra', '20.000,00')
        goals = get_goals(family.id)
        assert all(g.family_id == family.id for g in goals)
        assert len(goals) == 1


# ── Rotas ─────────────────────────────────────────────────────────────────────

class TestRotasGoals:
    def _login(self, client, email):
        client.post('/auth/login', data={'email': email, 'password': 'senha1234'})

    def test_lista_exige_login(self, client):
        r = client.get('/goals', follow_redirects=False)
        assert r.status_code == 302

    def test_lista_retorna_200(self, app_ctx, client, family, user):
        self._login(client, 'gabi@test.com')
        r = client.get('/goals')
        assert r.status_code == 200

    def test_criar_meta_via_post(self, app_ctx, client, family, user):
        self._login(client, 'gabi@test.com')
        r = client.post('/goals/new', data={
            'name': 'Viagem',
            'target_amount': '5.000,00',
            'target_date': '',
            'account_id': '0',
        }, follow_redirects=False)
        assert r.status_code == 302

    def test_meta_de_outra_familia_retorna_404(self, app_ctx, client, family, user, other_family, other_user):
        goal = create_goal(family.id, 'Minha', '1.000,00')
        self._login(client, 'hugo@test.com')
        r = client.get(f'/goals/{goal.id}/edit')
        assert r.status_code == 404
