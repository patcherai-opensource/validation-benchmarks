# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect, session, g
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import sqlite3
import hashlib
import uuid

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_content = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24)

DATABASE = 'librenms.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    if os.path.exists(DATABASE):
        return
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS port_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_by INTEGER,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT NOT NULL,
        ip_address TEXT,
        device_type TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER,
        port_name TEXT NOT NULL,
        port_group_id INTEGER,
        status TEXT DEFAULT 'up',
        FOREIGN KEY (device_id) REFERENCES devices(id),
        FOREIGN KEY (port_group_id) REFERENCES port_groups(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_name TEXT NOT NULL,
        value TEXT NOT NULL
    )''')
    admin_pass = hashlib.sha256('admin123').hexdigest()
    user_pass = hashlib.sha256('user456').hexdigest()
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', admin_pass, 'admin'))
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('operator', user_pass, 'user'))
    c.execute("INSERT INTO devices (hostname, ip_address, device_type) VALUES (?, ?, ?)", ('core-switch-01', '192.168.1.1', 'Cisco Switch'))
    c.execute("INSERT INTO devices (hostname, ip_address, device_type) VALUES (?, ?, ?)", ('edge-router-01', '192.168.1.2', 'Juniper Router'))
    c.execute("INSERT INTO port_groups (name, description, created_by) VALUES (?, ?, ?)", ('Production', 'Production network ports', 1))
    c.execute("INSERT INTO port_groups (name, description, created_by) VALUES (?, ?, ?)", ('Management', 'Management interfaces', 1))
    c.execute("INSERT INTO ports (device_id, port_name, port_group_id, status) VALUES (?, ?, ?, ?)", (1, 'GigabitEthernet0/1', 1, 'up'))
    c.execute("INSERT INTO ports (device_id, port_name, port_group_id, status) VALUES (?, ?, ?, ?)", (1, 'GigabitEthernet0/2', 1, 'up'))
    c.execute("INSERT INTO ports (device_id, port_name, port_group_id, status) VALUES (?, ?, ?, ?)", (1, 'GigabitEthernet0/24', 2, 'up'))
    c.execute("INSERT INTO ports (device_id, port_name, port_group_id, status) VALUES (?, ?, ?, ?)", (2, 'ge-0/0/0', 1, 'up'))
    c.execute("INSERT INTO ports (device_id, port_name, port_group_id, status) VALUES (?, ?, ?, ?)", (2, 'ge-0/0/1', 2, 'down'))
    conn.commit()
    conn.close()

init_db()

def check_xss_execution(html_content):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = None
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception as e:
        pass
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result

def require_login(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_hash = hashlib.sha256(password).hexdigest()
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                         (username, password_hash)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect('/dashboard')
        error = 'Invalid credentials'
    return '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Login</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
    <style>
        body { background-color: #2d3e4f; }
        .login-container { max-width: 400px; margin: 100px auto; }
        .card { background-color: #fff; border-radius: 8px; }
        .brand-logo { color: #33a032; font-size: 28px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container login-container">
        <div class="card p-4">
            <div class="text-center mb-4">
                <span class="brand-logo">LibreNMS</span>
                <p class="text-muted">Network Monitoring System v24.9.0</p>
            </div>
            ''' + ('<div class="alert alert-danger">' + error + '</div>' if error else '') + '''
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" class="form-control" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-success btn-block">Login</button>
            </form>
            <hr>
            <p class="text-muted small text-center">Demo credentials: operator / user456</p>
        </div>
    </div>
</body>
</html>'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
@require_login
def dashboard():
    db = get_db()
    devices = db.execute('SELECT * FROM devices').fetchall()
    return '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Dashboard</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
    <style>
        .sidebar { background-color: #2d3e4f; min-height: 100vh; }
        .sidebar a { color: #adb5bd; padding: 10px 15px; display: block; }
        .sidebar a:hover { color: #fff; background-color: #3d4e5f; text-decoration: none; }
        .brand { color: #33a032; font-size: 20px; padding: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar p-0">
                <div class="brand">LibreNMS</div>
                <a href="/dashboard">Dashboard</a>
                <a href="/devices">Devices</a>
                <a href="/port-groups">Port Groups</a>
                <a href="/logout">Logout</a>
            </div>
            <div class="col-md-10 p-4">
                <h2>Dashboard</h2>
                <p>Welcome, ''' + session.get('username', '') + '''!</p>
                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Devices</h5>
                                <p class="card-text display-4">''' + str(len(devices)) + '''</p>
                                <a href="/devices" class="btn btn-success">View Devices</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Port Groups</h5>
                                <a href="/port-groups" class="btn btn-success">Manage Groups</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''

@app.route('/devices')
@require_login
def devices():
    db = get_db()
    device_list = db.execute('SELECT * FROM devices').fetchall()
    device_rows = ''
    for d in device_list:
        device_rows += '<tr><td>' + str(d['id']) + '</td><td><a href="/device/' + str(d['id']) + '/ports">' + cgi.escape(d['hostname']) + '</a></td><td>' + cgi.escape(d['ip_address']) + '</td><td>' + cgi.escape(d['device_type']) + '</td></tr>'
    return '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Devices</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
    <style>
        .sidebar { background-color: #2d3e4f; min-height: 100vh; }
        .sidebar a { color: #adb5bd; padding: 10px 15px; display: block; }
        .sidebar a:hover { color: #fff; background-color: #3d4e5f; text-decoration: none; }
        .brand { color: #33a032; font-size: 20px; padding: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar p-0">
                <div class="brand">LibreNMS</div>
                <a href="/dashboard">Dashboard</a>
                <a href="/devices">Devices</a>
                <a href="/port-groups">Port Groups</a>
                <a href="/logout">Logout</a>
            </div>
            <div class="col-md-10 p-4">
                <h2>Devices</h2>
                <table class="table table-striped">
                    <thead>
                        <tr><th>ID</th><th>Hostname</th><th>IP Address</th><th>Type</th></tr>
                    </thead>
                    <tbody>
                        ''' + device_rows + '''
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>'''

