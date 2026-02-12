from flask import Flask, request, render_template, redirect, session, jsonify, g
from functools import wraps
import sqlite3
import os
import hashlib
import json

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

DATABASE = 'easyappointments.db'

# Privilege constants matching Easy!Appointments
PRIV_USERS = 'users'
PRIV_SERVICES = 'services'
PRIV_APPOINTMENTS = 'appointments'
PRIV_CUSTOMERS = 'customers'
PRIV_SYSTEM_SETTINGS = 'system_settings'

# Role constants
ROLE_ADMIN = 'admin'
ROLE_PROVIDER = 'provider'
ROLE_SECRETARY = 'secretary'
ROLE_CUSTOMER = 'customer'


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


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS ea_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer',
            id_roles INTEGER NOT NULL DEFAULT 4,
            timezone TEXT DEFAULT 'UTC',
            language TEXT DEFAULT 'english',
            notifications INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS ea_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            duration INTEGER NOT NULL DEFAULT 30,
            price REAL DEFAULT 0.00,
            currency TEXT DEFAULT 'USD',
            description TEXT,
            color TEXT DEFAULT '#7cbae8',
            availabilities_type TEXT DEFAULT 'flexible',
            attendants_number INTEGER DEFAULT 1,
            is_private INTEGER DEFAULT 0,
            id_categories INTEGER DEFAULT NULL,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES ea_users(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS ea_services_providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_users INTEGER NOT NULL,
            id_services INTEGER NOT NULL,
            FOREIGN KEY (id_users) REFERENCES ea_users(id),
            FOREIGN KEY (id_services) REFERENCES ea_services(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS ea_appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_datetime TEXT NOT NULL,
            end_datetime TEXT NOT NULL,
            notes TEXT,
            hash TEXT,
            is_unavailability INTEGER DEFAULT 0,
            id_users_provider INTEGER,
            id_users_customer INTEGER,
            id_services INTEGER,
            id_google_calendar TEXT,
            FOREIGN KEY (id_users_provider) REFERENCES ea_users(id),
            FOREIGN KEY (id_users_customer) REFERENCES ea_users(id),
            FOREIGN KEY (id_services) REFERENCES ea_services(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS ea_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS ea_service_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS ea_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            appointments INTEGER DEFAULT 0,
            customers INTEGER DEFAULT 0,
            services INTEGER DEFAULT 0,
            users INTEGER DEFAULT 0,
            system_settings INTEGER DEFAULT 0
        )
    ''')

    # Insert default roles
    default_roles = [
        (1, 'Administrator', 'admin', 1, 1, 1, 1, 1, 1),
        (2, 'Provider', 'provider', 0, 1, 1, 0, 0, 0),
        (3, 'Secretary', 'secretary', 0, 1, 1, 0, 0, 0),
        (4, 'Customer', 'customer', 0, 0, 0, 0, 0, 0),
    ]
    c.executemany(
        'INSERT OR IGNORE INTO ea_roles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        default_roles
    )

    # Read flag from file (planted at build time)
    flag_value = 'FLAG{placeholder}'
    try:
        with open('/app/.flag_config', 'r') as f:
            flag_value = f.read().strip()
    except FileNotFoundError:
        pass

    # Insert application settings
    settings = [
        ('company_name', 'Easy!Appointments'),
        ('company_email', 'info@easyappointments.org'),
        ('company_link', 'https://easyappointments.org'),
        ('company_working_plan', '{"monday":{"start":"09:00","end":"18:00","breaks":[{"start":"12:00","end":"13:00"}]},"tuesday":{"start":"09:00","end":"18:00","breaks":[{"start":"12:00","end":"13:00"}]},"wednesday":{"start":"09:00","end":"18:00","breaks":[{"start":"12:00","end":"13:00"}]},"thursday":{"start":"09:00","end":"18:00","breaks":[{"start":"12:00","end":"13:00"}]},"friday":{"start":"09:00","end":"18:00","breaks":[{"start":"12:00","end":"13:00"}]},"saturday":null,"sunday":null}'),
        ('date_format', 'DMY'),
        ('time_format', 'regular'),
        ('display_cookie_notice', '0'),
        ('cookie_notice_content', 'Cookie notice content.'),
        ('display_terms_content', '0'),
        ('terms_content', 'Terms and conditions content.'),
        ('display_privacy_policy', '0'),
        ('privacy_policy_content', 'Privacy policy content.'),
        ('api_token', flag_value),
        ('google_sync', '0'),
        ('google_token', ''),
        ('require_captcha', '0'),
        ('require_phone_number', '1'),
        ('display_any_provider', '1'),
    ]
    for name, value in settings:
        c.execute('INSERT OR IGNORE INTO ea_settings (name, value) VALUES (?, ?)', (name, value))

    # Create admin user
    admin_pass = hash_password('easyappts_admin_2024')
    c.execute('''INSERT OR IGNORE INTO ea_users 
                 (first_name, last_name, email, username, password, role, id_roles) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              ('John', 'Admin', 'admin@easyappointments.org', 'admin', admin_pass, 'admin', 1))

    # Create provider user
    provider_pass = hash_password('provider123')
    c.execute('''INSERT OR IGNORE INTO ea_users 
                 (first_name, last_name, email, username, password, role, id_roles) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              ('Jane', 'Smith', 'jane@easyappointments.org', 'jsmith', provider_pass, 'provider', 2))

    # Create a default service
    c.execute('''INSERT OR IGNORE INTO ea_services 
                 (id, name, duration, price, currency, description, color, created_by)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (1, 'General Consultation', 30, 50.00, 'USD', 'Standard consultation service', '#7cbae8', 1))

    # Create some categories
    c.execute('INSERT OR IGNORE INTO ea_service_categories (id, name, description) VALUES (?, ?, ?)',
              (1, 'General', 'General services'))
    c.execute('INSERT OR IGNORE INTO ea_service_categories (id, name, description) VALUES (?, ?, ?)',
              (2, 'Specialized', 'Specialized services'))

    # Link provider to service
    c.execute('INSERT OR IGNORE INTO ea_services_providers (id, id_users, id_services) VALUES (?, ?, ?)',
              (1, 2, 1))

    # Create some sample appointments
    c.execute('''INSERT OR IGNORE INTO ea_appointments 
                 (id, start_datetime, end_datetime, notes, hash, id_users_provider, id_users_customer, id_services)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (1, '2024-03-15 09:00:00', '2024-03-15 09:30:00', 'Initial consultation', 
               hashlib.md5(b'appt1').hexdigest(), 2, None, 1))

    conn.commit()
    conn.close()


init_db()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/user/login')
        return f(*args, **kwargs)
    return decorated


def can(user_id, action, privilege_type):
    """Check if user has a specific privilege - mirrors Easy!Appointments privilege system."""
    db = get_db()
    user = db.execute('SELECT id_roles, role FROM ea_users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        return False

    if user['role'] == ROLE_ADMIN:
        return True

    role = db.execute('SELECT * FROM ea_roles WHERE id = ?', (user['id_roles'],)).fetchone()
    if not role:
        return False

    if privilege_type in dict(role).keys():
        return role[privilege_type] >= 1
    return False


def cannot(user_id, action, privilege_type):
    """Inverse of can() - mirrors Easy!Appointments cannot() method."""
    return not can(user_id, action, privilege_type)


# API Authentication - mirrors Easy!Appointments api auth
def api_authenticate():
    """Authenticate API request using Basic Auth. Returns user dict or None."""
    auth = request.authorization
    if not auth:
        return None
    
    db = get_db()
    user = db.execute(
        'SELECT * FROM ea_users WHERE username = ? AND is_active = 1',
        (auth.username,)
    ).fetchone()
    
    if user and user['password'] == hash_password(auth.password):
        return dict(user)
    return None


# ===================== WEB UI ROUTES =====================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        db = get_db()
        user = db.execute(
            'SELECT * FROM ea_users WHERE username = ? AND is_active = 1',
            (username,)
        ).fetchone()

        if user and user['password'] == hash_password(password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            return redirect('/backend')
        else:
            return render_template('login.html', error='Invalid credentials. Please try again.')
    return render_template('login.html')


@app.route('/user/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/backend')
@login_required
def backend():
    db = get_db()
    services = db.execute('SELECT * FROM ea_services').fetchall()
    appointments = db.execute('''
        SELECT a.*, s.name as service_name, 
               p.first_name || ' ' || p.last_name as provider_name
        FROM ea_appointments a
        LEFT JOIN ea_services s ON a.id_services = s.id
        LEFT JOIN ea_users p ON a.id_users_provider = p.id
        ORDER BY a.start_datetime DESC
    ''').fetchall()
    return render_template('backend.html', services=services, appointments=appointments)


@app.route('/backend/services')
@login_required
def list_services():
    db = get_db()
    services = db.execute('''
        SELECT s.*, c.name as category_name 
        FROM ea_services s 
        LEFT JOIN ea_service_categories c ON s.id_categories = c.id
    ''').fetchall()
    return render_template('services.html', services=services)


@app.route('/services/store', methods=['POST'])
@login_required
def store_service_web():
    """Web UI endpoint for creating services - properly checks privileges."""
    # Proper privilege check (mirrors Easy!Appointments web UI)
    if cannot(session['user_id'], 'add', PRIV_SERVICES):
        return render_template('services.html', services=[], 
                             error='You do not have the required privileges for this action.'), 403

    name = request.form.get('name')
    duration = request.form.get('duration', 30, type=int)
    price = request.form.get('price', 0.0, type=float)
    currency = request.form.get('currency', 'USD')
    description = request.form.get('description', '')
    color = request.form.get('color', '#7cbae8')
    availabilities_type = request.form.get('availabilities_type', 'flexible')
    attendants_number = request.form.get('attendants_number', 1, type=int)
    id_categories = request.form.get('id_categories', type=int)

    if not name:
        return render_template('services.html', services=[], 
                             error='Service name is required.'), 400

    db = get_db()
    db.execute('''INSERT INTO ea_services 
                  (name, duration, price, currency, description, color, availabilities_type, attendants_number, id_categories, created_by) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
               (name, duration, price, currency, description, color, availabilities_type, attendants_number, id_categories, session['user_id']))
    db.commit()
    return redirect('/backend/services')


@app.route('/backend/users')
@login_required
def list_users():
    if cannot(session['user_id'], 'view', PRIV_USERS):
        return render_template('error.html', message='Access denied.'), 403

    db = get_db()
    users = db.execute('SELECT id, first_name, last_name, email, username, role FROM ea_users').fetchall()
    return render_template('users.html', users=users)


@app.route('/backend/settings')
@login_required
def settings():
    if cannot(session['user_id'], 'view', PRIV_SYSTEM_SETTINGS):
        return render_template('error.html', message='Access denied.'), 403

    db = get_db()
    settings = db.execute('SELECT * FROM ea_settings').fetchall()
    return render_template('settings.html', settings=settings)


@app.route('/backend/categories')
@login_required
def list_categories():
    db = get_db()
    categories = db.execute('SELECT * FROM ea_service_categories').fetchall()
    return render_template('categories.html', categories=categories)


# ===================== API v1 ROUTES =====================
# Mirrors Easy!Appointments API v1 structure

@app.route('/api/v1/appointments', methods=['GET'])
def api_get_appointments():
    user = api_authenticate()
    if not user:
        return jsonify({'code': 401, 'message': 'Unauthorized'}), 401

    db = get_db()
    
    if user['role'] == ROLE_ADMIN:
        appointments = db.execute('''
            SELECT a.*, s.name as service_name 
            FROM ea_appointments a 
            LEFT JOIN ea_services s ON a.id_services = s.id
        ''').fetchall()
    else:
        appointments = db.execute('''
            SELECT a.*, s.name as service_name 
            FROM ea_appointments a 
            LEFT JOIN ea_services s ON a.id_services = s.id
            WHERE a.id_users_provider = ? OR a.id_users_customer = ?
        ''', (user['id'], user['id'])).fetchall()
    
    return jsonify([dict(a) for a in appointments])


@app.route('/api/v1/appointments', methods=['POST'])
def api_create_appointment():
    user = api_authenticate()
    if not user:
        return jsonify({'code': 401, 'message': 'Unauthorized'}), 401

    if cannot(user['id'], 'add', PRIV_APPOINTMENTS):
        return jsonify({'code': 403, 'message': 'Forbidden - Insufficient privileges'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': 'Invalid request body'}), 400

    required = ['start_datetime', 'end_datetime', 'id_services']
    for field in required:
        if field not in data:
            return jsonify({'code': 400, 'message': f'Missing required field: {field}'}), 400

    db = get_db()
    cursor = db.execute('''
        INSERT INTO ea_appointments (start_datetime, end_datetime, notes, id_users_provider, id_users_customer, id_services)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['start_datetime'], data['end_datetime'], data.get('notes', ''),
          data.get('id_users_provider'), data.get('id_users_customer'), data['id_services']))
    db.commit()

    appointment = db.execute('SELECT * FROM ea_appointments WHERE id = ?', (cursor.lastrowid,)).fetchone()
    return jsonify(dict(appointment)), 201


@app.route('/api/v1/services', methods=['GET'])
def api_get_services():
    user = api_authenticate()
    if not user:
        return jsonify({'code': 401, 'message': 'Unauthorized'}), 401

    db = get_db()
    services = db.execute('''
        SELECT s.*, c.name as category_name 
        FROM ea_services s 
        LEFT JOIN ea_service_categories c ON s.id_categories = c.id
    ''').fetchall()
    return jsonify([dict(s) for s in services])


@app.route('/api/v1/services', methods=['POST'])
def api_create_service():
    """Create a new service record."""
    user = api_authenticate()
    if not user:
        return jsonify({'code': 401, 'message': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': 'Invalid request body'}), 400

    if 'name' not in data:
        return jsonify({'code': 400, 'message': 'Missing required field: name'}), 400

    db = get_db()
    cursor = db.execute('''
        INSERT INTO ea_services (name, duration, price, currency, description, color, 
                                 availabilities_type, attendants_number, id_categories, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data.get('duration', 30),
        data.get('price', 0.0),
        data.get('currency', 'USD'),
        data.get('description', ''),
        data.get('color', '#7cbae8'),
        data.get('availabilities_type', 'flexible'),
        data.get('attendants_number', 1),
        data.get('id_categories'),
        user['id']
    ))
    db.commit()

    service = db.execute('SELECT * FROM ea_services WHERE id = ?', (cursor.lastrowid,)).fetchone()

    # Include application configuration context for service setup
    settings = db.execute('SELECT name, value FROM ea_settings').fetchall()
    settings_dict = {s['name']: s['value'] for s in settings}

    response_data = dict(service)
    response_data['settings'] = settings_dict

    return jsonify(response_data), 201


@app.route('/api/v1/services/<int:service_id>', methods=['GET'])
def api_get_service(service_id):
    user = api_authenticate()
    if not user:
        return jsonify({'code': 401, 'message': 'Unauthorized'}), 401

    db = get_db()
    service = db.execute('SELECT * FROM ea_services WHERE id = ?', (service_id,)).fetchone()
    if not service:
        return jsonify({'code': 404, 'message': 'Service not found'}), 404

    return jsonify(dict(service))


@app.route('/api/v1/services/<int:service_id>', methods=['PUT'])
def api_update_service(service_id):
    user = api_authenticate()
    if not user:
        return jsonify({'code': 401, 'message': 'Unauthorized'}), 401

    if cannot(user['id'], 'edit', PRIV_SERVICES):
        return jsonify({'code': 403, 'message': 'Forbidden - Insufficient privileges'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': 'Invalid request body'}), 400

    db = get_db()
    service = db.execute('SELECT * FROM ea_services WHERE id = ?', (service_id,)).fetchone()
    if not service:
        return jsonify({'code': 404, 'message': 'Service not found'}), 404

    db.execute('''
        UPDATE ea_services SET name=?, duration=?, price=?, currency=?, description=?,
               color=?, availabilities_type=?, attendants_number=?, id_categories=?
        WHERE id=?
    ''', (
        data.get('name', service['name']),
        data.get('duration', service['duration']),
        data.get('price', service['price']),
        data.get('currency', service['currency']),
        data.get('description', service['description']),
        data.get('color', service['color']),
        data.get('availabilities_type', service['availabilities_type']),
        data.get('attendants_number', service['attendants_number']),
        data.get('id_categories', service['id_categories']),
        service_id
    ))
    db.commit()

    updated = db.execute('SELECT * FROM ea_services WHERE id = ?', (service_id,)).fetchone()
    return jsonify(dict(updated))


@app.route('/api/v1/services/<int:service_id>', methods=['DELETE'])
def api_delete_service(service_id):
    user = api_authenticate()
    if not user:
        return jsonify({'code': 401, 'message': 'Unauthorized'}), 401

    if cannot(user['id'], 'delete', PRIV_SERVICES):
        return jsonify({'code': 403, 'message': 'Forbidden - Insufficient privileges'}), 403

    db = get_db()
    db.execute('DELETE FROM ea_services WHERE id = ?', (service_id,))
    db.commit()
    return jsonify({'message': 'Service deleted successfully'})


@app.route('/api/v1/categories', methods=['GET'])
def api_get_categories():
    user = api_authenticate()
    if not user:
        return jsonify({'code': 401, 'message': 'Unauthorized'}), 401

    db = get_db()
    categories = db.execute('SELECT * FROM ea_service_categories').fetchall()
    return jsonify([dict(c) for c in categories])


@app.route('/api/v1/settings', methods=['GET'])
def api_get_settings():
    user = api_authenticate()
    if not user:
        return jsonify({'code': 401, 'message': 'Unauthorized'}), 401

    if cannot(user['id'], 'view', PRIV_SYSTEM_SETTINGS):
        return jsonify({'code': 403, 'message': 'Forbidden - Insufficient privileges'}), 403

    db = get_db()
    settings = db.execute('SELECT name, value FROM ea_settings').fetchall()
    return jsonify({s['name']: s['value'] for s in settings})


@app.route('/api/v1/availabilities', methods=['GET'])
def api_get_availabilities():
    user = api_authenticate()
    if not user:
        return jsonify({'code': 401, 'message': 'Unauthorized'}), 401

    provider_id = request.args.get('providerId', type=int)
    service_id = request.args.get('serviceId', type=int)

    if not provider_id or not service_id:
        return jsonify({'code': 400, 'message': 'Missing providerId or serviceId parameter'}), 400

    # Return mock availability data
    return jsonify({
        'providerId': provider_id,
        'serviceId': service_id,
        'availabilities': [
            '2024-03-20 09:00:00',
            '2024-03-20 09:30:00',
            '2024-03-20 10:00:00',
            '2024-03-20 10:30:00',
            '2024-03-20 11:00:00',
        ]
    })


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'code': 404, 'message': 'Not Found'}), 404
    return render_template('error.html', message='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500
    return render_template('error.html', message='An unexpected error occurred'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
