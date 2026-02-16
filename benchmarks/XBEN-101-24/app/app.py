import hashlib
import base64
import os
import time
import logging
from flask import Flask, request, make_response, redirect, url_for, render_template, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32).hex()

# Read flag from build-time planted file
FLAG_FILE = '/app/flag.txt'
try:
    with open(FLAG_FILE, 'r') as f:
        FLAG = f.read().strip()
except FileNotFoundError:
    FLAG = 'FLAG{placeholder}'

logger = logging.getLogger('querybridge')
logging.basicConfig(level=logging.WARNING)

SIGNATURE_DELIMITER = '&sig='
DIGEST_ALGORITHM = 'sha512'

# Secret for cookie signing - generated once at startup
_signing_secret = os.urandom(64)


class TokenSigner:
    """Signs and verifies authentication tokens using SHA-512 HMAC-like digest."""

    def __init__(self, secret_bytes):
        if secret_bytes is None:
            raise ValueError("Secret bytes must not be None")
        self._secret = secret_bytes

    def create_signed_token(self, payload):
        if not payload:
            raise ValueError("Empty payload cannot be signed")
        sig = self._compute_digest(payload)
        return payload + SIGNATURE_DELIMITER + sig

    def validate_and_extract(self, signed_token):
        idx = signed_token.rfind(SIGNATURE_DELIMITER)
        if idx == -1:
            raise ValueError("Malformed token: missing signature delimiter in " + signed_token)
        provided_sig = signed_token[idx + len(SIGNATURE_DELIMITER):]
        raw_payload = signed_token[:idx]
        expected_sig = self._compute_digest(raw_payload)

        if not self._constant_time_compare(provided_sig.encode(), expected_sig.encode()):
            raise ValueError(
                "Token signature mismatch, provided = " + provided_sig +
                " expected = " + expected_sig
            )
        return raw_payload

    def _compute_digest(self, data):
        h = hashlib.new(DIGEST_ALGORITHM)
        h.update(data.encode('utf-8'))
        h.update(self._secret)
        return base64.b64encode(h.digest()).decode('utf-8')

    @staticmethod
    def _constant_time_compare(a, b):
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
        return result == 0


signer = TokenSigner(_signing_secret)

# In-memory user store (seeded with default users)
USERS = {
    'admin': {'password': os.urandom(32).hex(), 'role': 'admin'},
    'analyst': {'password': 'analyst123', 'role': 'analyst'},
    'viewer': {'password': 'viewer456', 'role': 'viewer'},
}

SESSION_COOKIE_NAME = 'qb.session.auth'
SESSION_MAX_AGE = 3600


def build_cookie_payload(username, role):
    ts = int(time.time())
    return f"cu={username}&rl={role}&ts={ts}"


def parse_cookie_payload(payload):
    parts = {}
    for segment in payload.split('&'):
        if '=' in segment:
            k, v = segment.split('=', 1)
            parts[k] = v
    return parts


def get_authenticated_user(req):
    """Extract and validate session cookie. Returns (username, role) or raises ValueError."""
    cookie_val = req.cookies.get(SESSION_COOKIE_NAME)
    if not cookie_val:
        return None
    payload = signer.validate_and_extract(cookie_val)
    info = parse_cookie_payload(payload)
    username = info.get('cu')
    role = info.get('rl')
    if username and role:
        return (username, role)
    return None


@app.route('/ping')
def health_check():
    return 'OK', 200


@app.route('/')
def index():
    try:
        user = get_authenticated_user(request)
    except ValueError:
        # Invalid cookie, clear it and redirect
        resp = make_response(redirect(url_for('index')))
        resp.delete_cookie(SESSION_COOKIE_NAME)
        return resp
    if user:
        return render_template('dashboard.html', username=user[0], role=user[1])
    return render_template('index.html')


@app.route('/session/connect', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user_rec = USERS.get(username)
        if user_rec and user_rec['password'] == password:
            payload = build_cookie_payload(username, user_rec['role'])
            signed = signer.create_signed_token(payload)
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie(SESSION_COOKIE_NAME, signed, max_age=SESSION_MAX_AGE, httponly=True)
            return resp
        else:
            error = 'Invalid credentials'

    # Check if user is already authenticated
    try:
        user = get_authenticated_user(request)
        if user:
            return redirect(url_for('index'))
    except ValueError:
        pass

    return render_template('login.html', error=error)


@app.route('/session/disconnect', methods=['POST'])
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie(SESSION_COOKIE_NAME)
    return resp


@app.route('/api/v1/verify-token', methods=['POST'])
def verify_token():
    """API endpoint for validating session tokens.
    Used by downstream services to verify authentication cookies."""
    token = None
    if request.is_json:
        token = request.json.get('token', '')
    else:
        token = request.form.get('token', '')
    if not token:
        return jsonify({'valid': False, 'error': 'No token provided'}), 400

    try:
        payload = signer.validate_and_extract(token)
        info = parse_cookie_payload(payload)
        return jsonify({
            'valid': True,
            'user': info.get('cu'),
            'role': info.get('rl')
        })
    except ValueError as e:
        return jsonify({'valid': False, 'error': str(e)}), 401


@app.route('/api/v1/queries', methods=['GET'])
def list_queries():
    try:
        user = get_authenticated_user(request)
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    sample_queries = [
        {'id': 1, 'sql': 'SELECT count(*) FROM transactions', 'status': 'completed', 'owner': 'analyst'},
        {'id': 2, 'sql': 'SELECT * FROM users LIMIT 10', 'status': 'completed', 'owner': 'analyst'},
        {'id': 3, 'sql': 'SELECT avg(amount) FROM transactions WHERE date > \'2024-01-01\'', 'status': 'running', 'owner': 'viewer'},
    ]
    return jsonify({'queries': sample_queries})


@app.route('/api/v1/cluster/status', methods=['GET'])
def cluster_status():
    try:
        user = get_authenticated_user(request)
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    return jsonify({
        'cluster': 'production-01',
        'nodes': 4,
        'status': 'healthy',
        'uptime': '14d 6h 32m',
        'version': '3.1.3'
    })


@app.route('/admin/config', methods=['GET'])
def admin_config():
    try:
        user = get_authenticated_user(request)
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    if not user:
        return redirect(url_for('login'))
    username, role = user
    if role != 'admin':
        return render_template('forbidden.html'), 403
    return render_template('admin_config.html', flag=FLAG, username=username)


@app.route('/api/v1/tables', methods=['GET'])
def list_tables():
    try:
        user = get_authenticated_user(request)
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    tables = [
        {'name': 'transactions', 'rows': 1584203, 'size': '2.3 GB'},
        {'name': 'users', 'rows': 45021, 'size': '128 MB'},
        {'name': 'sessions', 'rows': 892341, 'size': '567 MB'},
        {'name': 'audit_log', 'rows': 3291042, 'size': '4.1 GB'},
    ]
    return jsonify({'tables': tables})


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