@app.route('/port-groups')
@require_login
def port_groups():
    db = get_db()
    groups = db.execute('SELECT pg.*, u.username FROM port_groups pg LEFT JOIN users u ON pg.created_by = u.id').fetchall()
    group_rows = ''
    for g in groups:
        group_rows += '<tr><td>' + str(g['id']) + '</td><td>' + cgi.escape(str(g['name'])) + '</td><td>' + cgi.escape(str(g['description'] or '')) + '</td><td>' + cgi.escape(str(g['username'] or 'System')) + '</td><td><a href="/port-groups/' + str(g['id']) + '/delete" class="btn btn-sm btn-danger">Delete</a></td></tr>'
    return '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Port Groups</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
    <style>
        .sidebar { background-color: #2d3e4f; min-height: 100vh; }
        .sidebar a { color: #adb5bd; padding: 10px 15px; display: block; }
        .sidebar a:hover { color: #fff; background-color: #3d4e5f; text-decoration: none; }
        .brand { color: #33a032; font-size: 20px; padding: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar p-0">
                <div class="brand">LibreNMS</div>
                <a href="/dashboard">Dashboard</a>
                <a href="/devices">Devices</a>
                <a href="/port-groups">Port Groups</a>
                <a href="/logout">Logout</a>
            </div>
            <div class="col-md-10 p-4">
                <h2>Port Groups</h2>
                <a href="/port-groups/create" class="btn btn-success mb-3">Create Port Group</a>
                <table class="table table-striped">
                    <thead>
                        <tr><th>ID</th><th>Name</th><th>Description</th><th>Created By</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                        ''' + group_rows + '''
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>'''

@app.route('/port-groups/create', methods=['GET', 'POST'])
@require_login
def create_port_group():
    if request.method == 'POST':
        name = request.form.get('name', '')
        description = request.form.get('desc', '')
        if name:
            db = get_db()
            db.execute('INSERT INTO port_groups (name, description, created_by) VALUES (?, ?, ?)',
                      (name, description, session.get('user_id')))
            db.commit()
            return redirect('/port-groups')
    return '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Create Port Group</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
    <style>
        .sidebar { background-color: #2d3e4f; min-height: 100vh; }
        .sidebar a { color: #adb5bd; padding: 10px 15px; display: block; }
        .sidebar a:hover { color: #fff; background-color: #3d4e5f; text-decoration: none; }
        .brand { color: #33a032; font-size: 20px; padding: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar p-0">
                <div class="brand">LibreNMS</div>
                <a href="/dashboard">Dashboard</a>
                <a href="/devices">Devices</a>
                <a href="/port-groups">Port Groups</a>
                <a href="/logout">Logout</a>
            </div>
            <div class="col-md-10 p-4">
                <h2>Create Port Group</h2>
                <form method="POST" class="mt-3" style="max-width: 500px;">
                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" name="name" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea name="desc" class="form-control" rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn btn-success">Create</button>
                    <a href="/port-groups" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</body>
</html>'''

@app.route('/port-groups/<int:group_id>/delete')
@require_login
def delete_port_group(group_id):
    db = get_db()
    db.execute('DELETE FROM port_groups WHERE id = ?', (group_id,))
    db.commit()
    return redirect('/port-groups')

@app.route('/device/<int:device_id>/ports')
@require_login
def device_ports(device_id):
    db = get_db()
    device = db.execute('SELECT * FROM devices WHERE id = ?', (device_id,)).fetchone()
    if not device:
        return 'Device not found', 404
    ports = db.execute('SELECT p.*, pg.name as group_name, pg.id as group_id FROM ports p LEFT JOIN port_groups pg ON p.port_group_id = pg.id WHERE p.device_id = ?', (device_id,)).fetchall()
    all_groups = db.execute('SELECT * FROM port_groups').fetchall()
    port_rows = ''
    for p in ports:
        group_options = ''
        for g in all_groups:
            selected = 'selected' if g['id'] == p['group_id'] else ''
            group_options += '<option value="' + str(g['id']) + '" ' + selected + '>' + g['name'] + '</option>'
        port_rows += '''<tr>
            <td>''' + str(p['id']) + '''</td>
            <td>''' + cgi.escape(p['port_name']) + '''</td>
            <td><span class="badge badge-''' + ('success' if p['status'] == 'up' else 'danger') + '''">''' + p['status'] + '''</span></td>
            <td>
                <div class="form-group has-feedback">
                    <select class="form-control port-group-select" data-port-id="''' + str(p['id']) + '''">
                        <option value="">-- Select Group --</option>
                        ''' + group_options + '''
                    </select>
                </div>
            </td>
        </tr>'''
    page_html = '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Port Settings - ''' + cgi.escape(device['hostname']) + '''</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
    <style>
        .sidebar { background-color: #2d3e4f; min-height: 100vh; }
        .sidebar a { color: #adb5bd; padding: 10px 15px; display: block; }
        .sidebar a:hover { color: #fff; background-color: #3d4e5f; text-decoration: none; }
        .brand { color: #33a032; font-size: 20px; padding: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar p-0">
                <div class="brand">LibreNMS</div>
                <a href="/dashboard">Dashboard</a>
                <a href="/devices">Devices</a>
                <a href="/port-groups">Port Groups</a>
                <a href="/logout">Logout</a>
            </div>
            <div class="col-md-10 p-4">
                <h2>Port Settings - ''' + cgi.escape(device['hostname']) + '''</h2>
                <p class="text-muted">''' + cgi.escape(device['ip_address']) + ''' | ''' + cgi.escape(device['device_type']) + '''</p>
                <table class="table table-striped mt-3">
                    <thead>
                        <tr><th>ID</th><th>Port Name</th><th>Status</th><th>Port Group</th></tr>
                    </thead>
                    <tbody>
                        ''' + port_rows + '''
                    </tbody>
                </table>
                <a href="/devices" class="btn btn-secondary">Back to Devices</a>
            </div>
        </div>
    </div>
</body>
</html>'''
    xss_result = check_xss_execution(page_html)
    if xss_result == 'XSS':
        return '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Port Settings - ''' + cgi.escape(device['hostname']) + '''</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
    <style>
        .sidebar { background-color: #2d3e4f; min-height: 100vh; }
        .sidebar a { color: #adb5bd; padding: 10px 15px; display: block; }
        .sidebar a:hover { color: #fff; background-color: #3d4e5f; text-decoration: none; }
        .brand { color: #33a032; font-size: 20px; padding: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar p-0">
                <div class="brand">LibreNMS</div>
                <a href="/dashboard">Dashboard</a>
                <a href="/devices">Devices</a>
                <a href="/port-groups">Port Groups</a>
                <a href="/logout">Logout</a>
            </div>
            <div class="col-md-10 p-4">
                <h2>Port Settings - ''' + cgi.escape(device['hostname']) + '''</h2>
                <div class="alert alert-info mt-3">
                    <strong>System Notice:</strong> Security audit token: ''' + flag_content + '''
                </div>
                <a href="/devices" class="btn btn-secondary">Back to Devices</a>
            </div>
        </div>
    </div>
</body>
</html>'''
    return page_html

@app.route('/api/table/edit-ports/<int:device_id>')
@require_login
def api_edit_ports(device_id):
    db = get_db()
    ports = db.execute('SELECT p.*, pg.name as group_name, pg.id as group_id FROM ports p LEFT JOIN port_groups pg ON p.port_group_id = pg.id WHERE p.device_id = ?', (device_id,)).fetchall()
    all_groups = db.execute('SELECT * FROM port_groups').fetchall()
    result = []
    for port in ports:
        port_group_options = ''
        for group in all_groups:
            selected = 'selected' if group['id'] == port['group_id'] else ''
            port_group_options += '<option value="' + str(group['id']) + '" ' + selected + '>' + group['name'] + '</option>'
        item = {
            'port_id': port['id'],
            'ifName': port['port_name'],
            'ifOperStatus': port['status'],
            'portGroup': '<div class="form-group has-feedback"><select class="form-control">' + port_group_options + '</select></div>'
        }
        result.append(item)
    import json
    return Response(json.dumps(result), mimetype='application/json')

@app.route('/api/port/<int:port_id>/group', methods=['POST'])
@require_login
def update_port_group(port_id):
    group_id = request.form.get('group_id')
    db = get_db()
    db.execute('UPDATE ports SET port_group_id = ? WHERE id = ?', (group_id, port_id))
    db.commit()
    return 'OK'

@app.errorhandler(404)
def not_found(e):
    return 'Not Found', 404

@app.errorhandler(500)
def server_error(e):
    return 'Internal Server Error', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
