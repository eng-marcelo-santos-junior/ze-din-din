import pytest
from app.auth.services import register_user
from app.families.services import create_family
from app.categories.services import (
    create_category, get_category, get_categories,
    update_category, archive_category, seed_default_categories,
)
from app.models.category import Category, CategoryType
from app.extensions import db


@pytest.fixture
def user(app_ctx):
    return register_user('Carol', 'carol@test.com', 'senha1234')


@pytest.fixture
def other_user(app_ctx):
    return register_user('Davi', 'davi@test.com', 'senha1234')


@pytest.fixture
def family(user):
    return create_family('Família Carol', 'BRL', user.id)


@pytest.fixture
def other_family(other_user):
    return create_family('Família Davi', 'BRL', other_user.id)


@pytest.fixture
def expense_cat(family):
    return create_category(family.id, 'Alimentação', CategoryType.EXPENSE, '#fd7e14', 'bi-basket')


@pytest.fixture
def income_cat(family):
    return create_category(family.id, 'Salário', CategoryType.INCOME, '#198754', 'bi-briefcase')


class TestSeedDefaultCategories:
    def test_cria_categorias_padrao_ao_criar_familia(self, family):
        cats = get_categories(family.id)
        names = [c.name for c in cats]
        assert 'Salário' in names
        assert 'Alimentação' in names
        assert 'Moradia' in names

    def test_categorias_padrao_marcadas_como_is_default(self, family):
        cats = get_categories(family.id)
        assert all(c.is_default for c in cats)

    def test_criadas_receitas_e_despesas(self, family):
        income = get_categories(family.id, category_type=CategoryType.INCOME)
        expense = get_categories(family.id, category_type=CategoryType.EXPENSE)
        assert len(income) == 5
        assert len(expense) == 14

    def test_categorias_isoladas_por_familia(self, family, other_family):
        cats_family = get_categories(family.id)
        cats_other = get_categories(other_family.id)
        ids_family = {c.id for c in cats_family}
        ids_other = {c.id for c in cats_other}
        assert ids_family.isdisjoint(ids_other)


class TestCreateCategory:
    def test_cria_categoria_corretamente(self, family):
        cat = create_category(family.id, 'Transporte', CategoryType.EXPENSE)
        assert cat.id is not None
        assert cat.name == 'Transporte'
        assert cat.type == CategoryType.EXPENSE
        assert cat.family_id == family.id

    def test_nome_com_espacos_e_limpo(self, family):
        cat = create_category(family.id, '  Lazer  ', CategoryType.EXPENSE)
        assert cat.name == 'Lazer'

    def test_cria_subcategoria(self, family, expense_cat):
        sub = create_category(
            family.id, 'Restaurantes', CategoryType.EXPENSE,
            parent_id=expense_cat.id,
        )
        assert sub.parent_id == expense_cat.id


class TestGetCategory:
    def test_retorna_categoria_da_familia(self, expense_cat, family):
        found = get_category(expense_cat.id, family.id)
        assert found is not None

    def test_nao_retorna_categoria_de_outra_familia(self, expense_cat, other_family):
        found = get_category(expense_cat.id, other_family.id)
        assert found is None

    def test_retorna_none_para_id_inexistente(self, family):
        assert get_category(99999, family.id) is None


class TestUpdateCategory:
    def test_atualiza_nome(self, expense_cat):
        update_category(expense_cat, 'Comida', CategoryType.EXPENSE, '#fd7e14', 'bi-basket')
        assert expense_cat.name == 'Comida'

    def test_atualiza_tipo(self, expense_cat):
        update_category(expense_cat, expense_cat.name, CategoryType.INCOME, expense_cat.color, expense_cat.icon)
        assert expense_cat.type == CategoryType.INCOME


class TestArchiveCategory:
    def test_arquiva_categoria(self, expense_cat):
        archive_category(expense_cat)
        assert expense_cat.is_active is False

    def test_categoria_arquivada_nao_aparece_na_listagem(self, expense_cat, family):
        archive_category(expense_cat)
        cats = get_categories(family.id, active_only=True)
        assert expense_cat not in cats


class TestRotasCategories:
    def _login(self, client, email, password='senha1234'):
        client.post('/auth/login', data={'email': email, 'password': password})

    def test_lista_exige_login(self, client):
        r = client.get('/categories', follow_redirects=False)
        assert r.status_code == 302
        assert '/auth/login' in r.headers['Location']

    def test_lista_retorna_200_com_familia(self, app_ctx, client, family, user):
        self._login(client, 'carol@test.com')
        r = client.get('/categories')
        assert r.status_code == 200
        assert 'Salário'.encode() in r.data

    def test_criar_categoria_via_post(self, app_ctx, client, family, user):
        self._login(client, 'carol@test.com')
        r = client.post('/categories/new', data={
            'name': 'Streaming',
            'type': 'EXPENSE',
            'parent_id': '0',
            'color': '#6f42c1',
            'icon': 'bi-play-circle',
        }, follow_redirects=False)
        assert r.status_code == 302
        assert '/categories' in r.headers['Location']

    def test_editar_categoria_de_outra_familia_retorna_404(self, app_ctx, client, expense_cat, other_family, other_user):
        self._login(client, 'davi@test.com')
        r = client.get(f'/categories/{expense_cat.id}/edit')
        assert r.status_code == 404
