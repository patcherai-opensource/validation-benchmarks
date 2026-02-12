import sqlite3
import os
import threading
import time
import logging

import requests as http_requests
from flask import Flask, request, render_template, redirect, session, url_for, abort, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

DB_PATH = '/app/modoboa.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    flag = open('/app/.admin_notes', 'r').read().strip() if os.path.exists('/app/.admin_notes') else 'FLAG{placeholder}'

    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS core_user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT DEFAULT '',
        last_name TEXT DEFAULT '',
        email TEXT DEFAULT '',
        role TEXT DEFAULT 'SimpleUsers',
        is_active INTEGER DEFAULT 1,
        language TEXT DEFAULT 'en',
        phone_number TEXT DEFAULT '',
        secondary_email TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        profile_public INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS admin_domain (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        quota INTEGER DEFAULT 0,
        enabled INTEGER DEFAULT 1,
        created_by_id INTEGER,
        default_mailbox_quota INTEGER DEFAULT 10,
        transport TEXT DEFAULT 'relay',
        FOREIGN KEY (created_by_id) REFERENCES core_user(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS admin_mailbox (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT NOT NULL,
        domain_id INTEGER,
        user_id INTEGER,
        quota INTEGER DEFAULT 10,
        use_domain_quota INTEGER DEFAULT 1,
        FOREIGN KEY (domain_id) REFERENCES admin_domain(id),
        FOREIGN KEY (user_id) REFERENCES core_user(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS admin_alias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT NOT NULL,
        domain_id INTEGER,
        enabled INTEGER DEFAULT 1,
        FOREIGN KEY (domain_id) REFERENCES admin_domain(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submitted_by_id INTEGER,
        url TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (submitted_by_id) REFERENCES core_user(id)
    )''')

    # Seed initial data
    users = [
        ('admin', 'S3cur3P@ssw0rd!', 'Admin', 'User', 'admin@example.com',
         'SuperAdmins', 1, 'en', '', '', flag, 0),
        ('postmaster@example.com', 'Pm@st3r2024', 'Postmaster', 'Account',
         'postmaster@example.com', 'DomainAdmins', 1, 'en', '', '', '', 0),
        ('user@example.com', 'ChangeMe123', 'Regular', 'User',
         'user@example.com', 'SimpleUsers', 1, 'en', '', '', '', 0),
    ]
    for u in users:
        c.execute('''INSERT OR IGNORE INTO core_user 
            (username, password, first_name, last_name, email, role, is_active, language, phone_number, secondary_email, notes, profile_public)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', u)

    domains = [
        ('example.com', 100, 1, 1, 10, 'relay'),
        ('mail.example.com', 50, 1, 1, 5, 'relay'),
    ]
    for d in domains:
        c.execute('''INSERT OR IGNORE INTO admin_domain
            (name, quota, enabled, created_by_id, default_mailbox_quota, transport)
            VALUES (?, ?, ?, ?, ?, ?)''', d)

    mailboxes = [
        ('admin', 1, 1, 50, 0),
        ('postmaster', 1, 2, 10, 1),
        ('user', 1, 3, 10, 1),
    ]
    for m in mailboxes:
        c.execute('''INSERT OR IGNORE INTO admin_mailbox
            (address, domain_id, user_id, quota, use_domain_quota)
            VALUES (?, ?, ?, ?, ?)''', m)

    aliases = [
        ('abuse@example.com', 1, 1),
        ('noreply@example.com', 1, 1),
    ]
    for a in aliases:
        c.execute('''INSERT OR IGNORE INTO admin_alias
            (address, domain_id, enabled)
            VALUES (?, ?, ?)''', a)

    conn.commit()
    conn.close()


init_db()


def require_login(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') not in ('SuperAdmins', 'DomainAdmins'):
            abort(403)
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    if 'user_id' not in session:
        return None
    conn = get_db()
    user = conn.execute('SELECT * FROM core_user WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return user


# ---- Public routes ----

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM core_user WHERE username = ? AND password = ? AND is_active = 1',
            (username, password)
        ).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        error = 'Invalid credentials.'
    return render_template('login.html', error=error)


@app.route('/new_account/', methods=['GET', 'POST'])
def new_account():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()

        if not username or not password:
            error = 'Username and password are required.'
        else:
            conn = get_db()
            existing = conn.execute('SELECT id FROM core_user WHERE username = ?', (username,)).fetchone()
            if existing:
                error = 'Username already exists.'
                conn.close()
            else:
                conn.execute(
                    '''INSERT INTO core_user (username, password, first_name, last_name, email, role, is_active)
                       VALUES (?, ?, ?, ?, ?, 'SimpleUsers', 1)''',
                    (username, password, first_name, last_name, email)
                )
                conn.commit()
                conn.close()
                return redirect(url_for('login'))

    return render_template('new_account.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---- Dashboard ----

@app.route('/dashboard')
@require_login
def dashboard():
    user = get_current_user()
    conn = get_db()
    stats = {}
    if session.get('role') in ('SuperAdmins', 'DomainAdmins'):
        stats['domains'] = conn.execute('SELECT COUNT(*) FROM admin_domain').fetchone()[0]
        stats['accounts'] = conn.execute('SELECT COUNT(*) FROM core_user').fetchone()[0]
        stats['mailboxes'] = conn.execute('SELECT COUNT(*) FROM admin_mailbox').fetchone()[0]
        stats['aliases'] = conn.execute('SELECT COUNT(*) FROM admin_alias').fetchone()[0]
    conn.close()
    return render_template('dashboard.html', user=user, stats=stats)


# ---- Admin: Domains ----

@app.route('/admin/domains/')
@require_admin
def list_domains():
    conn = get_db()
    domains = conn.execute('SELECT * FROM admin_domain').fetchall()
    conn.close()
    return render_template('domains.html', domains=domains)


@app.route('/admin/domains/<int:dom_id>/')
@require_admin
def domain_detail(dom_id):
    conn = get_db()
    domain = conn.execute('SELECT * FROM admin_domain WHERE id = ?', (dom_id,)).fetchone()
    if not domain:
        conn.close()
        abort(404)
    mailboxes = conn.execute(
        'SELECT m.*, u.username, u.email FROM admin_mailbox m JOIN core_user u ON m.user_id = u.id WHERE m.domain_id = ?',
        (dom_id,)
    ).fetchall()
    aliases = conn.execute('SELECT * FROM admin_alias WHERE domain_id = ?', (dom_id,)).fetchall()
    conn.close()
    return render_template('domain_detail.html', domain=domain, mailboxes=mailboxes, aliases=aliases)


@app.route('/admin/domains/<int:dom_id>/edit/')
@require_admin
def editdomain(dom_id):
    conn = get_db()
    domain = conn.execute('SELECT * FROM admin_domain WHERE id = ?', (dom_id,)).fetchone()
    if not domain:
        conn.close()
        abort(404)

    name = request.args.get('name', domain['name'])
    quota = request.args.get('quota', domain['quota'])
    enabled = request.args.get('enabled', domain['enabled'])
    transport = request.args.get('transport', domain['transport'])

    conn.execute(
        'UPDATE admin_domain SET name = ?, quota = ?, enabled = ?, transport = ? WHERE id = ?',
        (name, quota, enabled, transport, dom_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('domain_detail', dom_id=dom_id))


# ---- Admin: Accounts ----

@app.route('/admin/accounts/')
@require_admin
def list_accounts():
    conn = get_db()
    accounts = conn.execute('SELECT * FROM core_user').fetchall()
    conn.close()
    return render_template('accounts.html', accounts=accounts)


@app.route('/admin/accounts/<int:pk>/')
@require_admin
def account_detail(pk):
    conn = get_db()
    account = conn.execute('SELECT * FROM core_user WHERE id = ?', (pk,)).fetchone()
    if not account:
        conn.close()
        abort(404)
    conn.close()
    return render_template('account_detail.html', account=account)


@app.route('/admin/accounts/<int:pk>/edit/')
@require_admin
def editaccount(pk):
    conn = get_db()
    account = conn.execute('SELECT * FROM core_user WHERE id = ?', (pk,)).fetchone()
    if not account:
        conn.close()
        abort(404)

    first_name = request.args.get('first_name', account['first_name'])
    last_name = request.args.get('last_name', account['last_name'])
    email = request.args.get('email', account['email'])
    role = request.args.get('role', account['role'])
    secondary_email = request.args.get('secondary_email', account['secondary_email'])
    phone_number = request.args.get('phone_number', account['phone_number'])
    language = request.args.get('language', account['language'])
    profile_public = request.args.get('profile_public', account['profile_public'])

    conn.execute(
        '''UPDATE core_user SET first_name=?, last_name=?, email=?, role=?,
           secondary_email=?, phone_number=?, language=?, profile_public=?
           WHERE id=?''',
        (first_name, last_name, email, role, secondary_email, phone_number,
         language, profile_public, pk)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('account_detail', pk=pk))


# ---- Public profiles ----

@app.route('/accounts/<int:pk>/profile/')
def public_profile(pk):
    conn = get_db()
    account = conn.execute('SELECT * FROM core_user WHERE id = ?', (pk,)).fetchone()
    if not account:
        conn.close()
        abort(404)
    if not int(account['profile_public']):
        conn.close()
        return render_template('profile_private.html'), 403
    conn.close()
    return render_template('public_profile.html', account=account)


# ---- Support ticket / URL report (admin bot) ----

def admin_bot_visit(url, ticket_id):
    """Simulate an admin reviewing a reported URL by visiting it."""
    time.sleep(2)
    try:
        s = http_requests.Session()
        base = 'http://127.0.0.1:8000'
        # Admin logs in
        s.post(f'{base}/login', data={
            'username': 'admin',
            'password': 'S3cur3P@ssw0rd!'
        }, allow_redirects=True)
        # Admin visits the reported URL
        # Only allow URLs on the same host for security
        if url.startswith('/'):
            visit_url = base + url
        elif url.startswith(base):
            visit_url = url
        else:
            visit_url = url
        s.get(visit_url, timeout=10)
        conn = get_db()
        conn.execute('UPDATE support_tickets SET status = ? WHERE id = ?', ('reviewed', ticket_id))
        conn.commit()
        conn.close()
    except Exception:
        pass


@app.route('/support/')
@require_login
def support_page():
    conn = get_db()
    tickets = conn.execute(
        'SELECT * FROM support_tickets WHERE submitted_by_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('support.html', tickets=tickets)


@app.route('/support/report/', methods=['POST'])
@require_login
def report_url():
    url = request.form.get('url', '').strip()
    if not url:
        return redirect(url_for('support_page'))

    conn = get_db()
    c = conn.cursor()
    c.execute(
        'INSERT INTO support_tickets (submitted_by_id, url) VALUES (?, ?)',
        (session['user_id'], url)
    )
    ticket_id = c.lastrowid
    conn.commit()
    conn.close()

    # Start admin bot in background
    t = threading.Thread(target=admin_bot_visit, args=(url, ticket_id), daemon=True)
    t.start()

    return redirect(url_for('support_page'))


# ---- API endpoints for domain stats ----

@app.route('/api/v1/domains/')
@require_login
def api_domains():
    if session.get('role') not in ('SuperAdmins', 'DomainAdmins'):
        return jsonify({'error': 'Forbidden'}), 403
    conn = get_db()
    domains = conn.execute('SELECT id, name, quota, enabled FROM admin_domain').fetchall()
    conn.close()
    return jsonify([dict(d) for d in domains])


@app.route('/api/v1/accounts/')
@require_login
def api_accounts():
    if session.get('role') not in ('SuperAdmins', 'DomainAdmins'):
        return jsonify({'error': 'Forbidden'}), 403
    conn = get_db()
    accounts = conn.execute(
        'SELECT id, username, email, role, is_active FROM core_user'
    ).fetchall()
    conn.close()
    return jsonify([dict(a) for a in accounts])


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access denied.'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error.'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000, threaded=True)
