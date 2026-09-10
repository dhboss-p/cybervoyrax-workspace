from flask import Flask

from .config import Config
from .extensions import db
from .errors import register_error_handlers
from .logging_setup import register_request_logging
from .csrf import register_csrf

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from .routes.main import main_bp
    from .routes.health import health_bp
    from .routes.api_system import api_system_bp
    from .routes.ui import ui_bp
    from .routes.account import account_bp
    from .routes.directory import directory_bp
    from .routes.projects import projects_bp
    from .routes.documents import documents_bp
    from .routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(api_system_bp)
    app.register_blueprint(ui_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(directory_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(admin_bp)

    register_csrf(app)
    register_error_handlers(app)
    register_request_logging(app)
    return app
