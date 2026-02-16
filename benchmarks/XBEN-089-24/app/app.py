import os
import sqlite3
import threading
import time
import hashlib
import secrets
from functools import wraps
from flask import Flask, request, redirect, session, render_template, jsonify, g, abort

app = Flask(__name__)

def _derive_secret():
    """Derive session key from installation-specific data."""
    try:
        with open('/app/data/.flag_seed', 'rb') as f:
            seed = f.read()
    except FileNotFoundError:
        seed = b'default-installation-seed'
    return hashlib.sha256(b'session-signing-' + seed).hexdigest()

app.secret_key = _derive_secret()

DATABASE = '/app/data/cms.db'

# ---------------------------------------------------------------------------
# Runtime level management
# ---------------------------------------------------------------------------
LEVEL_RUN = 'Run'
LEVEL_SETUP = 'Setup'
LEVEL_BOOT = 'Boot'

_runtime_lock = threading.Lock()
_runtime_level = LEVEL_BOOT
_db_available = True


def get_runtime_level():
    global _runtime_level
    return _runtime_level


def set_runtime_level(level):
    global _runtime_level
    with _runtime_lock:
        _runtime_level = level


def check_db_available():
    """Check if database is reachable."""
    global _db_available
    return _db_available


def determine_runtime_level():
    """
    Determine the runtime level based on database connectivity.
    If the database cannot be reached, we drop to Setup level so the
    administrator can reconfigure the connection.
    """
    if not check_db_available():
        set_runtime_level(LEVEL_SETUP)
        return

    try:
        conn = sqlite3.connect(DATABASE, timeout=3)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cms_users'")
        result = cursor.fetchone()
        conn.close()
        if result:
            set_runtime_level(LEVEL_RUN)
        else:
            set_runtime_level(LEVEL_SETUP)
    except Exception:
        set_runtime_level(LEVEL_SETUP)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

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


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    return f"{salt}:{hashed}"


def verify_password(stored, provided):
    try:
        salt, hashed = stored.split(':')
        return hash_password(provided, salt) == stored
    except Exception:
        return False


