from flask import Flask, request, redirect, session, url_for, render_template, jsonify
import sqlite3
import hashlib
import hmac
import struct
import time
import threading
import os
import base64

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

DATABASE = 'panel.db'

# In-memory token cache (maps confirmation_token -> user_id)
# Mirrors the cache-based approach used in Pterodactyl Panel's LoginCheckpointController
_token_cache = {}
_token_cache_lock = threading.Lock()
TOKEN_TTL = 300


def cache_put(key, value, ttl=TOKEN_TTL):
    with _token_cache_lock:
        _token_cache[key] = {'value': value, 'expires': time.time() + ttl}


def cache_get(key, default=0):
    with _token_cache_lock:
        entry = _token_cache.get(key)
        if entry is None:
            return default
        if time.time() > entry['expires']:
            del _token_cache[key]
            return default
        return entry['value']


def cache_forget(key):
    with _token_cache_lock:
        _token_cache.pop(key, None)


def generate_token(user_id):
    """Generate a confirmation token for the 2FA checkpoint."""
    import json
    payload = json.dumps({"user": user_id, "purpose": "2fa_auth"})
    return base64.urlsafe_b64encode(payload.encode()).decode().rstrip('=')


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def compute_totp(secret, time_offset=0):
    """Compute TOTP code for a given secret and time."""
    t = (int(time.time()) // 30) + time_offset
    key = base64.b32decode(secret, casefold=True)
    msg = struct.pack('>Q', t)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[-1] & 0x0F
    truncated = struct.unpack('>I', h[o:o+4])[0] & 0x7FFFFFFF
    return str(truncated % 1000000).zfill(6)


def verify_totp(secret, code):
    """Verify a TOTP code against a secret with a time window tolerance."""
    for offset in range(-2, 3):
        expected = compute_totp(secret, offset)
        if code == expected:
            return True
    return False


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            totp_enabled INTEGER NOT NULL DEFAULT 0,
            totp_secret TEXT,
            use_totp INTEGER NOT NULL DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            node_id INTEGER NOT NULL DEFAULT 1,
            memory INTEGER NOT NULL DEFAULT 1024,
            disk INTEGER NOT NULL DEFAULT 10240,
            cpu INTEGER NOT NULL DEFAULT 100,
            status TEXT NOT NULL DEFAULT 'running',
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            fqdn TEXT NOT NULL,
            memory INTEGER NOT NULL DEFAULT 8192,
            disk INTEGER NOT NULL DEFAULT 102400,
            scheme TEXT NOT NULL DEFAULT 'https'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            identifier TEXT UNIQUE NOT NULL,
            memo TEXT,
            allowed_ips TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    conn.commit()

    # Seed admin user with TOTP enabled
    # Admin uses a standard TOTP secret
    admin_totp_secret = 'JBSWY3DPEHPK3PXP'
    cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone() is None:
        cursor.execute(
            'INSERT INTO users (username, email, password, role, totp_enabled, totp_secret, use_totp) VALUES (?, ?, ?, ?, ?, ?, ?)',
            ('admin', 'admin@pterodactyl.local', 'Kj8#mP2$vL9nQ4wR', 'admin', 1, admin_totp_secret, 1)
        )
        admin_id = cursor.lastrowid

        cursor.execute(
            'INSERT INTO servers (uuid, name, owner_id, node_id, memory, disk, cpu, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'production-web-01', admin_id, 1, 4096, 51200, 200, 'running')
        )
        cursor.execute(
            'INSERT INTO servers (uuid, name, owner_id, node_id, memory, disk, cpu, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'staging-api-02', admin_id, 1, 2048, 25600, 100, 'running')
        )

    # Seed regular user with TOTP enabled - uses same TOTP secret as admin for testing convenience
    user_totp_secret = 'JBSWY3DPEHPK3PXP'
    cursor.execute('SELECT id FROM users WHERE username = ?', ('user',))
    if cursor.fetchone() is None:
        cursor.execute(
            'INSERT INTO users (username, email, password, role, totp_enabled, totp_secret, use_totp) VALUES (?, ?, ?, ?, ?, ?, ?)',
            ('user', 'user@pterodactyl.local', 'userpassword', 'user', 1, user_totp_secret, 1)
        )
        user_id = cursor.lastrowid

        cursor.execute(
            'INSERT INTO servers (uuid, name, owner_id, node_id, memory, disk, cpu, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'minecraft-server', user_id, 1, 1024, 10240, 100, 'running')
        )

    # Seed node
    cursor.execute('SELECT id FROM nodes WHERE id = 1')
    if cursor.fetchone() is None:
        cursor.execute(
            'INSERT INTO nodes (name, fqdn, memory, disk, scheme) VALUES (?, ?, ?, ?, ?)',
            ('Node-01', 'node01.pterodactyl.local', 16384, 512000, 'https')
        )

    # Seed settings - flag stored as admin system note
    flag_value = open('/app/flag.txt', 'r').read().strip() if os.path.exists('/app/flag.txt') else 'flag{placeholder}'
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('app:name', 'Pterodactyl Panel'))
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('app:version', '1.6.1'))
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('app:admin_note', flag_value))

    conn.commit()
    conn.close()


