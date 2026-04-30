from datetime import datetime
from flask import Flask
from .config import config
from .extensions import db, migrate, login_manager, csrf


def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from . import models  # noqa

    from .utils.money import format_cents_to_money
    app.jinja_env.filters['money'] = format_cents_to_money

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

    return app
