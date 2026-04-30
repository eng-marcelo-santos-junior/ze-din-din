import pytest
from flask import g
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope='session')
def app():
    """Cria app e empurra o contexto uma única vez para toda a sessão de testes."""
    _app = create_app('testing')
    ctx = _app.app_context()
    ctx.push()
    _db.create_all()
    yield _app
    _db.drop_all()
    _db.session.remove()
    ctx.pop()


@pytest.fixture(autouse=True)
def clean_tables():
    """
    Após cada teste:
    1. Limpa o cache de usuário do Flask-Login (g._login_user persiste no
       contexto de sessão e causaria ObjectDeletedError no próximo teste).
    2. Remove a session SQLAlchemy.
    3. Apaga todas as linhas das tabelas.
    """
    yield
    if hasattr(g, '_login_user'):
        del g._login_user
    _db.session.remove()
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def app_ctx(app):
    """Fixture para testes de serviços que acessam o BD diretamente."""
    yield app
