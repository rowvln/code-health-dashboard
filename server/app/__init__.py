from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes.analysis import analysis_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

    app.register_blueprint(analysis_bp, url_prefix="/api")

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app
