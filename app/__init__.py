# app/__init__.py
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Load default config
    app.config.from_object("app.config")

    # Load instance config (for secrets, etc.)
    app.config.from_pyfile('config.py', silent=True)

    # Enable CORS
    CORS(app)

    # Register Blueprints (routes)
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
