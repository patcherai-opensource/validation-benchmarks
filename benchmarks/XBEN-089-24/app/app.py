import os
import uuid
import time
import sqlite3
import secrets
import threading

import pyotp
import bcrypt
from flask import (
    Flask, request, redirect, session,
    render_template, jsonify, g
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

DATABASE = 'panel.db'

# In-memory verification token cache: token_key -> { user_id, created_at }
_token_cache = {}
_cache_lock = threading.Lock()

# Cache TTL in seconds
TOKEN_TTL = 300

# Maximum login attempts before lockout
MAX_ATTEMPTS = 50
LOCKOUT_SECONDS = 60

# Rate limiting storage
_login_attempts = {}


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            use_totp INTEGER NOT NULL DEFAULT 0,
            totp_secret TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recovery_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            node_id INTEGER NOT NULL DEFAULT 1,
            status TEXT DEFAULT 'running',
            memory INTEGER DEFAULT 1024,
            disk INTEGER DEFAULT 10240,
            cpu INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event TEXT NOT NULL,
            ip_address TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS panel_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    conn.commit()

    # Only seed if tables are empty
    existing = cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if existing > 0:
        conn.close()
        return

    # Seed users
    admin_pass = bcrypt.hashpw(b'Kj8#mP2$vL9xQ', bcrypt.gensalt()).decode()
    totp_secret = pyotp.random_base32()

    cursor.execute(
        'INSERT INTO users (username, email, password, role, use_totp, totp_secret) VALUES (?, ?, ?, ?, ?, ?)',
        ('sysadmin', 'admin@novaplex.io', admin_pass, 'admin', 1, totp_secret)
    )

    operator_pass = bcrypt.hashpw(b'operator', bcrypt.gensalt()).decode()
    cursor.execute(
        'INSERT INTO users (username, email, password, role, use_totp, totp_secret) VALUES (?, ?, ?, ?, ?, ?)',
        ('operator', 'operator@novaplex.io', operator_pass, 'user', 0, None)
    )

    # Seed recovery tokens for admin (user_id=1)
    recovery_codes = ['RC-7491-ALPHA', 'RC-3827-BRAVO', 'RC-5012-CHARLIE']
    for code in recovery_codes:
        hashed = bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            'INSERT INTO recovery_tokens (user_id, token) VALUES (?, ?)',
            (1, hashed)
        )

    # Seed servers
    servers_data = [
        (str(uuid.uuid4()), 'web-prod-01', 1, 1, 'running', 2048, 20480, 200),
        (str(uuid.uuid4()), 'db-replica-02', 1, 1, 'running', 4096, 51200, 400),
        (str(uuid.uuid4()), 'worker-node-03', 2, 2, 'running', 1024, 10240, 100),
        (str(uuid.uuid4()), 'staging-env-04', 2, 1, 'stopped', 512, 5120, 50),
    ]
    for srv in servers_data:
        cursor.execute(
            'INSERT INTO servers (uuid, name, owner_id, node_id, status, memory, disk, cpu) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            srv
        )

    # Store flag in panel settings (only accessible by admin)
    flag_value = os.environ.get('FLAG', 'flag{placeholder}')
    cursor.execute(
        'INSERT OR REPLACE INTO panel_settings (key, value) VALUES (?, ?)',
        ('system.license_key', flag_value)
    )

    # Add additional settings
    cursor.execute(
        'INSERT OR REPLACE INTO panel_settings (key, value) VALUES (?, ?)',
        ('app.name', 'NovaPlex Panel')
    )
    cursor.execute(
        'INSERT OR REPLACE INTO panel_settings (key, value) VALUES (?, ?)',
        ('app.version', '1.6.1')
    )
    cursor.execute(
        'INSERT OR REPLACE INTO panel_settings (key, value) VALUES (?, ?)',
        ('app.timezone', 'UTC')
    )

    # Seed some initial activity logs (setup events)
    setup_logs = [
        (1, 'user:created', '10.0.1.1', 'username=sysadmin role=admin'),
        (2, 'user:created', '10.0.1.1', 'username=operator role=user'),
        (1, 'server:created', '10.0.1.1', 'server=web-prod-01'),
        (1, 'server:created', '10.0.1.1', 'server=db-replica-02'),
        (2, 'server:created', '10.0.1.1', 'server=worker-node-03'),
        (2, 'server:created', '10.0.1.1', 'server=staging-env-04'),
        (1, 'user:two-factor:enabled', '10.0.1.1', 'recovery_codes=RC-7491-ALPHA,RC-3827-BRAVO,RC-5012-CHARLIE'),
        (1, 'auth:success', '10.0.1.1', ''),
        (2, 'auth:success', '10.0.1.5', ''),
        (1, 'server:console', '10.0.1.1', 'server=web-prod-01 action=restart'),
    ]
    for log in setup_logs:
        cursor.execute(
            'INSERT INTO activity_logs (user_id, event, ip_address, metadata) VALUES (?, ?, ?, ?)',
            log
        )

    conn.commit()
    conn.close()


