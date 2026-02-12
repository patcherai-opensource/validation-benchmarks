import os
import logging
from flask import Flask

def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    app.config['SECRET_KEY'] = os.urandom(32).hex()
    app.config['MAX_CONTENT_LENGTH'] = 64 * 1024
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    logging.basicConfig(level=logging.WARNING)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {'error': 'Internal server error'}, 500

    return app
