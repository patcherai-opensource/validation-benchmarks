"""
Route definitions for the MathEngine application.
"""
import uuid
from flask import (
    Blueprint, request, jsonify, render_template,
    session, make_response
)
from .engine import get_session, remove_session

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/docs')
def documentation():
    return render_template('docs.html')


@main_bp.route('/ping')
def health():
    return 'ok', 200


@api_bp.route('/compute', methods=['POST'])
def compute():
    """
    Evaluate a mathematical expression.

    Accepts JSON body:
        {"expression": "..."}
    or form data:
        expression=...

    Returns JSON with evaluation result.
    """
    sid = request.cookies.get('session_id')
    if not sid:
        sid = uuid.uuid4().hex

    if request.is_json:
        data = request.get_json(silent=True) or {}
        expression = data.get('expression', '')
    else:
        expression = request.form.get('expression', '')

    if not expression:
        return jsonify({'error': 'No expression provided'}), 400

    compute_session = get_session(sid)
    result = compute_session.evaluate(expression)

    resp = make_response(jsonify(result.to_dict()))
    resp.set_cookie('session_id', sid, httponly=True, samesite='Lax', max_age=3600)
    return resp


@api_bp.route('/session', methods=['GET'])
def session_info():
    """Get information about the current computation session."""
    sid = request.cookies.get('session_id')
    if not sid:
        return jsonify({'active': False}), 200

    compute_session = get_session(sid)
    symbols = compute_session.get_symbols()
    return jsonify({
        'active': True,
        'session_id': sid[:8] + '...',
        'symbols': symbols
    })


@api_bp.route('/session', methods=['DELETE'])
def reset_session():
    """Reset the current computation session."""
    sid = request.cookies.get('session_id')
    if sid:
        remove_session(sid)
    return jsonify({'status': 'reset'}), 200


@api_bp.route('/examples', methods=['GET'])
def examples():
    """Return example expressions."""
    return jsonify({
        'examples': [
            {
                'description': 'Basic arithmetic',
                'expression': '2 + 3 * 4'
            },
            {
                'description': 'Trigonometric functions',
                'expression': 'sin(pi / 4)'
            },
            {
                'description': 'Define a function',
                'expression': 'def quadratic(a, b, c, x):\n    return a*x**2 + b*x + c'
            },
            {
                'description': 'Use a defined function',
                'expression': 'quadratic(1, -3, 2, 5)'
            },
            {
                'description': 'List comprehension',
                'expression': '[x**2 for x in range(10)]'
            },
            {
                'description': 'Statistical calculation',
                'expression': 'data = [14, 23, 31, 42, 19]\nsum(data) / len(data)'
            },
        ]
    })
