import os
from datetime import timedelta
from sqlalchemy.pool import NullPool


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://zedindin:zedindin@localhost:5432/zedindin_dev',
    )
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL',
        'postgresql://zedindin:zedindin@localhost:5432/zedindin_test',
    )


class ProductionConfig(Config):
    DEBUG = False
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Neon e Heroku retornam "postgres://" — SQLAlchemy exige "postgresql://"
    _raw_url = os.environ.get('DATABASE_URL', '')
    SQLALCHEMY_DATABASE_URI = (
        _raw_url.replace('postgres://', 'postgresql://', 1) if _raw_url else None
    )

    # NullPool obrigatório em serverless: sem conexões persistentes entre invocações
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': NullPool,
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
