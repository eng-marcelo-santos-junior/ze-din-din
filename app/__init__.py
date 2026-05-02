import os
import sys
from datetime import datetime
from flask import Flask
from .config import config
from .extensions import db, migrate, login_manager, csrf


def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Class-level os.environ.get() in ProductionConfig evaluates at import time,
    # before Vercel injects env vars. Re-read at runtime using multiple known
    # Neon/Vercel variable names as fallbacks.
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        _candidates = (
            'DATABASE_URL',
            'POSTGRES_URL',
            'DATABASE_URL_UNPOOLED',
            'POSTGRES_URL_NON_POOLING',
            'DATABASE_PRIVATE_URL',
        )
        for _key in _candidates:
            _raw = os.environ.get(_key, '')
            if _raw:
                app.config['SQLALCHEMY_DATABASE_URI'] = _raw.replace(
                    'postgres://', 'postgresql://', 1
                )
                print(f"[create_app] SQLALCHEMY_DATABASE_URI set from {_key}", file=sys.stderr)
                break
        else:
            print(f"[create_app] No DB URL found. Checked: {_candidates}", file=sys.stderr)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from . import models  # noqa

    from .utils.money import format_cents_to_money
    app.jinja_env.filters['money'] = format_cents_to_money
    app.jinja_env.filters['abs'] = abs

    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        current_family = None
        if current_user.is_authenticated:
            from .utils.families import get_current_family
            current_family = get_current_family(current_user)
        return {'now': datetime.utcnow(), 'current_family': current_family}

    from .main import main_bp
    app.register_blueprint(main_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from .families import families_bp
    app.register_blueprint(families_bp)

    from .accounts import accounts_bp
    app.register_blueprint(accounts_bp)

    from .categories import categories_bp
    app.register_blueprint(categories_bp)

    from .transactions import transactions_bp
    app.register_blueprint(transactions_bp)

    from .budgets import budgets_bp
    app.register_blueprint(budgets_bp)

    from .bills import bills_bp
    app.register_blueprint(bills_bp)

    from .goals import goals_bp
    app.register_blueprint(goals_bp)

    from .reports import reports_bp
    app.register_blueprint(reports_bp)

    return app