def simulate_admin_login():
    """Simulates the admin having an active login checkpoint in progress.
    In production, this represents the realistic scenario where an admin
    has begun the login process and their token is sitting in the cache."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    admin = cursor.fetchone()
    conn.close()

    while True:
        if admin:
            token = generate_token(admin['id'])
            cache_put(token, admin['id'], ttl=TOKEN_TTL)
        time.sleep(30)


# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/auth/login')


@app.route('/auth/login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        return render_template('auth/login.html', error='Please provide both username and password.')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password, role, use_totp FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user is None or user['password'] != password:
        return render_template('auth/login.html', error='These credentials do not match our records.')

    if user['use_totp']:
        token = generate_token(user['id'])
        cache_put(token, user['id'])
        return render_template('auth/checkpoint.html', confirmation_token=token)
    else:
        session['user_id'] = user['id']
        session['role'] = user['role']
        return redirect('/dashboard')


@app.route('/auth/login/checkpoint', methods=['POST'])
def auth_login_checkpoint():
    """
    Verify the TOTP code for two-factor authentication.
    The confirmation_token identifies which user is completing 2FA.
    """
    token = request.form.get('confirmation_token', '')
    authentication_code = request.form.get('authentication_code', '').strip()

    if not token or not authentication_code:
        return render_template('auth/login.html', error='Missing required fields for authentication.')

    # Look up the user from the cache using the provided confirmation token
    user_id = cache_get(token, 0)

    if user_id == 0:
        return render_template('auth/login.html', error='Authentication token has expired. Please try again.')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role, totp_secret FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        return render_template('auth/login.html', error='User not found.')

    # Validate the TOTP code
    if not verify_totp(user['totp_secret'], authentication_code):
        return render_template('auth/checkpoint.html',
                             confirmation_token=token,
                             error='The authentication code provided is not valid.')

    # Authentication successful
    cache_forget(token)
    session['user_id'] = user['id']
    session['role'] = user['role']

    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/auth/login')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, role FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    cursor.execute('SELECT id, uuid, name, memory, disk, cpu, status FROM servers WHERE owner_id = ?', (session['user_id'],))
    servers = cursor.fetchall()
    conn.close()

    if user is None:
        session.clear()
        return redirect('/auth/login')

    return render_template('dashboard.html', user=user, servers=servers)


@app.route('/admin')
def admin_panel():
    if 'user_id' not in session:
        return redirect('/auth/login')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    if user is None or user['role'] != 'admin':
        return redirect('/dashboard')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.execute('SELECT * FROM servers')
    servers = cursor.fetchall()
    cursor.execute('SELECT * FROM nodes')
    nodes = cursor.fetchall()
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('app:admin_note',))
    note_row = cursor.fetchone()
    admin_note = note_row['value'] if note_row else ''
    conn.close()

    return render_template('admin/overview.html',
                         user=user, users=users, servers=servers,
                         nodes=nodes, admin_note=admin_note)


@app.route('/admin/settings')
def admin_settings():
    if 'user_id' not in session:
        return redirect('/auth/login')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    if user is None or user['role'] != 'admin':
        return redirect('/dashboard')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings')
    settings = cursor.fetchall()
    conn.close()

    return render_template('admin/settings.html', user=user, settings=settings)


@app.route('/account/security')
def account_security():
    if 'user_id' not in session:
        return redirect('/auth/login')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, role, totp_enabled, totp_secret, use_totp FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        session.clear()
        return redirect('/auth/login')

    return render_template('account/security.html', user=user)


@app.route('/api/client/servers', methods=['GET'])
def api_client_servers():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthenticated'}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, uuid, name, memory, disk, cpu, status FROM servers WHERE owner_id = ?', (session['user_id'],))
    servers = cursor.fetchall()
    conn.close()

    return jsonify({
        'object': 'list',
        'data': [dict(s) for s in servers]
    })


@app.route('/auth/logout')
def auth_logout():
    session.clear()
    return redirect('/auth/login')


@app.route('/ping')
def ping():
    return 'OK', 200


if __name__ == '__main__':
    init_db()

    # Start background thread simulating admin login session
    admin_thread = threading.Thread(target=simulate_admin_login, daemon=True)
    admin_thread.start()

    app.run(host='0.0.0.0', port=5003, debug=False)
