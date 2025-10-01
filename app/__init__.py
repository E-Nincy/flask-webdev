import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
from flask_moment import Moment

# Load environment variables from .env
load_dotenv()

# --- Extensions ---
db = SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
moment = Moment()

def create_app(config_name='default'):
    """Application Factory - creates and configures the Flask app"""
    app = Flask(__name__)

    # --- Load config from config.py ---
    from .config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # --- Initialize extensions ---
    db.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.register'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    mail.init_app(app)
    moment.init_app(app)

    # --- Register blueprints ---
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # --- Import models and inject context ---
    from .models import Permission, ReleaseType  # 👈 ahora aquí
    @app.context_processor
    def inject_permissions_and_releases():
        return dict(Permission=Permission, ReleaseType=ReleaseType)

    # --- Create database tables if they don't exist ---
    with app.app_context():
        db.create_all()

    return app
