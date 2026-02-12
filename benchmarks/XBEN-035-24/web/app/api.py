import uuid
from flask import Blueprint, request, jsonify, session
from .engine import evaluate_expression, get_session_history, reset_session

api_bp = Blueprint('api', __name__)


def _get_session_id():
    if 'sid' not in session:
        session['sid'] = uuid.uuid4().hex
    return session['sid']


@api_bp.route('/evaluate', methods=['POST'])
def evaluate():
    """Evaluate a mathematical expression or code block.

    Accepts JSON body:
        { "code": "<expression or code>" }

    Returns JSON:
        { "result": "<evaluation result>", "errors": [...] }
    """
    data = request.get_json(silent=True)
    if not data or 'code' not in data:
        return jsonify({'error': 'Missing required field: code'}), 400

    code = data['code']
    if not isinstance(code, str) or len(code) == 0:
        return jsonify({'error': 'Code must be a non-empty string'}), 400

    if len(code) > 50000:
        return jsonify({'error': 'Code exceeds maximum length (50000 chars)'}), 400

    sid = _get_session_id()

    try:
        result = evaluate_expression(sid, code)
        return jsonify(result)
    except Exception:
        return jsonify({'error': 'Evaluation failed'}), 500


@api_bp.route('/history', methods=['GET'])
def history():
    """Return evaluation history for the current session."""
    sid = _get_session_id()
    hist = get_session_history(sid)
    return jsonify({'history': hist})


@api_bp.route('/reset', methods=['POST'])
def reset():
    """Reset the current session interpreter."""
    sid = _get_session_id()
    reset_session(sid)
    session.pop('sid', None)
    return jsonify({'status': 'Session reset'})


@api_bp.route('/examples', methods=['GET'])
def examples():
    """Return example expressions users can try."""
    return jsonify({
        'examples': [
            {
                'title': 'Basic arithmetic',
                'code': '2 + 3 * 4',
                'description': 'Standard math operations'
            },
            {
                'title': 'Variable assignment',
                'code': 'x = 10\ny = x ** 2\ny',
                'description': 'Define and use variables'
            },
            {
                'title': 'Trigonometry',
                'code': 'sin(pi / 4)',
                'description': 'Trigonometric functions with numpy'
            },
            {
                'title': 'Custom function',
                'code': 'def quadratic(a, b, c, x):\n    return a*x**2 + b*x + c\nquadratic(1, -3, 2, 5)',
                'description': 'Define and call custom functions'
            },
            {
                'title': 'Array operations',
                'code': 'arr = linspace(0, 10, 5)\nsum(arr)',
                'description': 'Create and manipulate arrays'
            },
            {
                'title': 'Statistics',
                'code': 'data = [23, 45, 12, 67, 34, 89, 56]\nmean(data)',
                'description': 'Statistical calculations'
            },
        ]
    })
