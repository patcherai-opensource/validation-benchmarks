"""
MathEngine Server - Scientific computation service
Provides a safe expression evaluation API for mathematical computations.
"""
import os
import logging
from flask import Flask

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=None)

    app.config['SECRET_KEY'] = os.urandom(32).hex()
    app.config['MAX_CONTENT_LENGTH'] = 64 * 1024

    from .routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(e):
        return {'error': 'Internal server error'}, 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080)
