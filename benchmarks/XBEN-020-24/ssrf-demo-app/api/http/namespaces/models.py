"""
Models management API namespace.

Handles ML model lifecycle operations.
"""

import logging
from datetime import datetime

from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

models_bp = Blueprint('models', __name__)

# Sample model registry
_models = {
    'home_rentals_predictor': {
        'name': 'home_rentals_predictor',
        'engine': 'lightwood',
        'status': 'complete',
        'accuracy': 0.92,
        'created_at': '2024-01-15T10:30:00',
        'training_time': 45.2,
    },
    'customer_churn': {
        'name': 'customer_churn',
        'engine': 'lightwood',
        'status': 'complete',
        'accuracy': 0.87,
        'created_at': '2024-01-20T14:15:00',
        'training_time': 120.5,
    },
}


@models_bp.route('/models', methods=['GET'])
def list_models():
    """List all models."""
    result = []
    for name, model in _models.items():
        result.append({
            'name': model['name'],
            'engine': model['engine'],
            'status': model['status'],
            'accuracy': model.get('accuracy'),
            'created_at': model['created_at'],
        })
    return jsonify(result), 200


@models_bp.route('/models/<name>', methods=['GET'])
def get_model(name):
    """Get model details."""
    model = _models.get(name)
    if model is None:
        return jsonify({'error': f'Model "{name}" not found'}), 404
    return jsonify(model), 200


@models_bp.route('/models/<name>', methods=['PUT'])
def create_model(name):
    """Create a new model (stub)."""
    data = request.get_json(silent=True) or {}

    engine = data.get('engine', 'lightwood')
    predict = data.get('predict')
    training_data = data.get('training_data')

    if not predict:
        return jsonify({'error': '"predict" field is required'}), 400

    _models[name] = {
        'name': name,
        'engine': engine,
        'status': 'generating',
        'accuracy': None,
        'created_at': datetime.utcnow().isoformat(),
        'training_time': None,
        'predict': predict,
    }

    return jsonify({'message': f'Model "{name}" creation started', 'name': name}), 202


@models_bp.route('/models/<name>', methods=['DELETE'])
def delete_model(name):
    """Delete a model."""
    if name not in _models:
        return jsonify({'error': f'Model "{name}" not found'}), 404

    del _models[name]
    return jsonify({'message': f'Model "{name}" deleted'}), 200