def init_db():
    """Initialize database schema and seed data."""
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            user_group TEXT NOT NULL DEFAULT 'editor',
            is_approved INTEGER NOT NULL DEFAULT 1,
            is_locked INTEGER NOT NULL DEFAULT 0,
            last_login TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            body TEXT,
            content_type TEXT NOT NULL DEFAULT 'page',
            status TEXT NOT NULL DEFAULT 'draft',
            author_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES cms_users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            media_type TEXT NOT NULL,
            file_size INTEGER,
            uploaded_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uploaded_by) REFERENCES cms_users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            detail TEXT,
            ip_address TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Read flag from build-time file
    flag_value = 'flag{placeholder}'
    try:
        with open('/app/data/.flag_seed', 'r') as f:
            flag_value = f.read().strip()
    except FileNotFoundError:
        pass

    # Seed super admin user (id=-1 is reserved like Umbraco's SuperUser)
    admin_pw = hash_password(secrets.token_hex(32))
    cursor.execute('''
        INSERT OR IGNORE INTO cms_users
        (id, email, username, password_hash, display_name, user_group, is_approved)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (-1, 'admin@localcms.io', 'superadmin', admin_pw, 'Super Admin', 'admin', 1))

    # Seed editor user
    editor_pw = hash_password('editor2024')
    cursor.execute('''
        INSERT OR IGNORE INTO cms_users
        (email, username, password_hash, display_name, user_group, is_approved)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('editor@localcms.io', 'editor', editor_pw, 'Content Editor', 'editor', 1))

    # Seed content
    cursor.execute('''
        INSERT OR IGNORE INTO cms_content (title, slug, body, content_type, status, author_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('Welcome', 'welcome', '<p>Welcome to our CMS platform.</p>', 'page', 'published', -1))

    cursor.execute('''
        INSERT OR IGNORE INTO cms_content (title, slug, body, content_type, status, author_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('About Us', 'about', '<p>Learn more about our organization.</p>', 'page', 'published', -1))

    # Store flag in settings (only accessible from admin panel)
    cursor.execute('''
        INSERT OR REPLACE INTO cms_settings (key, value)
        VALUES (?, ?)
    ''', ('system.license.key', flag_value))

    # Store version info
    cursor.execute('''
        INSERT OR REPLACE INTO cms_settings (key, value)
        VALUES (?, ?)
    ''', ('system.version', '12.1.0'))

    cursor.execute('''
        INSERT OR REPLACE INTO cms_settings (key, value)
        VALUES (?, ?)
    ''', ('system.install_completed', '1'))

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Auth decorators
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/umbraco/login')
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/umbraco/login')
        if session.get('user_group') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def setup_mode_required(f):
    """Only allow access when runtime level is Setup."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if get_runtime_level() != LEVEL_SETUP:
            return jsonify({'error': 'Forbidden', 'message': 'Application is not in setup mode.'}), 403
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Lifecycle: background thread re-evaluates runtime level periodically
# ---------------------------------------------------------------------------

def runtime_monitor():
    """Periodically re-check DB connectivity and update runtime level."""
    while True:
        time.sleep(5)
        determine_runtime_level()


# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return redirect('/umbraco')


@app.route('/ping')
def health_ping():
    return 'ok', 200


@app.route('/umbraco')
def backoffice_root():
    if get_runtime_level() == LEVEL_SETUP:
        return redirect('/umbraco/setup')
    if 'user_id' in session:
        return redirect('/umbraco/dashboard')
    return redirect('/umbraco/login')


@app.route('/umbraco/login', methods=['GET', 'POST'])
def backoffice_login():
    if get_runtime_level() == LEVEL_SETUP:
        return redirect('/umbraco/setup')

    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

    if not email or not password:
        return render_template('login.html', error='Please provide email and password.')

    try:
        db = get_db()
        user = db.execute('SELECT * FROM cms_users WHERE email = ?', (email,)).fetchone()
    except Exception:
        return render_template('login.html', error='Service temporarily unavailable.')

    if user and verify_password(user['password_hash'], password):
        if not user['is_approved']:
            return render_template('login.html', error='Account is not approved.')
        if user['is_locked']:
            return render_template('login.html', error='Account is locked.')

        session['user_id'] = user['id']
        session['username'] = user['username']
        session['display_name'] = user['display_name']
        session['user_group'] = user['user_group']

        db.execute('UPDATE cms_users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
        db.commit()

        try:
            db.execute('INSERT INTO cms_audit_log (user_id, action, detail, ip_address) VALUES (?, ?, ?, ?)',
                       (user['id'], 'login', 'User logged in', request.remote_addr))
            db.commit()
        except Exception:
            pass

        return redirect('/umbraco/dashboard')

    return render_template('login.html', error='Invalid email or password.')


@app.route('/umbraco/logout')
def backoffice_logout():
    session.clear()
    return redirect('/umbraco/login')


# ---------------------------------------------------------------------------
# Back office dashboard
# ---------------------------------------------------------------------------

@app.route('/umbraco/dashboard')
@login_required
def backoffice_dashboard():
    db = get_db()
    content = db.execute(
        'SELECT c.*, u.display_name as author_name FROM cms_content c '
        'LEFT JOIN cms_users u ON c.author_id = u.id ORDER BY c.updated_at DESC'
    ).fetchall()
    return render_template('dashboard.html', content=content)


@app.route('/umbraco/content')
@login_required
def backoffice_content():
    db = get_db()
    content = db.execute(
        'SELECT c.*, u.display_name as author_name FROM cms_content c '
        'LEFT JOIN cms_users u ON c.author_id = u.id ORDER BY c.updated_at DESC'
    ).fetchall()
    return render_template('content.html', content=content)


@app.route('/umbraco/media')
@login_required
def backoffice_media():
    db = get_db()
    media = db.execute('SELECT * FROM cms_media ORDER BY created_at DESC').fetchall()
    return render_template('media.html', media=media)


@app.route('/umbraco/users')
@admin_required
def backoffice_users():
    db = get_db()
    users = db.execute('SELECT id, email, username, display_name, user_group, is_approved, is_locked, last_login, created_at FROM cms_users ORDER BY id').fetchall()
    return render_template('users.html', users=users)


@app.route('/umbraco/settings')
@admin_required
def backoffice_settings():
    db = get_db()
    settings = db.execute('SELECT * FROM cms_settings ORDER BY key').fetchall()
    return render_template('settings.html', settings=settings)


# ---------------------------------------------------------------------------
# Back office API endpoints
# ---------------------------------------------------------------------------

@app.route('/umbraco/api/v1/content', methods=['GET'])
@login_required
def api_content_list():
    db = get_db()
    content = db.execute('SELECT id, title, slug, content_type, status, created_at, updated_at FROM cms_content ORDER BY updated_at DESC').fetchall()
    return jsonify([dict(c) for c in content])


@app.route('/umbraco/api/v1/content/<int:content_id>', methods=['GET'])
@login_required
def api_content_get(content_id):
    db = get_db()
    content = db.execute('SELECT * FROM cms_content WHERE id = ?', (content_id,)).fetchone()
    if not content:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(content))


@app.route('/umbraco/api/v1/users', methods=['GET'])
@admin_required
def api_users_list():
    db = get_db()
    users = db.execute('SELECT id, email, username, display_name, user_group, is_approved, is_locked, created_at FROM cms_users ORDER BY id').fetchall()
    return jsonify([dict(u) for u in users])


@app.route('/umbraco/api/v1/audit', methods=['GET'])
@admin_required
def api_audit_log():
    db = get_db()
    logs = db.execute(
        'SELECT l.*, u.display_name as user_name FROM cms_audit_log l '
        'LEFT JOIN cms_users u ON l.user_id = u.id ORDER BY l.created_at DESC LIMIT 100'
    ).fetchall()
    return jsonify([dict(l) for l in logs])


# ---------------------------------------------------------------------------
# Runtime status API (information endpoint, like Umbraco's /umbraco/api)
# ---------------------------------------------------------------------------

@app.route('/umbraco/api/v1/runtime/status', methods=['GET'])
def api_runtime_status():
    """Public endpoint returning current runtime level."""
    level = get_runtime_level()
    resp = {
        'level': level,
        'version': '12.1.0',
        'serverTime': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'endpoints': {
            'content': '/umbraco/api/v1/content',
            'users': '/umbraco/api/v1/users',
            'audit': '/umbraco/api/v1/audit',
            'diagnostics': '/umbraco/api/v1/diagnostics/connectivity',
            'setup': '/umbraco/setup/api/status'
        }
    }
    return jsonify(resp)


# ---------------------------------------------------------------------------
# Diagnostics / maintenance endpoint
# ---------------------------------------------------------------------------

@app.route('/umbraco/api/v1/diagnostics/connectivity', methods=['POST'])
def api_diagnostics_connectivity():
    """Manage database connectivity for health monitoring."""
    global _db_available
    action = request.json.get('action', '') if request.is_json else request.form.get('action', '')

    if action == 'test':
        try:
            conn = sqlite3.connect(DATABASE, timeout=2)
            conn.execute('SELECT 1')
            conn.close()
            return jsonify({'status': 'connected', 'database': 'cms.db'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

    elif action == 'suspend':
        _db_available = False
        determine_runtime_level()
        return jsonify({'status': 'suspended', 'runtimeLevel': get_runtime_level()})

    elif action == 'resume':
        _db_available = True
        determine_runtime_level()
        return jsonify({'status': 'resumed', 'runtimeLevel': get_runtime_level()})

    return jsonify({'error': 'Invalid action. Use test, suspend, or resume.'}), 400


# ---------------------------------------------------------------------------
# Setup / Install endpoints (only active when runtime level is Setup)
# ---------------------------------------------------------------------------

@app.route('/umbraco/setup')
def setup_page():
    if get_runtime_level() != LEVEL_SETUP:
        return redirect('/umbraco')
    return render_template('setup.html')


@app.route('/umbraco/setup/api/status', methods=['GET'])
@setup_mode_required
def setup_api_status():
    """Returns current setup status and available steps."""
    return jsonify({
        'runtimeLevel': get_runtime_level(),
        'steps': [
            {'name': 'DatabaseConfiguration', 'complete': False},
            {'name': 'SchemaValidation', 'complete': False},
            {'name': 'FinalizeSetup', 'complete': False}
        ]
    })


@app.route('/umbraco/setup/api/validatedb', methods=['POST'])
@setup_mode_required
def setup_api_validate_db():
    """Validate database connection settings."""
    return jsonify({
        'valid': check_db_available(),
        'message': 'Database connection validated.' if check_db_available() else 'Cannot reach database.'
    })


@app.route('/umbraco/setup/api/finalize', methods=['POST'])
@setup_mode_required
def setup_api_finalize():
    """Complete the setup process and restart the runtime."""
    global _db_available

    level_before_restart = get_runtime_level()

    # Restore database connectivity (simulates the DB coming back)
    _db_available = True
    determine_runtime_level()

    if level_before_restart == LEVEL_SETUP:
        try:
            db_conn = sqlite3.connect(DATABASE)
            db_conn.row_factory = sqlite3.Row
            super_user = db_conn.execute('SELECT * FROM cms_users WHERE id = -1').fetchone()
            db_conn.close()

            if super_user:
                session['user_id'] = super_user['id']
                session['username'] = super_user['username']
                session['display_name'] = super_user['display_name']
                session['user_group'] = super_user['user_group']
        except Exception:
            pass

    return jsonify({
        'success': True,
        'runtimeLevel': get_runtime_level(),
        'redirect': '/umbraco/dashboard'
    })


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access denied.'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error.'), 500


# ---------------------------------------------------------------------------
# Application startup
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    init_db()
    determine_runtime_level()

    monitor_thread = threading.Thread(target=runtime_monitor, daemon=True)
    monitor_thread.start()

    app.run(host='0.0.0.0', port=5003)
