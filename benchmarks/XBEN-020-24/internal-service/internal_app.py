"""
Internal administration service.
Provides system configuration and management endpoints.
Only accessible from the internal network.
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

_secret_config_path = '/app/.secret_config'
_cached_config = None


def _read_config():
    global _cached_config
    if _cached_config is not None:
        return _cached_config
    try:
        with open(_secret_config_path, 'r') as f:
            _cached_config = f.read().strip()
        return _cached_config
    except FileNotFoundError:
        return None


@app.route('/')
def index():
    """Internal service root."""
    admin_token = _read_config()
    return jsonify({
        'service': 'mindsdb-internal-admin',
        'status': 'running',
        'admin_token': admin_token,
        'endpoints': ['/config', '/health', '/metrics'],
    }), 200


@app.route('/config')
def config_endpoint():
    """Internal configuration endpoint with sensitive data."""
    admin_token = _read_config()
    return jsonify({
        'database_host': '10.0.0.5',
        'database_port': 3306,
        'database_name': 'mindsdb_prod',
        'admin_token': admin_token,
        'cache_backend': 'redis://10.0.0.10:6379',
        'storage_backend': 's3://mindsdb-data-prod',
        'log_level': 'INFO',
        'max_workers': 8,
    }), 200


@app.route('/metrics')
def metrics():
    """Internal metrics endpoint."""
    return jsonify({
        'requests_total': 15234,
        'active_models': 12,
        'cache_hit_rate': 0.87,
        'uptime_seconds': 432100,
    }), 200


@app.route('/health')
def health():
    """Health check."""
    return jsonify({'status': 'healthy'}), 200
