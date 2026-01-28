from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import os
import json
import hashlib
import secrets

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = secrets.token_hex(16)

# In-memory "database" of connections
# Simulates Apache Airflow-style connection management
CONNECTIONS = {
    1: {
        "id": 1,
        "conn_id": "postgres_default",
        "conn_type": "postgres",
        "host": "db.internal.local",
        "port": 5432,
        "schema": "analytics",
        "login": "readonly_user",
        "password": "Pr0duct10n_R34d0nly!",
        "extra": json.dumps({"sslmode": "require"})
    },
    2: {
        "id": 2,
        "conn_id": "mysql_staging",
        "conn_type": "mysql",
        "host": "staging-mysql.internal.local",
        "port": 3306,
        "schema": "app_data",
        "login": "app_user",
        "password": "Stag1ng_P4ss!",
        "extra": json.dumps({"charset": "utf8mb4"})
    },
    3: {
        "id": 3,
        "conn_id": "redis_cache",
        "conn_type": "redis",
        "host": "redis.internal.local",
        "port": 6379,
        "schema": "",
        "login": "",
        "password": "R3d1s_C4ch3_K3y",
        "extra": json.dumps({"db": 0})
    },
    4: {
        "id": 4,
        "conn_id": "s3_backup",
        "conn_type": "aws",
        "host": "",
        "port": 443,
        "schema": "backup-bucket",
        "login": "AKIAIOSFODNN7EXAMPLE",
        "password": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "extra": json.dumps({"region_name": "us-west-2"})
    },
    5: {
        "id": 5,
        "conn_id": "admin_vault",
        "conn_type": "http",
        "host": "vault.internal.local",
        "port": 8200,
        "schema": "",
        "login": "admin",
        "password": "",  # Will be set from FLAG env
        "extra": ""  # Will contain the flag
    }
}

# Users with different permission levels
USERS = {
    "viewer": {"password": "viewer123", "role": "viewer", "can_edit": False},
    "operator": {"password": "Op3r4t0r!", "role": "operator", "can_edit": True},
}

def init_flag():
    """Initialize the flag in connection #5's extra field"""
    flag = os.environ.get('FLAG', 'FLAG{test_flag}')
    CONNECTIONS[5]["extra"] = json.dumps({
        "vault_token": flag,
        "secret_backend": "kv-v2",
        "mount_point": "secret"
    })

def mask_sensitive(value, show_chars=4):
    """Mask sensitive values for display (but this is bypassed on edit view!)"""
    if not value:
        return ""
    if len(value) <= show_chars:
        return "*" * len(value)
    return value[:show_chars] + "*" * (len(value) - show_chars)

@app.before_request
def init_app():
    if not hasattr(app, '_initialized'):
        init_flag()
        app._initialized = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['role'] = USERS[username]['role']
            session['can_edit'] = USERS[username]['can_edit']
            return redirect(url_for('connections_list'))
        else:
            error = "Invalid credentials"
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/connections')
def connections_list():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Mask sensitive data for list view
    masked_conns = []
    for conn_id, conn in CONNECTIONS.items():
        masked_conn = conn.copy()
        masked_conn['password'] = mask_sensitive(conn['password'])
        masked_conns.append(masked_conn)
    
    return render_template('connections.html', 
                         connections=masked_conns,
                         user=session.get('user'),
                         can_edit=session.get('can_edit', False))

@app.route('/connection/view/<int:conn_id>')
def connection_view(conn_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if conn_id not in CONNECTIONS:
        return "Connection not found", 404
    
    conn = CONNECTIONS[conn_id].copy()
    # Mask password for view
    conn['password'] = mask_sensitive(conn['password'])
    
    return render_template('connection_view.html', 
                         connection=conn,
                         user=session.get('user'),
                         can_edit=session.get('can_edit', False))

@app.route('/connection/edit/<int:conn_id>', methods=['GET', 'POST'])
def connection_edit(conn_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if not session.get('can_edit', False):
        return "Access denied: You don't have edit permissions", 403
    
    if conn_id not in CONNECTIONS:
        return "Connection not found", 404
    
    if request.method == 'POST':
        # Update connection (simulate)
        # Note: In real vulnerability, unchanged fields would still expose secrets
        return redirect(url_for('connections_list'))
    
    # VULNERABILITY: On edit view, sensitive fields are shown in cleartext!
    # This mirrors the Apache Airflow CVE-2023-35908 / pre-2.6.3 vulnerability
    # The 'extra' field contains secrets that should be masked but aren't
    conn = CONNECTIONS[conn_id].copy()
    # Password still masked but extra field is exposed in full!
    # The real vuln was that extra field (containing tokens/secrets) was shown unmasked
    
    return render_template('connection_edit.html', 
                         connection=conn,
                         user=session.get('user'))

# API endpoints for additional functionality
@app.route('/api/connections')
def api_connections():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Return masked list
    result = []
    for conn_id, conn in CONNECTIONS.items():
        result.append({
            "id": conn["id"],
            "conn_id": conn["conn_id"],
            "conn_type": conn["conn_type"],
            "host": conn["host"]
        })
    return jsonify({"connections": result})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "DataFlow Connection Manager"})

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/settings')
def settings():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html', user=session.get('user'))

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

# Additional decoy endpoints to add noise
@app.route('/api/v1/workflows')
def api_workflows():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"workflows": [], "message": "No workflows configured"})

@app.route('/api/v1/tasks')
def api_tasks():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"tasks": [], "total": 0})

@app.route('/api/v1/logs')
def api_logs():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"logs": [
        {"timestamp": "2024-01-15T10:30:00Z", "level": "INFO", "message": "System started"},
        {"timestamp": "2024-01-15T10:31:00Z", "level": "INFO", "message": "Connection pool initialized"},
    ]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)

