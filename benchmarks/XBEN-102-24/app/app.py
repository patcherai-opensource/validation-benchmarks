import sqlite3
import os
import hashlib
import threading
import time

import requests
from flask import (
    Flask, request, render_template, redirect, session, url_for,
    jsonify, g, abort
)

app = Flask(__name__)
app.secret_key = hashlib.sha256(os.urandom(32)).hexdigest()

DB_PATH = '/app/data/mailadmin.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH, timeout=30)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA journal_mode=WAL')
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'SimpleUser',
        is_active INTEGER DEFAULT 1,
        first_name TEXT DEFAULT '',
        last_name TEXT DEFAULT '',
        language TEXT DEFAULT 'en',
        phone_number TEXT DEFAULT '',
        secondary_email TEXT DEFAULT ''
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS mail_domains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        quota INTEGER DEFAULT 0,
        default_mailbox_quota INTEGER DEFAULT 0,
        message_limit INTEGER DEFAULT NULL,
        enabled INTEGER DEFAULT 1,
        domain_type TEXT DEFAULT 'domain',
        enable_dns_checks INTEGER DEFAULT 1,
        created_by INTEGER,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS mailboxes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT NOT NULL,
        domain_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        quota INTEGER DEFAULT 0,
        enabled INTEGER DEFAULT 1,
        FOREIGN KEY (domain_id) REFERENCES mail_domains(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS mail_aliases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT NOT NULL,
        domain_id INTEGER NOT NULL,
        enabled INTEGER DEFAULT 1,
        FOREIGN KEY (domain_id) REFERENCES mail_domains(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS alias_recipients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alias_id INTEGER NOT NULL,
        address TEXT NOT NULL,
        FOREIGN KEY (alias_id) REFERENCES mail_aliases(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS domain_admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (domain_id) REFERENCES mail_domains(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS system_config (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    admin_pw = hashlib.sha256('Modoboa1!'.encode()).hexdigest()
    postmaster_pw = hashlib.sha256('password'.encode()).hexdigest()
    user_pw = hashlib.sha256('changeme'.encode()).hexdigest()

    flag = 'FLAG{placeholder}'

    c.execute('''INSERT OR IGNORE INTO users
        (username, password_hash, role, first_name, last_name, secondary_email)
        VALUES (?, ?, 'SuperAdmin', 'System', 'Administrator', 'admin-backup@internal.local')''',
        ('admin', admin_pw))

    c.execute('''INSERT OR IGNORE INTO users
        (username, password_hash, role, first_name, last_name)
        VALUES (?, ?, 'DomainAdmin', 'Post', 'Master')''',
        ('postmaster', postmaster_pw))

    c.execute('''INSERT OR IGNORE INTO users
        (username, password_hash, role, first_name, last_name)
        VALUES (?, ?, 'SimpleUser', 'John', 'Doe')''',
        ('user', user_pw))

    c.execute('''INSERT OR IGNORE INTO mail_domains
        (name, quota, default_mailbox_quota, enabled, created_by)
        VALUES ('example.com', 10240, 1024, 1, 1)''')

    c.execute('''INSERT OR IGNORE INTO mail_domains
        (name, quota, default_mailbox_quota, enabled, created_by)
        VALUES ('internal.local', 5120, 512, 1, 1)''')

    c.execute('''INSERT OR REPLACE INTO system_config VALUES ('admin_secret_token', ?)''', (flag,))
    c.execute('''INSERT OR REPLACE INTO system_config VALUES ('smtp_relay', 'relay.internal.local')''')
    c.execute('''INSERT OR REPLACE INTO system_config VALUES ('default_language', 'en')''')
    c.execute('''INSERT OR REPLACE INTO system_config VALUES ('handle_mailboxes', 'yes')''')
    c.execute('''INSERT OR REPLACE INTO system_config VALUES ('auto_account_removal', 'no')''')
    c.execute('''INSERT OR REPLACE INTO system_config VALUES ('enable_mx_checks', 'yes')''')

    conn.commit()
    conn.close()


init_db()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_current_user():
    if 'user_id' not in session:
        return None
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return user


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return redirect(url_for('login'))
        g.user = user
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return redirect(url_for('login'))
        if user['role'] not in ('SuperAdmin', 'DomainAdmin'):
            abort(403)
        g.user = user
        return f(*args, **kwargs)
    return decorated


def superadmin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return redirect(url_for('login'))
        if user['role'] != 'SuperAdmin':
            abort(403)
        g.user = user
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def root():
    user = get_current_user()
    if user:
        if user['role'] in ('SuperAdmin', 'DomainAdmin'):
            return redirect(url_for('dashboard'))
        return redirect(url_for('user_settings'))
    return redirect(url_for('login'))


@app.route('/ping')
def ping():
    return 'OK', 200


@app.route('/accounts/login/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ? AND password_hash = ? AND is_active = 1',
            (username, hash_password(password))
        ).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            if user['role'] in ('SuperAdmin', 'DomainAdmin'):
                return redirect(url_for('dashboard'))
            return redirect(url_for('user_settings'))
        error = 'Invalid credentials.'
    return render_template('accounts/login.html', error=error)


@app.route('/accounts/logout/', methods=['POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard/')
@admin_required
def dashboard():
    db = get_db()
    domains = db.execute('SELECT COUNT(*) as cnt FROM mail_domains').fetchone()
    mailboxes = db.execute('SELECT COUNT(*) as cnt FROM mailboxes').fetchone()
    accounts = db.execute('SELECT COUNT(*) as cnt FROM users').fetchone()
    aliases = db.execute('SELECT COUNT(*) as cnt FROM mail_aliases').fetchone()
    return render_template('admin/dashboard.html',
        domain_count=domains['cnt'],
        mailbox_count=mailboxes['cnt'],
        account_count=accounts['cnt'],
        alias_count=aliases['cnt'],
        user=g.user
    )


@app.route('/admin/domains/')
@admin_required
def domain_list():
    db = get_db()
    domains = db.execute('SELECT * FROM mail_domains ORDER BY name').fetchall()
    return render_template('admin/domains.html', domains=domains, user=g.user)


@app.route('/admin/domains/<int:dom_id>/')
@admin_required
def domain_detail(dom_id):
    db = get_db()
    domain = db.execute('SELECT * FROM mail_domains WHERE id = ?', (dom_id,)).fetchone()
    if not domain:
        abort(404)
    mailboxes = db.execute(
        'SELECT m.*, u.username FROM mailboxes m JOIN users u ON m.user_id = u.id WHERE m.domain_id = ?',
        (dom_id,)
    ).fetchall()
    aliases = db.execute('SELECT * FROM mail_aliases WHERE domain_id = ?', (dom_id,)).fetchall()
    return render_template('admin/domain_detail.html',
        domain=domain, mailboxes=mailboxes, aliases=aliases, user=g.user)


@app.route('/admin/domains/<int:dom_id>/modify/')
@admin_required
def modify_domain(dom_id):
    """Modify domain settings."""
    db = get_db()
    domain = db.execute('SELECT * FROM mail_domains WHERE id = ?', (dom_id,)).fetchone()
    if not domain:
        abort(404)

    name = request.args.get('name', domain['name'])
    quota = request.args.get('quota', domain['quota'])
    default_mailbox_quota = request.args.get('default_mailbox_quota', domain['default_mailbox_quota'])
    enabled = request.args.get('enabled', domain['enabled'])
    message_limit = request.args.get('message_limit', domain['message_limit'])

    try:
        quota = int(quota)
        default_mailbox_quota = int(default_mailbox_quota)
        enabled = int(enabled) if str(enabled) in ('0', '1') else domain['enabled']
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid parameter values'}), 400

    db.execute(
        '''UPDATE mail_domains SET name=?, quota=?, default_mailbox_quota=?,
           enabled=?, message_limit=? WHERE id=?''',
        (name, quota, default_mailbox_quota, enabled, message_limit, dom_id)
    )
    db.commit()
    return redirect(url_for('domain_detail', dom_id=dom_id))


@app.route('/admin/identities/')
@admin_required
def identity_list():
    db = get_db()
    users = db.execute('SELECT * FROM users ORDER BY username').fetchall()
    return render_template('admin/identities.html', users=users, user=g.user)


@app.route('/admin/identities/<int:pk>/')
@admin_required
def account_detail(pk):
    db = get_db()
    account = db.execute('SELECT * FROM users WHERE id = ?', (pk,)).fetchone()
    if not account:
        abort(404)
    return render_template('admin/account_detail.html', account=account, user=g.user)


@app.route('/admin/identities/<int:pk>/modify/')
@superadmin_required
def modify_account(pk):
    """Modify account settings."""
    db = get_db()
    account = db.execute('SELECT * FROM users WHERE id = ?', (pk,)).fetchone()
    if not account:
        abort(404)

    username = request.args.get('username', account['username'])
    first_name = request.args.get('first_name', account['first_name'])
    last_name = request.args.get('last_name', account['last_name'])
    role = request.args.get('role', account['role'])
    is_active = request.args.get('is_active', account['is_active'])
    secondary_email = request.args.get('secondary_email', account['secondary_email'])

    if role not in ('SuperAdmin', 'DomainAdmin', 'SimpleUser'):
        role = account['role']

    try:
        is_active = int(is_active) if str(is_active) in ('0', '1') else account['is_active']
    except (ValueError, TypeError):
        is_active = account['is_active']

    db.execute(
        '''UPDATE users SET username=?, first_name=?, last_name=?,
           role=?, is_active=?, secondary_email=? WHERE id=?''',
        (username, first_name, last_name, role, is_active, secondary_email, pk)
    )
    db.commit()
    return redirect(url_for('account_detail', pk=pk))


@app.route('/admin/settings/')
@superadmin_required
def system_settings():
    db = get_db()
    configs = db.execute(
        "SELECT key, value FROM system_config"
    ).fetchall()
    return render_template('admin/settings.html', configs=configs, user=g.user)


@app.route('/api/v1/domains/')
@admin_required
def api_domain_list():
    db = get_db()
    domains = db.execute('SELECT id, name, enabled FROM mail_domains ORDER BY name').fetchall()
    return jsonify([{'id': d['id'], 'name': d['name'], 'enabled': bool(d['enabled'])} for d in domains])


@app.route('/api/v1/accounts/')
@admin_required
def api_account_list():
    db = get_db()
    accounts = db.execute('SELECT id, username, role, is_active FROM users ORDER BY username').fetchall()
    return jsonify([{
        'id': a['id'], 'username': a['username'],
        'role': a['role'], 'is_active': bool(a['is_active'])
    } for a in accounts])


@app.route('/user/settings/', methods=['GET', 'POST'])
@login_required
def user_settings():
    db = get_db()
    if request.method == 'POST':
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        language = request.form.get('language', 'en')
        phone_number = request.form.get('phone_number', '')
        db.execute(
            'UPDATE users SET first_name=?, last_name=?, language=?, phone_number=? WHERE id=?',
            (first_name, last_name, language, phone_number, g.user['id'])
        )
        db.commit()
        return redirect(url_for('user_settings'))
    user_data = db.execute('SELECT * FROM users WHERE id = ?', (g.user['id'],)).fetchone()
    return render_template('user/settings.html', user_data=user_data, user=g.user)


@app.route('/admin/report/', methods=['GET', 'POST'])
@login_required
def report_url():
    """Report a URL for admin review - admin will visit reported URLs."""
    message = None
    if request.method == 'POST':
        reported_path = request.form.get('url', '')
        if reported_path:
            if not reported_path.startswith('/'):
                reported_path = '/' + reported_path
            threading.Thread(
                target=simulate_admin_visit, args=(reported_path,), daemon=True
            ).start()
            message = 'URL has been submitted for admin review.'
    return render_template('admin/report.html', message=message, user=g.user)


def simulate_admin_visit(path):
    """Simulate an admin visiting the reported path."""
    base = 'http://127.0.0.1:8000'
    time.sleep(2)
    try:
        sess = requests.Session()
        sess.get(base + '/accounts/login/')
        sess.post(base + '/accounts/login/', data={
            'username': 'admin',
            'password': 'Modoboa1!'
        }, allow_redirects=False)
        sess.get(base + path, timeout=10)
    except Exception:
        pass


@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000, threaded=True)
