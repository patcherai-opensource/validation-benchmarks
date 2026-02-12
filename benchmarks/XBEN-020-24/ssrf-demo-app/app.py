"""
MindsDB HTTP API Application Factory.
"""

import os
import logging
from flask import Flask

from config import Config


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure logging
    logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))

    # Suppress default Flask/Werkzeug banners
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)

    # Ensure storage directories exist
    os.makedirs(Config.FILES_DIR, exist_ok=True)
    os.makedirs(Config.TMP_DIR, exist_ok=True)

    # Register blueprints
    from api.http.namespaces.file import file_bp
    from api.http.namespaces.models import models_bp
    from api.http.namespaces.databases import databases_bp
    from api.http.namespaces.status import status_bp

    app.register_blueprint(status_bp)
    app.register_blueprint(file_bp, url_prefix='/api')
    app.register_blueprint(models_bp, url_prefix='/api')
    app.register_blueprint(databases_bp, url_prefix='/api')

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(e):
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(400)
    def bad_request(e):
        return {'error': 'Bad request'}, 400

    return app
