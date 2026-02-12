"""
Databases management API namespace.

Handles database connection configurations.
"""

import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

databases_bp = Blueprint('databases', __name__)

# Database registry
_databases = {
    'mindsdb': {
        'name': 'mindsdb',
        'engine': 'mindsdb',
        'type': 'system',
        'tables': ['models', 'predictors', 'jobs'],
    },
    'files': {
        'name': 'files',
        'engine': 'files',
        'type': 'system',
        'tables': [],
    },
    'information_schema': {
        'name': 'information_schema',
        'engine': 'system',
        'type': 'system',
        'tables': ['SCHEMATA', 'TABLES', 'COLUMNS'],
    },
    'admin_config': {
        'name': 'admin_config',
        'engine': 'http',
        'type': 'data',
        'connection_data': {
            'url': 'http://127.0.0.1:8888/config',
            'method': 'GET',
        },
        'tables': ['settings'],
    },
}


@databases_bp.route('/databases', methods=['GET'])
def list_databases():
    """List all database connections."""
    result = []
    for name, db in _databases.items():
        result.append({
            'name': db['name'],
            'engine': db['engine'],
            'type': db.get('type', 'data'),
        })
    return jsonify(result), 200


@databases_bp.route('/databases/<name>', methods=['GET'])
def get_database(name):
    """Get database details."""
    db = _databases.get(name)
    if db is None:
        return jsonify({'error': f'Database "{name}" not found'}), 404
    return jsonify(db), 200


@databases_bp.route('/databases/<name>', methods=['PUT'])
def create_database(name):
    """Create a new database connection."""
    data = request.get_json(silent=True) or {}

    engine = data.get('engine')
    if not engine:
        return jsonify({'error': '"engine" field is required'}), 400

    connection_data = data.get('connection_data', {})

    _databases[name] = {
        'name': name,
        'engine': engine,
        'type': 'data',
        'connection_data': connection_data,
        'tables': [],
    }

    return jsonify({'message': f'Database "{name}" created', 'name': name}), 201


@databases_bp.route('/databases/<name>', methods=['DELETE'])
def delete_database(name):
    """Delete a database connection."""
    if name not in _databases:
        return jsonify({'error': f'Database "{name}" not found'}), 404

    if _databases[name].get('type') == 'system':
        return jsonify({'error': 'Cannot delete system databases'}), 403

    del _databases[name]
    return jsonify({'message': f'Database "{name}" deleted'}), 200
