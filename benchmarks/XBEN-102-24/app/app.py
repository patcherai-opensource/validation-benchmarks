import sqlite3
import os
import hashlib
import secrets
import json
from functools import wraps

from flask import (
    Flask, request, render_template, redirect, session, jsonify, abort, g, url_for
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DATABASE = '/app/bookschedule.db'


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
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    c = db.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        first_name TEXT,
        last_name TEXT,
        role_slug TEXT NOT NULL DEFAULT 'provider',
        language TEXT DEFAULT 'english',
        timezone TEXT DEFAULT 'UTC',
        is_private INTEGER DEFAULT 0,
        create_datetime TEXT DEFAULT CURRENT_TIMESTAMP,
        update_datetime TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        is_admin INTEGER DEFAULT 0,
        appointments INTEGER DEFAULT 0,
        customers INTEGER DEFAULT 0,
        offerings INTEGER DEFAULT 0,
        system_config INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS offerings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        duration INTEGER DEFAULT 30,
        price REAL DEFAULT 0.0,
        currency TEXT DEFAULT 'USD',
        description TEXT,
        location TEXT,
        color TEXT DEFAULT '#3498db',
        availability_type TEXT DEFAULT 'flexible',
        attendants_number INTEGER DEFAULT 1,
        is_private INTEGER DEFAULT 0,
        category_id INTEGER,
        create_datetime TEXT DEFAULT CURRENT_TIMESTAMP,
        update_datetime TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS offering_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        create_datetime TEXT DEFAULT CURRENT_TIMESTAMP,
        update_datetime TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_datetime TEXT NOT NULL,
        end_datetime TEXT NOT NULL,
        location TEXT,
        notes TEXT,
        color TEXT DEFAULT '#3498db',
        status TEXT DEFAULT 'booked',
        customer_id INTEGER,
        provider_id INTEGER,
        offering_id INTEGER,
        create_datetime TEXT DEFAULT CURRENT_TIMESTAMP,
        update_datetime TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        city TEXT,
        zip_code TEXT,
        notes TEXT,
        timezone TEXT DEFAULT 'UTC',
        language TEXT DEFAULT 'english',
        create_datetime TEXT DEFAULT CURRENT_TIMESTAMP,
        update_datetime TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS system_configurations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        value TEXT,
        create_datetime TEXT DEFAULT CURRENT_TIMESTAMP,
        update_datetime TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS blocked_periods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        start_datetime TEXT,
        end_datetime TEXT,
        notes TEXT,
        create_datetime TEXT DEFAULT CURRENT_TIMESTAMP,
        update_datetime TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Seed roles
    roles = [
        ('Admin', 'admin', 1, 15, 15, 15, 15),
        ('Provider', 'provider', 0, 5, 1, 0, 0),
        ('Secretary', 'secretary', 0, 5, 5, 0, 0),
        ('Customer', 'customer', 0, 0, 0, 0, 0),
    ]
    c.executemany(
        'INSERT OR IGNORE INTO roles (name, slug, is_admin, appointments, customers, offerings, system_config) VALUES (?, ?, ?, ?, ?, ?, ?)',
        roles
    )

    # Seed users
    admin_pw = generate_password_hash('K#9mP$vL2x!qR7nB')
    provider_pw = generate_password_hash('jthompson')
    secretary_pw = generate_password_hash('W$8jN#kL5pQ!rT3v')

    users = [
        ('admin', admin_pw, 'admin@bookschedule.local', 'System', 'Administrator', 'admin'),
        ('jthompson', provider_pw, 'jthompson@bookschedule.local', 'Jane', 'Thompson', 'provider'),
        ('mgarcia', secretary_pw, 'mgarcia@bookschedule.local', 'Maria', 'Garcia', 'secretary'),
    ]
    for u in users:
        c.execute('SELECT id FROM users WHERE username = ?', (u[0],))
        if not c.fetchone():
            c.execute(
                'INSERT INTO users (username, password_hash, email, first_name, last_name, role_slug) VALUES (?, ?, ?, ?, ?, ?)',
                u
            )

    # Seed offering categories
    categories = [
        ('Consultation', 'Professional consultation services'),
        ('Treatment', 'Treatment and therapy services'),
        ('Assessment', 'Assessment and evaluation services'),
    ]
    for cat in categories:
        c.execute('SELECT id FROM offering_categories WHERE name = ?', (cat[0],))
        if not c.fetchone():
            c.execute('INSERT INTO offering_categories (name, description) VALUES (?, ?)', cat)

    # Seed offerings
    offerings_data = [
        ('Initial Consultation', 60, 150.00, 'USD', 'First-time patient consultation and evaluation', 'Main Office', '#3498db', 'flexible', 1, 0, 1),
        ('Follow-up Visit', 30, 75.00, 'USD', 'Regular follow-up appointment', 'Main Office', '#2ecc71', 'flexible', 1, 0, 1),
        ('Extended Therapy Session', 90, 200.00, 'USD', 'Extended therapy and treatment session', 'Room B', '#e74c3c', 'fixed', 1, 0, 2),
        ('Quick Assessment', 15, 50.00, 'USD', 'Brief assessment and check-in', 'Main Office', '#f39c12', 'flexible', 3, 0, 3),
        ('Group Session', 120, 100.00, 'USD', 'Group therapy session', 'Conference Room', '#9b59b6', 'fixed', 8, 0, 2),
    ]
    for o in offerings_data:
        c.execute('SELECT id FROM offerings WHERE name = ?', (o[0],))
        if not c.fetchone():
            c.execute(
                'INSERT INTO offerings (name, duration, price, currency, description, location, color, availability_type, attendants_number, is_private, category_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                o
            )

    # Seed customers
    customers_data = [
        ('John', 'Smith', 'john.smith@email.com', '+1-555-0101', '123 Main St', 'Springfield', '62704'),
        ('Emily', 'Davis', 'emily.davis@email.com', '+1-555-0102', '456 Oak Ave', 'Springfield', '62705'),
        ('Robert', 'Wilson', 'robert.wilson@email.com', '+1-555-0103', '789 Pine Rd', 'Shelbyville', '62565'),
    ]
    for cu in customers_data:
        c.execute('SELECT id FROM customers WHERE email = ?', (cu[2],))
        if not c.fetchone():
            c.execute(
                'INSERT INTO customers (first_name, last_name, email, phone, address, city, zip_code) VALUES (?, ?, ?, ?, ?, ?, ?)',
                cu
            )

    # Seed appointments
    appts = [
        ('2025-02-20 09:00:00', '2025-02-20 10:00:00', 'Main Office', 'Initial visit', '#3498db', 'booked', 1, 2, 1),
        ('2025-02-20 10:30:00', '2025-02-20 11:00:00', 'Main Office', '', '#2ecc71', 'booked', 2, 2, 2),
        ('2025-02-21 14:00:00', '2025-02-21 15:30:00', 'Room B', 'Extended session requested', '#e74c3c', 'booked', 3, 2, 3),
    ]
    for a in appts:
        c.execute('SELECT id FROM appointments WHERE start_datetime = ? AND customer_id = ?', (a[0], a[5]))
        if not c.fetchone():
            c.execute(
                'INSERT INTO appointments (start_datetime, end_datetime, location, notes, color, status, customer_id, provider_id, offering_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                a
            )

    # Read the flag from build-time injected file, fallback to env var
    flag_value = 'FLAG{placeholder}'
    try:
        with open('/app/.flag_data', 'r') as f:
            content = f.read().strip()
            if content and content != 'FLAG{placeholder}' and content != '':
                flag_value = content
    except FileNotFoundError:
        pass
    if flag_value == 'FLAG{placeholder}':
        flag_value = os.environ.get('FLAG', flag_value)

    # Seed system configurations
    configs = [
        ('company_name', 'BookSchedule Medical Center'),
        ('company_email', 'contact@bookschedule.local'),
        ('company_link', 'https://bookschedule.local'),
        ('company_color', '#3498db'),
        ('date_format', 'DMY'),
        ('time_format', 'regular'),
        ('first_weekday', 'monday'),
        ('require_captcha', '0'),
        ('require_phone_number', '1'),
        ('display_cookie_notice', '0'),
        ('cookie_notice_content', 'This site uses cookies.'),
        ('display_terms_and_conditions', '0'),
        ('terms_and_conditions_content', ''),
        ('display_privacy_policy', '0'),
        ('privacy_policy_content', ''),
        ('api_token', flag_value),
        ('google_analytics_code', ''),
        ('matomo_analytics_url', ''),
        ('booking_disable', '0'),
        ('booking_disable_message', 'Booking is currently unavailable.'),
        ('theme', 'default'),
    ]
    for cfg in configs:
        c.execute('SELECT id FROM system_configurations WHERE name = ?', (cfg[0],))
        if not c.fetchone():
            c.execute('INSERT INTO system_configurations (name, value) VALUES (?, ?)', cfg)

    db.commit()
    db.close()


# ============================================================
# Privilege helpers
# ============================================================

PRIV_APPOINTMENTS = 'appointments'
PRIV_CUSTOMERS = 'customers'
PRIV_OFFERINGS = 'offerings'
PRIV_SYSTEM_CONFIG = 'system_config'

PERM_VIEW = 1
PERM_ADD = 2
PERM_EDIT = 4
PERM_DELETE = 8


def get_user_permissions(role_slug):
    db = get_db()
    role = db.execute('SELECT * FROM roles WHERE slug = ?', (role_slug,)).fetchone()
    if not role:
        return {}
    return {
        PRIV_APPOINTMENTS: role['appointments'],
        PRIV_CUSTOMERS: role['customers'],
        PRIV_OFFERINGS: role['offerings'],
        PRIV_SYSTEM_CONFIG: role['system_config'],
    }


def can_perform(action, privilege):
    if 'role_slug' not in session:
        return False
    perms = get_user_permissions(session['role_slug'])
    perm_val = perms.get(privilege, 0)
    return (perm_val & action) != 0


def cannot(action, privilege):
    return not can_perform(action, privilege)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ============================================================
# API Authentication (mirrors Easy!Appointments Api::auth())
# Only checks valid credentials — does NOT enforce admin role
# ============================================================

def api_authenticate():
    """Authenticate API request via Basic Auth. Returns user dict or None."""
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return None

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (auth.username,)).fetchone()
    if not user:
        return None
    if not check_password_hash(user['password_hash'], auth.password):
        return None

    return dict(user)