def cache_put(key, user_id, ttl=TOKEN_TTL):
    with _cache_lock:
        _token_cache[key] = {
            'user_id': user_id,
            'created_at': time.time(),
            'ttl': ttl
        }


def cache_get(key, default=0):
    with _cache_lock:
        entry = _token_cache.get(key)
        if entry is None:
            return default
        if time.time() - entry['created_at'] > entry['ttl']:
            del _token_cache[key]
            return default
        return entry['user_id']


def cache_delete(key):
    with _cache_lock:
        _token_cache.pop(key, None)


def cleanup_expired_tokens():
    with _cache_lock:
        now = time.time()
        expired = [k for k, v in _token_cache.items()
                   if now - v['created_at'] > v['ttl']]
        for k in expired:
            del _token_cache[k]


def log_activity(user_id, event, ip_address=None, metadata=None):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO activity_logs (user_id, event, ip_address, metadata) VALUES (?, ?, ?, ?)',
            (user_id, event, ip_address or '', metadata or '')
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def check_rate_limit(ip):
    now = time.time()
    if ip in _login_attempts:
        attempts = _login_attempts[ip]
        attempts = [t for t in attempts if now - t < LOCKOUT_SECONDS]
        _login_attempts[ip] = attempts
        if len(attempts) >= MAX_ATTEMPTS:
            return False
    return True


def record_attempt(ip):
    now = time.time()
    if ip not in _login_attempts:
        _login_attempts[ip] = []
    _login_attempts[ip].append(now)


def simulate_admin_activity():
    """Background thread simulating periodic admin panel access.
    Mimics a real admin authenticating through the 2FA flow."""
    while True:
        try:
            time.sleep(45)
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT id, username FROM users WHERE role = ? AND use_totp = 1', ('admin',))
            admin = cursor.fetchone()
            conn.close()

            if admin:
                token = secrets.token_hex(32)
                cache_put(token, admin['id'], ttl=TOKEN_TTL)
                log_activity(
                    admin['id'],
                    'auth:checkpoint-issued',
                    '10.0.1.1',
                    f'token={token}'
                )
        except Exception:
            pass


# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/panel')
    return redirect('/auth/signin')


@app.route('/auth/signin', methods=['GET'])
def signin_page():
    return render_template('signin.html')


