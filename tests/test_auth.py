import pytest
from app.auth.services import register_user, authenticate, get_user_by_email
from app.models.user import User
from app.extensions import db


class TestRegisterUser:
    def test_cria_usuario_com_dados_corretos(self, app_ctx):
        user = register_user('João Silva', 'joao@test.com', 'senha1234')
        assert user.id is not None
        assert user.name == 'João Silva'
        assert user.email == 'joao@test.com'
        assert user.is_active is True

    def test_email_convertido_para_minusculo(self, app_ctx):
        user = register_user('Maria', 'MARIA@TEST.COM', 'senha1234')
        assert user.email == 'maria@test.com'

    def test_senha_nao_salva_em_texto_puro(self, app_ctx):
        user = register_user('Pedro', 'pedro@test.com', 'senha1234')
        assert user.password_hash != 'senha1234'

    def test_senha_valida_com_check_password(self, app_ctx):
        user = register_user('Ana', 'ana@test.com', 'senha1234')
        assert user.check_password('senha1234') is True
        assert user.check_password('senhaerrada') is False

    def test_usuario_persistido_no_banco(self, app_ctx):
        register_user('Carlos', 'carlos@test.com', 'senha1234')
        user = db.session.scalar(db.select(User).where(User.email == 'carlos@test.com'))
        assert user is not None
        assert user.name == 'Carlos'


class TestAuthenticate:
    def test_credenciais_validas_retorna_usuario(self, app_ctx):
        register_user('Laura', 'laura@test.com', 'senha1234')
        user = authenticate('laura@test.com', 'senha1234')
        assert user is not None
        assert user.email == 'laura@test.com'

    def test_senha_errada_retorna_none(self, app_ctx):
        register_user('Bruno', 'bruno@test.com', 'senha1234')
        user = authenticate('bruno@test.com', 'senhaerrada')
        assert user is None

    def test_email_inexistente_retorna_none(self, app_ctx):
        user = authenticate('naoexiste@test.com', 'qualquer')
        assert user is None

    def test_email_case_insensitive(self, app_ctx):
        register_user('Rita', 'rita@test.com', 'senha1234')
        user = authenticate('RITA@TEST.COM', 'senha1234')
        assert user is not None

    def test_usuario_inativo_nao_autentica(self, app_ctx):
        user = register_user('Inativo', 'inativo@test.com', 'senha1234')
        user.is_active = False
        db.session.commit()
        result = authenticate('inativo@test.com', 'senha1234')
        assert result is None


class TestRotasAuth:
    def test_pagina_login_retorna_200(self, client):
        response = client.get('/auth/login')
        assert response.status_code == 200

    def test_pagina_register_retorna_200(self, client):
        response = client.get('/auth/register')
        assert response.status_code == 200

    def test_dashboard_redireciona_sem_login(self, client):
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']

    def test_cadastro_via_post_redireciona_para_dashboard(self, client):
        response = client.post('/auth/register', data={
            'name': 'Novo Usuario',
            'email': 'novo@test.com',
            'password': 'senha1234',
            'confirm_password': 'senha1234',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/dashboard' in response.headers['Location']

    def test_login_valido_redireciona_para_dashboard(self, app_ctx, client):
        register_user('Login Test', 'login@test.com', 'senha1234')
        response = client.post('/auth/login', data={
            'email': 'login@test.com',
            'password': 'senha1234',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/dashboard' in response.headers['Location']

    def test_login_invalido_permanece_na_pagina(self, client):
        response = client.post('/auth/login', data={
            'email': 'errado@test.com',
            'password': 'senhaerrada',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'E-mail ou senha incorretos' in response.data

    def test_logout_redireciona_para_login(self, app_ctx, client):
        register_user('Logout Test', 'logout@test.com', 'senha1234')
        client.post('/auth/login', data={
            'email': 'logout@test.com',
            'password': 'senha1234',
        })
        response = client.get('/auth/logout', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']
