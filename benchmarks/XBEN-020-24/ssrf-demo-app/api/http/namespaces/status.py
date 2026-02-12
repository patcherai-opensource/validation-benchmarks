"""
Status and health check endpoints.
"""

from flask import Blueprint, jsonify

from config import Config

status_bp = Blueprint('status', __name__)


@status_bp.route('/')
def root():
    """Root endpoint - service info."""
    return jsonify({
        'status': 'ok',
        'service': 'mindsdb',
        'api': '/api',
    }), 200


@status_bp.route('/api/status')
def api_status():
    """API status endpoint."""
    return jsonify({
        'status': 'ok',
        'cloud': Config.CLOUD,
        'environment': 'production',
    }), 200


@status_bp.route('/ping')
def ping():
    """Health check endpoint."""
    return 'ok', 200