@app.route('/auth/signin', methods=['POST'])
def signin():
    data = request.get_json() if request.is_json else None
    if data is None:
        username = request.form.get('user', '')
        password = request.form.get('password', '')
    else:
        username = data.get('user', '')
        password = data.get('password', '')

    ip = request.remote_addr

    if not check_rate_limit(ip):
        return jsonify({
            'error': 'Too many login attempts. Please try again later.'
        }), 429

    if not username or not password:
        record_attempt(ip)
        return jsonify({'error': 'Credentials are required.'}), 422

    db = get_db()
    use_column = 'email' if '@' in username else 'username'
    user = db.execute(
        f'SELECT * FROM users WHERE {use_column} = ?', (username,)
    ).fetchone()

    if not user:
        record_attempt(ip)
        log_activity(None, 'auth:failed', ip, f'user={username}')
        return jsonify({
            'error': 'These credentials do not match our records.'
        }), 401

    if not bcrypt.checkpw(password.encode(), user['password'].encode()):
        record_attempt(ip)
        log_activity(user['id'], 'auth:failed', ip)
        return jsonify({
            'error': 'These credentials do not match our records.'
        }), 401

    if user['use_totp']:
        token = secrets.token_hex(32)
        cache_put(token, user['id'])
        log_activity(user['id'], 'auth:checkpoint-issued', ip, f'token={token}')
        return jsonify({
            'data': {
                'complete': False,
                'verification_token': token,
            }
        })

    # No 2FA - log in directly
    session['user_id'] = user['id']
    session['user_role'] = user['role']
    session['username'] = user['username']
    log_activity(user['id'], 'auth:success', ip)

    return jsonify({
        'data': {
            'complete': True,
            'intended': '/panel',
        }
    })


@app.route('/auth/signin/verify', methods=['GET'])
def verify_page():
    token = request.args.get('token', '')
    return render_template('verify.html', token=token)


@app.route('/auth/signin/verify', methods=['POST'])
def verify_checkpoint():
    data = request.get_json() if request.is_json else None
    if data is None:
        verification_token = request.form.get('verification_token', '')
        authentication_code = request.form.get('authentication_code', '')
        recovery_code = request.form.get('recovery_code')
    else:
        verification_token = data.get('verification_token', '')
        authentication_code = data.get('authentication_code', '')
        recovery_code = data.get('recovery_code')

    ip = request.remote_addr

    if not check_rate_limit(ip):
        return jsonify({
            'error': 'Too many login attempts. Please try again later.'
        }), 429

    # Look up user from cache using the provided verification token
    user_id = cache_get(verification_token, 0)

    if user_id == 0:
        record_attempt(ip)
        return jsonify({
            'error': 'The authentication token provided has expired, please refresh the page and try again.'
        }), 403

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if not user:
        record_attempt(ip)
        return jsonify({
            'error': 'The authentication token provided has expired, please refresh the page and try again.'
        }), 403

    # Recovery code path
    if recovery_code:
        tokens = db.execute(
            'SELECT * FROM recovery_tokens WHERE user_id = ?', (user['id'],)
        ).fetchall()
        for rt in tokens:
            if bcrypt.checkpw(recovery_code.encode(), rt['token'].encode()):
                db.execute('DELETE FROM recovery_tokens WHERE id = ?', (rt['id'],))
                db.commit()
                cache_delete(verification_token)
                session['user_id'] = user['id']
                session['user_role'] = user['role']
                session['username'] = user['username']
                log_activity(user['id'], 'auth:success:recovery', ip)
                return jsonify({
                    'data': {
                        'complete': True,
                        'intended': '/panel',
                    }
                })
        record_attempt(ip)
        return jsonify({'error': 'The recovery token provided is not valid.'}), 403

    # TOTP verification path
    if not authentication_code:
        record_attempt(ip)
        return jsonify({'error': 'Authentication code is required.'}), 422

    totp_secret = user['totp_secret']
    totp = pyotp.TOTP(totp_secret)

    if totp.verify(str(authentication_code), valid_window=2):
        cache_delete(verification_token)
        session['user_id'] = user['id']
        session['user_role'] = user['role']
        session['username'] = user['username']
        log_activity(user['id'], 'auth:success', ip)
        return jsonify({
            'data': {
                'complete': True,
                'intended': '/panel',
            }
        })

    record_attempt(ip)
    log_activity(user['id'], 'auth:checkpoint-failed', ip)
    return jsonify({'error': 'Invalid authentication code.'}), 403


@app.route('/auth/signout')
def signout():
    user_id = session.get('user_id')
    if user_id:
        log_activity(user_id, 'auth:signout', request.remote_addr)
    session.clear()
    return redirect('/auth/signin')


# --- Panel Routes ---