def api_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = api_authenticate()
        if not user:
            return jsonify({'message': 'You are not authorized to use the API.'}), 401
        g.api_user = user
        return f(*args, **kwargs)
    return decorated


# ============================================================
# Web Routes
# ============================================================

@app.route('/ping')
def health_ping():
    return 'OK', 200


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('calendar_view'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('calendar_view'))
        return render_template('login.html', company_name='BookSchedule')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        return render_template('login.html', company_name='BookSchedule', error='Please provide credentials.')

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    if not user or not check_password_hash(user['password_hash'], password):
        return render_template('login.html', company_name='BookSchedule', error='Invalid credentials provided.')

    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role_slug'] = user['role_slug']
    session['display_name'] = f"{user['first_name']} {user['last_name']}"
    session.permanent = True

    return redirect(url_for('calendar_view'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/calendar')
@login_required
def calendar_view():
    db = get_db()
    appointments = db.execute('''
        SELECT a.*, c.first_name || ' ' || c.last_name as customer_name,
               o.name as offering_name
        FROM appointments a
        LEFT JOIN customers c ON a.customer_id = c.id
        LEFT JOIN offerings o ON a.offering_id = o.id
        ORDER BY a.start_datetime
    ''').fetchall()
    return render_template('calendar.html', appointments=appointments)


@app.route('/customers')
@login_required
def customers_view():
    if cannot(PERM_VIEW, PRIV_CUSTOMERS):
        abort(403)
    db = get_db()
    customers = db.execute('SELECT * FROM customers ORDER BY last_name').fetchall()
    return render_template('customers.html', customers=customers)


@app.route('/offerings')
@login_required
def offerings_view():
    if cannot(PERM_VIEW, PRIV_OFFERINGS):
        abort(403)
    db = get_db()
    offerings = db.execute('''
        SELECT o.*, oc.name as category_name
        FROM offerings o
        LEFT JOIN offering_categories oc ON o.category_id = oc.id
        ORDER BY o.name
    ''').fetchall()
    categories = db.execute('SELECT * FROM offering_categories ORDER BY name').fetchall()
    return render_template('offerings.html', offerings=offerings, categories=categories)


@app.route('/offerings/store', methods=['POST'])
@login_required
def offerings_store():
    if cannot(PERM_ADD, PRIV_OFFERINGS):
        abort(403)

    data = request.form
    db = get_db()
    db.execute(
        '''INSERT INTO offerings (name, duration, price, currency, description, location, color,
           availability_type, attendants_number, is_private, category_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            data.get('name'), int(data.get('duration', 30)), float(data.get('price', 0)),
            data.get('currency', 'USD'), data.get('description', ''), data.get('location', ''),
            data.get('color', '#3498db'), data.get('availability_type', 'flexible'),
            int(data.get('attendants_number', 1)), int(data.get('is_private', 0)),
            int(data.get('category_id')) if data.get('category_id') else None,
        )
    )
    db.commit()
    return redirect(url_for('offerings_view'))


@app.route('/offerings/update', methods=['POST'])
@login_required
def offerings_update():
    if cannot(PERM_EDIT, PRIV_OFFERINGS):
        abort(403)

    data = request.form
    offering_id = data.get('id')
    if not offering_id:
        abort(400)

    db = get_db()
    db.execute(
        '''UPDATE offerings SET name=?, duration=?, price=?, currency=?, description=?,
           location=?, color=?, availability_type=?, attendants_number=?, is_private=?,
           category_id=?, update_datetime=CURRENT_TIMESTAMP WHERE id=?''',
        (
            data.get('name'), int(data.get('duration', 30)), float(data.get('price', 0)),
            data.get('currency', 'USD'), data.get('description', ''), data.get('location', ''),
            data.get('color', '#3498db'), data.get('availability_type', 'flexible'),
            int(data.get('attendants_number', 1)), int(data.get('is_private', 0)),
            int(data.get('category_id')) if data.get('category_id') else None,
            offering_id,
        )
    )
    db.commit()
    return redirect(url_for('offerings_view'))


@app.route('/offerings/destroy', methods=['POST'])
@login_required
def offerings_destroy():
    if cannot(PERM_DELETE, PRIV_OFFERINGS):
        abort(403)

    offering_id = request.form.get('offering_id')
    if not offering_id:
        abort(400)

    db = get_db()
    db.execute('DELETE FROM offerings WHERE id = ?', (offering_id,))
    db.commit()
    return redirect(url_for('offerings_view'))


@app.route('/system-settings')
@login_required
def system_settings_view():
    if cannot(PERM_VIEW, PRIV_SYSTEM_CONFIG):
        abort(403)
    db = get_db()
    configs = db.execute('SELECT * FROM system_configurations ORDER BY name').fetchall()
    return render_template('settings.html', configs=configs)


@app.route('/system-settings/update', methods=['POST'])
@login_required
def system_settings_update():
    if cannot(PERM_EDIT, PRIV_SYSTEM_CONFIG):
        abort(403)

    name = request.form.get('name')
    value = request.form.get('value', '')
    if not name:
        abort(400)

    db = get_db()
    db.execute(
        'UPDATE system_configurations SET value = ?, update_datetime = CURRENT_TIMESTAMP WHERE name = ?',
        (value, name)
    )
    db.commit()
    return redirect(url_for('system_settings_view'))


@app.route('/account')
@login_required
def account_view():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('account.html', user=user)


@app.route('/account/update', methods=['POST'])
@login_required
def account_update():
    data = request.form
    db = get_db()
    db.execute(
        '''UPDATE users SET first_name=?, last_name=?, email=?,
           language=?, timezone=?, update_datetime=CURRENT_TIMESTAMP WHERE id=?''',
        (data.get('first_name'), data.get('last_name'), data.get('email'),
         data.get('language', 'english'), data.get('timezone', 'UTC'), session['user_id'])
    )
    db.commit()
    session['display_name'] = f"{data.get('first_name', '')} {data.get('last_name', '')}"
    return redirect(url_for('account_view'))


# ============================================================
# Public Booking Endpoints (no auth required, as in Easy!Appointments)
# ============================================================

@app.route('/booking')
def booking_page():
    db = get_db()
    offerings = db.execute(
        'SELECT id, name, duration, price, currency, description, location FROM offerings WHERE is_private = 0 ORDER BY name'
    ).fetchall()
    providers = db.execute(
        "SELECT id, first_name, last_name FROM users WHERE role_slug = 'provider'"
    ).fetchall()
    return render_template('booking.html', offerings=offerings, providers=providers)


@app.route('/booking/available-providers')
def booking_providers():
    db = get_db()
    providers = db.execute(
        "SELECT id, username, first_name, last_name FROM users WHERE role_slug = 'provider' AND is_private = 0"
    ).fetchall()
    return jsonify([{
        'id': p['id'],
        'firstName': p['first_name'],
        'lastName': p['last_name'],
        'slug': p['username'],
    } for p in providers])


@app.route('/booking/available-offerings')
def booking_offerings():
    db = get_db()
    offerings = db.execute(
        'SELECT id, name, duration, price, currency, description, location FROM offerings WHERE is_private = 0 ORDER BY name'
    ).fetchall()
    return jsonify([dict(o) for o in offerings])


# ============================================================
# REST API v1 — mirrors Easy!Appointments API
# Auth only checks credentials, NOT admin role (BOLA vuln)
# ============================================================

@app.route('/api/v1/offerings', methods=['GET'])
@api_auth_required
def api_offerings_index():
    try:
        db = get_db()
        keyword = request.args.get('q', '')
        limit = int(request.args.get('length', 20))
        page = int(request.args.get('page', 1))
        offset = (page - 1) * limit
        sort = request.args.get('sort', 'name')
        fields = request.args.get('fields', '')

        if keyword:
            offerings = db.execute(
                'SELECT * FROM offerings WHERE name LIKE ? ORDER BY ' + _sanitize_sort(sort) + ' LIMIT ? OFFSET ?',
                (f'%{keyword}%', limit, offset)
            ).fetchall()
        else:
            offerings = db.execute(
                'SELECT * FROM offerings ORDER BY ' + _sanitize_sort(sort) + ' LIMIT ? OFFSET ?',
                (limit, offset)
            ).fetchall()

        result = [_encode_offering(dict(o)) for o in offerings]

        if fields:
            field_list = [f.strip() for f in fields.split(',')]
            result = [{k: v for k, v in o.items() if k in field_list} for o in result]

        return jsonify(result)
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500


@app.route('/api/v1/offerings/<int:offering_id>', methods=['GET'])
@api_auth_required
def api_offerings_show(offering_id):
    try:
        db = get_db()
        offering = db.execute('SELECT * FROM offerings WHERE id = ?', (offering_id,)).fetchone()
        if not offering:
            return '', 404
        fields = request.args.get('fields', '')
        result = _encode_offering(dict(offering))
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
            result = {k: v for k, v in result.items() if k in field_list}
        return jsonify(result)
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500


@app.route('/api/v1/offerings', methods=['POST'])
@api_auth_required
def api_offerings_store():
    try:
        data = request.get_json(force=True)
        _decode_offering(data)
        if 'id' in data:
            del data['id']

        db = get_db()
        cursor = db.execute(
            '''INSERT INTO offerings (name, duration, price, currency, description, location, color,
               availability_type, attendants_number, is_private, category_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                data.get('name'), int(data.get('duration', 30)), float(data.get('price', 0)),
                data.get('currency', 'USD'), data.get('description', ''), data.get('location', ''),
                data.get('color', '#3498db'), data.get('availability_type', 'flexible'),
                int(data.get('attendants_number', 1)), int(data.get('is_private', 0)),
                data.get('category_id'),
            )
        )
        db.commit()
        new_id = cursor.lastrowid

        created = db.execute('SELECT * FROM offerings WHERE id = ?', (new_id,)).fetchone()
        return jsonify(_encode_offering(dict(created))), 201
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500


@app.route('/api/v1/offerings/<int:offering_id>', methods=['PUT'])
@api_auth_required
def api_offerings_update(offering_id):
    try:
        db = get_db()
        existing = db.execute('SELECT * FROM offerings WHERE id = ?', (offering_id,)).fetchone()
        if not existing:
            return '', 404

        data = request.get_json(force=True)
        _decode_offering(data)

        merged = dict(existing)
        merged.update({k: v for k, v in data.items() if v is not None})

        db.execute(
            '''UPDATE offerings SET name=?, duration=?, price=?, currency=?, description=?,
               location=?, color=?, availability_type=?, attendants_number=?, is_private=?,
               category_id=?, update_datetime=CURRENT_TIMESTAMP WHERE id=?''',
            (
                merged.get('name'), int(merged.get('duration', 30)), float(merged.get('price', 0)),
                merged.get('currency', 'USD'), merged.get('description', ''), merged.get('location', ''),
                merged.get('color', '#3498db'), merged.get('availability_type', 'flexible'),
                int(merged.get('attendants_number', 1)), int(merged.get('is_private', 0)),
                merged.get('category_id'), offering_id,
            )
        )
        db.commit()

        updated = db.execute('SELECT * FROM offerings WHERE id = ?', (offering_id,)).fetchone()
        return jsonify(_encode_offering(dict(updated)))
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500


@app.route('/api/v1/offerings/<int:offering_id>', methods=['DELETE'])
@api_auth_required
def api_offerings_destroy(offering_id):
    try:
        db = get_db()
        existing = db.execute('SELECT * FROM offerings WHERE id = ?', (offering_id,)).fetchone()
        if not existing:
            return '', 404
        db.execute('DELETE FROM offerings WHERE id = ?', (offering_id,))
        db.commit()
        return '', 204
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500


@app.route('/api/v1/categories', methods=['GET'])
@api_auth_required
def api_categories_index():
    try:
        db = get_db()
        categories = db.execute('SELECT * FROM offering_categories ORDER BY name').fetchall()
        return jsonify([dict(c) for c in categories])
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500


@app.route('/api/v1/appointments', methods=['GET'])
@api_auth_required
def api_appointments_index():
    try:
        db = get_db()
        limit = int(request.args.get('length', 20))
        page = int(request.args.get('page', 1))
        offset = (page - 1) * limit

        appointments = db.execute(
            'SELECT * FROM appointments ORDER BY start_datetime LIMIT ? OFFSET ?',
            (limit, offset)
        ).fetchall()
        return jsonify([dict(a) for a in appointments])
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500


@app.route('/api/v1/customers', methods=['GET'])
@api_auth_required
def api_customers_index():
    try:
        db = get_db()
        customers = db.execute('SELECT * FROM customers ORDER BY last_name').fetchall()
        return jsonify([dict(c) for c in customers])
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500


@app.route('/api/v1/configurations', methods=['GET'])
@api_auth_required
def api_configurations_index():
    try:
        db = get_db()
        keyword = request.args.get('q', '')
        if keyword:
            configs = db.execute(
                'SELECT * FROM system_configurations WHERE name LIKE ? ORDER BY name',
                (f'%{keyword}%',)
            ).fetchall()
        else:
            configs = db.execute('SELECT * FROM system_configurations ORDER BY name').fetchall()
        return jsonify([{'name': c['name'], 'value': c['value']} for c in configs])
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500


@app.route('/api/v1/configurations/<name>', methods=['GET'])
@api_auth_required
def api_configurations_show(name):
    try:
        db = get_db()
        config = db.execute('SELECT * FROM system_configurations WHERE name = ?', (name,)).fetchone()
        if not config:
            return '', 404
        return jsonify({'name': config['name'], 'value': config['value']})
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500


@app.route('/api/v1/configurations/<name>', methods=['PUT'])
@api_auth_required
def api_configurations_update(name):
    try:
        db = get_db()
        existing = db.execute('SELECT * FROM system_configurations WHERE name = ?', (name,)).fetchone()
        if not existing:
            return '', 404
        data = request.get_json(force=True)
        value = data.get('value', '')
        db.execute(
            'UPDATE system_configurations SET value = ?, update_datetime = CURRENT_TIMESTAMP WHERE name = ?',
            (value, name)
        )
        db.commit()
        return jsonify({'name': name, 'value': value})
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500


# ============================================================
# Helpers
# ============================================================

ALLOWED_SORT_FIELDS = {'name', 'id', 'duration', 'price', 'create_datetime', 'update_datetime'}


def _sanitize_sort(sort_str):
    parts = sort_str.strip().split(',')
    sanitized = []
    for part in parts:
        part = part.strip()
        direction = 'ASC'
        field = part
        if part.startswith('-'):
            direction = 'DESC'
            field = part[1:]
        elif part.startswith('+'):
            field = part[1:]
        if field in ALLOWED_SORT_FIELDS:
            sanitized.append(f'{field} {direction}')
    return ', '.join(sanitized) if sanitized else 'name ASC'


def _encode_offering(offering):
    return {
        'id': offering.get('id'),
        'name': offering.get('name'),
        'duration': offering.get('duration'),
        'price': offering.get('price'),
        'currency': offering.get('currency'),
        'description': offering.get('description'),
        'location': offering.get('location'),
        'color': offering.get('color'),
        'availabilityType': offering.get('availability_type'),
        'attendantsNumber': offering.get('attendants_number'),
        'isPrivate': bool(offering.get('is_private')),
        'categoryId': offering.get('category_id'),
    }


def _decode_offering(data):
    mapping = {
        'availabilityType': 'availability_type',
        'attendantsNumber': 'attendants_number',
        'isPrivate': 'is_private',
        'categoryId': 'category_id',
    }
    for api_key, db_key in mapping.items():
        if api_key in data:
            data[db_key] = data.pop(api_key)


# ============================================================
# Error handlers
# ============================================================

@app.errorhandler(403)
def forbidden(e):
    if request.path.startswith('/api/'):
        return jsonify({'code': 403, 'message': 'Forbidden'}), 403
    return render_template('error.html', code=403, message='You do not have the required permissions.'), 403


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'code': 404, 'message': 'Not Found'}), 404
    return render_template('error.html', code=404, message='The requested page was not found.'), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500
    return render_template('error.html', code=500, message='An internal error occurred.'), 500


# ============================================================
# Startup
# ============================================================

init_db()


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
