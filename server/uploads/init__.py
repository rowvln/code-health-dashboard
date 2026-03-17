from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes.analysis import analysis_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    app.register_blueprint(analysis_bp, url_prefix="/api")

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app
