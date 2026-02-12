from flask import Flask, request, redirect, session, url_for, render_template, jsonify, abort
import sqlite3
import hashlib
import os
import time
import threading
import logging

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

DATABASE = '/data/umbraco.db'
RUNTIME_LEVEL = 'Run'  # Run, Install, Upgrade
DB_AVAILABLE = True
DB_LOCK = threading.Lock()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('Umbraco.Core')


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_db():
    """Get a database connection, respecting availability state."""
    global DB_AVAILABLE
    with DB_LOCK:
        if not DB_AVAILABLE:
            raise sqlite3.OperationalError("database is locked")
    conn = sqlite3.connect(DATABASE, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the Umbraco database schema and seed data."""
    os.makedirs('/data', exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS umbracoUser (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userLogin TEXT UNIQUE NOT NULL,
            userPassword TEXT NOT NULL,
            userName TEXT NOT NULL,
            userEmail TEXT NOT NULL,
            userType INTEGER NOT NULL DEFAULT 0,
            userDisabled INTEGER NOT NULL DEFAULT 0,
            createDate TEXT DEFAULT CURRENT_TIMESTAMP,
            updateDate TEXT DEFAULT CURRENT_TIMESTAMP,
            failedLoginAttempts INTEGER DEFAULT 0,
            lastLoginDate TEXT,
            lastPasswordChangeDate TEXT DEFAULT CURRENT_TIMESTAMP,
            securityStampToken TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS umbracoUserGroup (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userGroupAlias TEXT NOT NULL,
            userGroupName TEXT NOT NULL,
            userGroupDefaultPermissions TEXT,
            createDate TEXT DEFAULT CURRENT_TIMESTAMP,
            updateDate TEXT DEFAULT CURRENT_TIMESTAMP,
            icon TEXT,
            startContentId INTEGER,
            startMediaId INTEGER,
            hasAccessToAllLanguages INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS umbracoUser2UserGroup (
            userId INTEGER NOT NULL,
            userGroupId INTEGER NOT NULL,
            PRIMARY KEY (userId, userGroupId),
            FOREIGN KEY (userId) REFERENCES umbracoUser(id),
            FOREIGN KEY (userGroupId) REFERENCES umbracoUserGroup(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS umbracoNode (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parentId INTEGER DEFAULT -1,
            nodeObjectType TEXT,
            text TEXT,
            sortOrder INTEGER DEFAULT 0,
            createDate TEXT DEFAULT CURRENT_TIMESTAMP,
            trashed INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            path TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS umbracoContent (
            nodeId INTEGER PRIMARY KEY,
            contentTypeId INTEGER,
            FOREIGN KEY (nodeId) REFERENCES umbracoNode(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS umbracoContentVersion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nodeId INTEGER,
            versionDate TEXT DEFAULT CURRENT_TIMESTAMP,
            current INTEGER DEFAULT 1,
            text TEXT,
            userId INTEGER,
            FOREIGN KEY (nodeId) REFERENCES umbracoNode(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS umbracoPropertyData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            versionId INTEGER,
            propertyTypeId INTEGER,
            dataNvarchar TEXT,
            dataNtext TEXT,
            dataInt INTEGER,
            FOREIGN KEY (versionId) REFERENCES umbracoContentVersion(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS umbracoKeyValue (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS umbracoServer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT,
            computerName TEXT,
            registeredDate TEXT DEFAULT CURRENT_TIMESTAMP,
            lastNotifiedDate TEXT DEFAULT CURRENT_TIMESTAMP,
            isActive INTEGER DEFAULT 1,
            isSchedulingPublisher INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS umbracoLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER DEFAULT -1,
            nodeId INTEGER DEFAULT -1,
            entityType TEXT,
            logHeader TEXT,
            logComment TEXT,
            datestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS umbracoAudit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            performingUserId INTEGER DEFAULT -1,
            affectedUserId INTEGER DEFAULT -1,
            affectedDetails TEXT,
            eventType TEXT,
            eventDetails TEXT,
            datestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cmsPropertyType (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataTypeId INTEGER,
            contentTypeId INTEGER,
            propertyTypeGroupId INTEGER,
            alias TEXT,
            name TEXT,
            sortOrder INTEGER DEFAULT 0,
            mandatory INTEGER DEFAULT 0,
            validationRegExp TEXT,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cmsContentType (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            nodeId INTEGER,
            alias TEXT,
            icon TEXT,
            thumbnail TEXT,
            description TEXT,
            isContainer INTEGER DEFAULT 0,
            isElement INTEGER DEFAULT 0,
            allowAtRoot INTEGER DEFAULT 0,
            variations INTEGER DEFAULT 1,
            FOREIGN KEY (nodeId) REFERENCES umbracoNode(id)
        )
    ''')

    # Seed admin user (SuperUser)
    admin_pw = hash_password('Umbraco2023!Secure')
    cursor.execute('''INSERT OR IGNORE INTO umbracoUser 
        (id, userLogin, userPassword, userName, userEmail, userType)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (-1, 'admin@umbraco.local', admin_pw, 'Administrator', 'admin@umbraco.local', 1))

    # Seed regular backoffice user
    editor_pw = hash_password('Editor2023!')
    cursor.execute('''INSERT OR IGNORE INTO umbracoUser 
        (id, userLogin, userPassword, userName, userEmail, userType)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (1, 'editor@umbraco.local', editor_pw, 'Content Editor', 'editor@umbraco.local', 0))

    # Seed user groups
    cursor.execute('''INSERT OR IGNORE INTO umbracoUserGroup 
        (id, userGroupAlias, userGroupName, userGroupDefaultPermissions, icon)
        VALUES (?, ?, ?, ?, ?)''',
        (1, 'admin', 'Administrators', 'CADMOSRPUK', 'icon-medal'))

    cursor.execute('''INSERT OR IGNORE INTO umbracoUserGroup 
        (id, userGroupAlias, userGroupName, userGroupDefaultPermissions, icon)
        VALUES (?, ?, ?, ?, ?)''',
        (2, 'editor', 'Editors', 'CRUDO', 'icon-edit'))

    cursor.execute('''INSERT OR IGNORE INTO umbracoUserGroup 
        (id, userGroupAlias, userGroupName, userGroupDefaultPermissions, icon)
        VALUES (?, ?, ?, ?, ?)''',
        (3, 'writer', 'Writers', 'CRU', 'icon-pencil'))

    cursor.execute('''INSERT OR IGNORE INTO umbracoUserGroup 
        (id, userGroupAlias, userGroupName, userGroupDefaultPermissions, icon)
        VALUES (?, ?, ?, ?, ?)''',
        (4, 'translator', 'Translators', 'CRU', 'icon-globe'))

    # Assign admin to Administrators group
    cursor.execute('INSERT OR IGNORE INTO umbracoUser2UserGroup (userId, userGroupId) VALUES (?, ?)', (-1, 1))
    # Assign editor to Editors group
    cursor.execute('INSERT OR IGNORE INTO umbracoUser2UserGroup (userId, userGroupId) VALUES (?, ?)', (1, 2))

    # Seed key-value settings
    cursor.execute('INSERT OR IGNORE INTO umbracoKeyValue (key, value) VALUES (?, ?)',
        ('Umbraco.Core.RuntimeState', 'Run'))
    cursor.execute('INSERT OR IGNORE INTO umbracoKeyValue (key, value) VALUES (?, ?)',
        ('Umbraco.Core.Upgrader.State', '{"currentState":"13.0.0","targetState":"13.0.0"}'))

    # Seed server registration
    cursor.execute('INSERT OR IGNORE INTO umbracoServer (address, computerName, isActive, isSchedulingPublisher) VALUES (?, ?, ?, ?)',
        ('https://localhost:5003', 'UMBRACO-SRV01', 1, 1))

    # Seed some content nodes (so the backoffice looks populated)
    cursor.execute('INSERT OR IGNORE INTO umbracoNode (id, parentId, nodeObjectType, text, sortOrder, level, path) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (1, -1, 'C66BA18E-EAF3-4CFF-8A22-41B16D66A972', 'Home', 0, 1, '-1,1'))
    cursor.execute('INSERT OR IGNORE INTO umbracoNode (id, parentId, nodeObjectType, text, sortOrder, level, path) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (2, 1, 'C66BA18E-EAF3-4CFF-8A22-41B16D66A972', 'About', 0, 2, '-1,1,2'))
    cursor.execute('INSERT OR IGNORE INTO umbracoNode (id, parentId, nodeObjectType, text, sortOrder, level, path) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (3, 1, 'C66BA18E-EAF3-4CFF-8A22-41B16D66A972', 'Contact', 1, 2, '-1,1,3'))

    # Seed audit log
    cursor.execute('INSERT OR IGNORE INTO umbracoAudit (id, performingUserId, eventType, eventDetails) VALUES (?, ?, ?, ?)',
        (1, -1, 'umbraco/user/save', 'Initial setup completed'))

    conn.commit()
    conn.close()


def determine_runtime_level():
    """
    Check database connectivity and determine the runtime level.
    If the database is unreachable, the system falls back to Install mode.
    This mirrors RuntimeState.DetermineRuntimeLevel() in Umbraco.
    """
    global RUNTIME_LEVEL
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM umbracoKeyValue WHERE key = 'Umbraco.Core.RuntimeState'")
        row = cursor.fetchone()
        conn.close()
        if row:
            RUNTIME_LEVEL = row['value']
        else:
            RUNTIME_LEVEL = 'Install'
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        RUNTIME_LEVEL = 'Install'
    return RUNTIME_LEVEL


def check_runtime_level():
    """Thread that periodically checks runtime level."""
    while True:
        determine_runtime_level()
        time.sleep(10)


# --- Middleware ---

@app.before_request
def check_system_state():
    """Log and track requests."""
    pass


# --- Public Routes ---

@app.route('/')
def index():
    level = determine_runtime_level()
    if level == 'Install':
        return redirect('/install')
    return redirect('/umbraco')


@app.route('/ping')
def ping():
    return 'pong', 200


@app.route('/umbraco/api/keepalive/ping', methods=['GET'])
def api_keepalive():
    return jsonify({"status": "ok"}), 200


# --- Install Routes ---

@app.route('/install')
def install_page():
    if RUNTIME_LEVEL != 'Install':
        return redirect('/umbraco')
    return render_template('install/index.html')


@app.route('/install/api/GetSetup', methods=['GET'])
def install_get_setup():
    if RUNTIME_LEVEL != 'Install':
        return jsonify({"error": "Umbraco is already configured"}), 403
    return jsonify({
        "installId": "a8e7c2d1-3f45-4b89-9c12-def456789abc",
        "steps": [
            {"name": "DatabaseConfigure", "serverOrder": 0, "view": "database"},
            {"name": "UserConfiguration", "serverOrder": 1, "view": "user"},
            {"name": "Permissions", "serverOrder": 2, "view": "starterkit"},
            {"name": "Complete", "serverOrder": 3, "view": "complete"}
        ],
        "currentStep": "Complete"
    })


@app.route('/install/api/PostValidateDatabaseConnection', methods=['POST'])
def install_validate_db():
    if RUNTIME_LEVEL != 'Install':
        return jsonify({"error": "Umbraco is already configured"}), 403
    try:
        conn = get_db()
        conn.close()
        return jsonify({"success": True, "message": "Database connection successful"})
    except Exception:
        return jsonify({"success": False, "message": "Database connection failed"})


@app.route('/install/api/PostPerformInstall', methods=['POST'])
def install_complete():
    """
    Complete the installation process.
    In vulnerable versions, this automatically signs in the SuperUser
    after completing the install steps, even when using a pre-existing database.
    """
    global RUNTIME_LEVEL

    if RUNTIME_LEVEL != 'Install':
        return jsonify({"error": "Umbraco is already configured"}), 403

    try:
        conn = get_db()
        cursor = conn.cursor()

        # Verify the database has the required schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='umbracoUser'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Database schema not found. Please configure the database first."}), 400

        # Update runtime state to Run
        cursor.execute("UPDATE umbracoKeyValue SET value = 'Run', updated = datetime('now') WHERE key = 'Umbraco.Core.RuntimeState'")
        conn.commit()

        RUNTIME_LEVEL = 'Run'

        # Retrieve SuperUser (id=-1) credentials for auto-signin
        cursor.execute("SELECT id, userLogin, userName, userEmail, userType FROM umbracoUser WHERE id = -1")
        superuser = cursor.fetchone()

        if superuser:
            # Auto sign-in as SuperUser after install completion
            session['user_id'] = superuser['id']
            session['user_login'] = superuser['userLogin']
            session['user_name'] = superuser['userName']
            session['user_email'] = superuser['userEmail']
            session['user_type'] = superuser['userType']
            session['is_admin'] = True
            session['auth_ticket'] = hashlib.sha256(
                f"{superuser['userLogin']}:{time.time()}".encode()
            ).hexdigest()

            # Log the install completion
            cursor.execute('''INSERT INTO umbracoAudit 
                (performingUserId, eventType, eventDetails) 
                VALUES (?, ?, ?)''',
                (-1, 'umbraco/install/complete', 'Installation completed, SuperUser signed in'))
            cursor.execute('''INSERT INTO umbracoLog 
                (userId, logHeader, logComment) 
                VALUES (?, ?, ?)''',
                (-1, 'Install', 'Installation completed successfully'))
            conn.commit()

        conn.close()

        return jsonify({
            "success": True,
            "message": "Installation completed successfully",
            "nextStep": "/umbraco"
        })

    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        return jsonify({"error": "Database error during installation"}), 500


# --- Backoffice Auth Routes ---

@app.route('/umbraco')
def backoffice():
    if 'user_id' not in session:
        return redirect('/umbraco/login')
    return redirect('/umbraco/backoffice')


@app.route('/umbraco/login', methods=['GET'])
def backoffice_login_page():
    level = determine_runtime_level()
    if level == 'Install':
        return redirect('/install')
    return render_template('umbraco/login.html')


@app.route('/umbraco/api/authentication/PostLogin', methods=['POST'])
def backoffice_login():
    level = determine_runtime_level()
    if level == 'Install':
        return jsonify({"error": "System is in install mode"}), 503

    data = request.get_json(silent=True)
    if not data:
        data = request.form

    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, userLogin, userPassword, userName, userEmail, userType, userDisabled, failedLoginAttempts
            FROM umbracoUser WHERE userLogin = ?
        ''', (username,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({"error": "Invalid username or password"}), 401

        if user['userDisabled']:
            conn.close()
            return jsonify({"error": "This account has been disabled"}), 401

        if user['failedLoginAttempts'] >= 5:
            conn.close()
            return jsonify({"error": "Account locked due to too many failed attempts"}), 401

        pw_hash = hash_password(password)
        if pw_hash != user['userPassword']:
            cursor.execute('UPDATE umbracoUser SET failedLoginAttempts = failedLoginAttempts + 1 WHERE id = ?', (user['id'],))
            conn.commit()
            conn.close()
            return jsonify({"error": "Invalid username or password"}), 401

        # Successful login
        cursor.execute('UPDATE umbracoUser SET failedLoginAttempts = 0, lastLoginDate = datetime("now") WHERE id = ?', (user['id'],))

        # Get user groups
        cursor.execute('''
            SELECT ug.userGroupAlias FROM umbracoUserGroup ug
            JOIN umbracoUser2UserGroup u2g ON ug.id = u2g.userGroupId
            WHERE u2g.userId = ?
        ''', (user['id'],))
        groups = [row['userGroupAlias'] for row in cursor.fetchall()]

        cursor.execute('''INSERT INTO umbracoAudit 
            (performingUserId, eventType, eventDetails) 
            VALUES (?, ?, ?)''',
            (user['id'], 'umbraco/user/login', f"User {user['userLogin']} logged in"))
        conn.commit()
        conn.close()

        session['user_id'] = user['id']
        session['user_login'] = user['userLogin']
        session['user_name'] = user['userName']
        session['user_email'] = user['userEmail']
        session['user_type'] = user['userType']
        session['is_admin'] = 'admin' in groups
        session['user_groups'] = groups
        session['auth_ticket'] = hashlib.sha256(
            f"{user['userLogin']}:{time.time()}".encode()
        ).hexdigest()

        return jsonify({
            "success": True,
            "user": {
                "name": user['userName'],
                "email": user['userEmail'],
                "locale": "en-US"
            },
            "redirect": "/umbraco/backoffice"
        })

    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        return jsonify({"error": "Service temporarily unavailable"}), 503


@app.route('/umbraco/api/authentication/PostLogout', methods=['POST'])
def backoffice_logout():
    session.clear()
    return jsonify({"success": True})


@app.route('/umbraco/logout')
def backoffice_logout_get():
    session.clear()
    return redirect('/umbraco/login')


# --- Backoffice Routes ---

@app.route('/umbraco/backoffice')
def backoffice_dashboard():
    if 'user_id' not in session:
        return redirect('/umbraco/login')
    return render_template('umbraco/backoffice.html',
        user_name=session.get('user_name', ''),
        is_admin=session.get('is_admin', False))


@app.route('/umbraco/backoffice/content')
def backoffice_content():
    if 'user_id' not in session:
        return redirect('/umbraco/login')
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, parentId, text, sortOrder, level, path FROM umbracoNode ORDER BY sortOrder')
        nodes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return render_template('umbraco/content.html',
            user_name=session.get('user_name', ''),
            is_admin=session.get('is_admin', False),
            nodes=nodes)
    except Exception:
        return render_template('umbraco/content.html',
            user_name=session.get('user_name', ''),
            is_admin=session.get('is_admin', False),
            nodes=[])


@app.route('/umbraco/backoffice/users')
def backoffice_users():
    if 'user_id' not in session:
        return redirect('/umbraco/login')
    if not session.get('is_admin'):
        abort(403)
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.userLogin, u.userName, u.userEmail, u.userType, u.userDisabled, u.lastLoginDate,
                   GROUP_CONCAT(ug.userGroupName, ', ') as groups
            FROM umbracoUser u
            LEFT JOIN umbracoUser2UserGroup u2g ON u.id = u2g.userId
            LEFT JOIN umbracoUserGroup ug ON u2g.userGroupId = ug.id
            GROUP BY u.id
        ''')
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
    except Exception:
        users = []
    return render_template('umbraco/users.html',
        user_name=session.get('user_name', ''),
        is_admin=session.get('is_admin', False),
        users=users)


@app.route('/umbraco/backoffice/settings')
def backoffice_settings():
    if 'user_id' not in session:
        return redirect('/umbraco/login')
    if not session.get('is_admin'):
        abort(403)

    flag = os.environ.get('FLAG', 'flag{not_set}')

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value, updated FROM umbracoKeyValue')
        settings = [dict(row) for row in cursor.fetchall()]
        cursor.execute('SELECT address, computerName, isActive, isSchedulingPublisher, registeredDate FROM umbracoServer')
        servers = [dict(row) for row in cursor.fetchall()]
        conn.close()
    except Exception:
        settings = []
        servers = []

    return render_template('umbraco/settings.html',
        user_name=session.get('user_name', ''),
        is_admin=session.get('is_admin', False),
        settings=settings,
        servers=servers,
        license_key=flag)


# --- System Health / Maintenance API ---

@app.route('/umbraco/api/server/GetStatus', methods=['GET'])
def server_status():
    return jsonify({
        "serverStatus": "Running" if DB_AVAILABLE else "Maintenance",
        "runtimeLevel": RUNTIME_LEVEL,
        "version": "13.0.0"
    })


@app.route('/umbraco/surface/maintenance/toggle', methods=['POST'])
def maintenance_toggle():
    """
    Toggle database availability for maintenance.
    This simulates the DB outage that triggers install mode.
    In production, this would be an external infrastructure event.
    """
    global DB_AVAILABLE

    action = request.form.get('action', request.args.get('action', ''))

    if action == 'disable':
        with DB_LOCK:
            DB_AVAILABLE = False
        determine_runtime_level()
        return jsonify({"success": True, "dbAvailable": False, "runtimeLevel": RUNTIME_LEVEL})
    elif action == 'enable':
        with DB_LOCK:
            DB_AVAILABLE = True
        return jsonify({"success": True, "dbAvailable": True, "runtimeLevel": RUNTIME_LEVEL})
    else:
        return jsonify({"error": "Invalid action. Use 'enable' or 'disable'."}), 400


# --- API endpoints ---

@app.route('/umbraco/backoffice/api/content/GetChildren', methods=['GET'])
def api_content_children():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    parent_id = request.args.get('parentId', -1, type=int)
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, parentId, text, sortOrder, level, path FROM umbracoNode WHERE parentId = ? ORDER BY sortOrder', (parent_id,))
        nodes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"items": nodes, "totalItems": len(nodes)})
    except Exception:
        return jsonify({"error": "Service unavailable"}), 503


@app.route('/umbraco/backoffice/api/users/GetAll', methods=['GET'])
def api_users():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    if not session.get('is_admin'):
        return jsonify({"error": "Forbidden"}), 403
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, userLogin, userName, userEmail, userType, userDisabled FROM umbracoUser')
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"items": users, "totalItems": len(users)})
    except Exception:
        return jsonify({"error": "Service unavailable"}), 503


@app.route('/umbraco/backoffice/api/audit/GetLog', methods=['GET'])
def api_audit():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    if not session.get('is_admin'):
        return jsonify({"error": "Forbidden"}), 403
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM umbracoAudit ORDER BY datestamp DESC LIMIT 50')
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"items": logs, "totalItems": len(logs)})
    except Exception:
        return jsonify({"error": "Service unavailable"}), 503


# --- Error Handlers ---

@app.errorhandler(403)
def forbidden(e):
    return render_template('umbraco/error.html', error_code=403, error_message="Access denied"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('umbraco/error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('umbraco/error.html', error_code=500, error_message="Internal server error"), 500


if __name__ == '__main__':
    init_db()
    determine_runtime_level()

    # Start background runtime level check
    t = threading.Thread(target=check_runtime_level, daemon=True)
    t.start()

    app.run(host='0.0.0.0', port=5003)
