"""
spacy-llm Prompt Service - REST API for NLP prompt generation and rendering.

Provides a web interface for generating and previewing prompts using
configurable Jinja2 templates for various NLP tasks (NER, sentiment,
text classification, summarization, raw).
"""

import logging
from flask import Flask

from config import Config

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("prompt_service")


def create_app():
    app = Flask(__name__, template_folder="web/templates", static_folder="web/static")
    app.config.from_object(Config)

    from routes.api import api_bp
    from routes.ui import ui_bp
    from routes.health import health_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(ui_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        return {"error": "Internal server error"}, 500

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=8000)