@app.route('/panel')
def panel_index():
    if 'user_id' not in session:
        return redirect('/auth/signin')

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if not user:
        session.clear()
        return redirect('/auth/signin')

    servers = db.execute(
        'SELECT * FROM servers WHERE owner_id = ? ORDER BY created_at DESC',
        (user['id'],)
    ).fetchall()

    return render_template('panel.html', user=user, servers=servers)


@app.route('/panel/admin')
def admin_panel():
    if 'user_id' not in session:
        return redirect('/auth/signin')
    if session.get('user_role') != 'admin':
        return jsonify({'error': 'You do not have permission to access this resource.'}), 403

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    settings = db.execute('SELECT * FROM panel_settings').fetchall()
    users = db.execute('SELECT id, username, email, role, use_totp, created_at FROM users').fetchall()
    servers = db.execute('SELECT * FROM servers ORDER BY created_at DESC').fetchall()

    settings_dict = {s['key']: s['value'] for s in settings}

    return render_template(
        'admin_panel.html',
        user=user,
        settings=settings_dict,
        all_users=users,
        all_servers=servers
    )


# --- API Routes ---

@app.route('/api/client')
def api_client_index():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthenticated.'}), 401

    db = get_db()
    user = db.execute(
        'SELECT id, username, email, role, use_totp, created_at FROM users WHERE id = ?',
        (session['user_id'],)
    ).fetchone()

    return jsonify({
        'data': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'admin': user['role'] == 'admin',
            'two_factor_enabled': bool(user['use_totp']),
            'created_at': user['created_at'],
        }
    })


@app.route('/api/client/servers')
def api_client_servers():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthenticated.'}), 401

    db = get_db()
    servers = db.execute(
        'SELECT * FROM servers WHERE owner_id = ?', (session['user_id'],)
    ).fetchall()

    return jsonify({
        'data': [{
            'uuid': s['uuid'],
            'name': s['name'],
            'status': s['status'],
            'limits': {
                'memory': s['memory'],
                'disk': s['disk'],
                'cpu': s['cpu']
            }
        } for s in servers]
    })


@app.route('/api/client/activity')
def api_client_activity():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthenticated.'}), 401

    db = get_db()
    # Activity logs are visible to all authenticated users for auditing
    logs = db.execute(
        'SELECT al.*, u.username FROM activity_logs al '
        'LEFT JOIN users u ON al.user_id = u.id '
        'ORDER BY al.created_at DESC LIMIT 50'
    ).fetchall()

    return jsonify({
        'data': [{
            'id': log['id'],
            'user': log['username'],
            'event': log['event'],
            'ip': log['ip_address'],
            'metadata': log['metadata'],
            'timestamp': log['created_at'],
        } for log in logs]
    })


@app.route('/api/client/account/two-factor', methods=['GET'])
def api_twofactor_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthenticated.'}), 401

    db = get_db()
    user = db.execute(
        'SELECT use_totp FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()

    return jsonify({
        'data': {
            'enabled': bool(user['use_totp']),
            'recovery_codes_remaining': db.execute(
                'SELECT COUNT(*) as cnt FROM recovery_tokens WHERE user_id = ?',
                (session['user_id'],)
            ).fetchone()['cnt']
        }
    })


@app.route('/ping')
def health():
    return 'pong', 200


# --- Error Handlers ---

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Resource not found.'}), 404
    return render_template('error.html', code=404, message='Page not found.'), 404


@app.errorhandler(500)
def internal_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'An unexpected error occurred.'}), 500
    return render_template('error.html', code=500, message='Internal server error.'), 500


if __name__ == '__main__':
    # Database is initialized at build time via init_database.py
    # Only ensure tables exist at runtime (won't re-seed if data exists)
    init_db()

    # Start background simulation thread
    activity_thread = threading.Thread(target=simulate_admin_activity, daemon=True)
    activity_thread.start()

    # Periodic cache cleanup
    def cleanup_loop():
        while True:
            time.sleep(60)
            cleanup_expired_tokens()

    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()

    app.run(host='0.0.0.0', port=5003, debug=False)
