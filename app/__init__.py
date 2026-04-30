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

    # Importa models para registrar no SQLAlchemy/Alembic e ativar user_loader
    from . import models  # noqa

    @app.context_processor
    def inject_globals():
        return {'now': datetime.utcnow()}

    from .main import main_bp
    app.register_blueprint(main_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    return app
