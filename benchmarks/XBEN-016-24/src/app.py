# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for, session, g, jsonify
import string
import subprocess
import os
import re
import sys
import sqlite3
import json
import time
import threading
import hashlib
import uuid

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24).encode('hex')

DATABASE = '/app/data/librenms.db'
ADMIN_TOKEN = None

import logging
logging.basicConfig(level=logging.WARNING)


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
    if not os.path.exists('/app/data'):
        os.makedirs('/app/data')
    db = sqlite3.connect(DATABASE)
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        level INTEGER DEFAULT 1,
        realname TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS devices (
        device_id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT NOT NULL,
        sysName TEXT,
        os TEXT DEFAULT 'linux',
        type TEXT DEFAULT 'server',
        hardware TEXT,
        ip TEXT,
        status INTEGER DEFAULT 1,
        last_polled TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS ports (
        port_id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER NOT NULL,
        ifName TEXT NOT NULL,
        ifAlias TEXT,
        ifDescr TEXT,
        ifSpeed INTEGER DEFAULT 1000000000,
        ifOperStatus TEXT DEFAULT 'up',
        ifAdminStatus TEXT DEFAULT 'up',
        FOREIGN KEY (device_id) REFERENCES devices(device_id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS port_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        desc_text TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS port_group_port (
        port_group_id INTEGER NOT NULL,
        port_id INTEGER NOT NULL,
        PRIMARY KEY (port_group_id, port_id),
        FOREIGN KEY (port_group_id) REFERENCES port_groups(id),
        FOREIGN KEY (port_id) REFERENCES ports(port_id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    # Seed default users
    admin_pw = hashlib.sha256('librenms_admin_2024').hexdigest()
    try:
        db.execute("INSERT INTO users (username, password, level, realname, email) VALUES (?, ?, 10, 'Admin User', 'admin@librenms.local')",
                   ('admin', admin_pw))
    except sqlite3.IntegrityError:
        pass

    operator_pw = hashlib.sha256('operator123').hexdigest()
    try:
        db.execute("INSERT INTO users (username, password, level, realname, email) VALUES (?, ?, 5, 'Network Operator', 'operator@librenms.local')",
                   ('operator', operator_pw))
    except sqlite3.IntegrityError:
        pass

    # Seed devices and ports
    try:
        db.execute("INSERT INTO devices (hostname, sysName, os, type, hardware, ip) VALUES ('core-sw01.internal', 'core-sw01', 'ios', 'network', 'Cisco Catalyst 9300', '10.0.1.1')")
        db.execute("INSERT INTO devices (hostname, sysName, os, type, hardware, ip) VALUES ('web-srv01.internal', 'web-srv01', 'linux', 'server', 'Dell PowerEdge R740', '10.0.2.10')")
        db.execute("INSERT INTO devices (hostname, sysName, os, type, hardware, ip) VALUES ('fw-edge01.internal', 'fw-edge01', 'panos', 'firewall', 'Palo Alto PA-3260', '10.0.0.1')")
    except:
        pass

    try:
        ports_data = [
            (1, 'GigabitEthernet0/1', 'Uplink to Distribution', 'GigabitEthernet0/1'),
            (1, 'GigabitEthernet0/2', 'Server Farm', 'GigabitEthernet0/2'),
            (1, 'GigabitEthernet0/3', 'Management VLAN', 'GigabitEthernet0/3'),
            (2, 'eth0', 'Primary NIC', 'eth0'),
            (2, 'eth1', 'Storage Network', 'eth1'),
            (3, 'ethernet1/1', 'WAN Link', 'ethernet1/1'),
            (3, 'ethernet1/2', 'DMZ', 'ethernet1/2'),
            (3, 'ethernet1/3', 'Internal LAN', 'ethernet1/3'),
        ]
        for device_id, ifName, ifAlias, ifDescr in ports_data:
            db.execute("INSERT INTO ports (device_id, ifName, ifAlias, ifDescr) VALUES (?, ?, ?, ?)",
                       (device_id, ifName, ifAlias, ifDescr))
    except:
        pass

    # Seed default port groups
    try:
        db.execute("INSERT INTO port_groups (name, desc_text) VALUES ('Production', 'Production network interfaces')")
        db.execute("INSERT INTO port_groups (name, desc_text) VALUES ('Management', 'Management and OOB interfaces')")
        # Assign some ports to groups
        db.execute("INSERT INTO port_group_port (port_group_id, port_id) VALUES (1, 1)")
        db.execute("INSERT INTO port_group_port (port_group_id, port_id) VALUES (1, 4)")
        db.execute("INSERT INTO port_group_port (port_group_id, port_id) VALUES (2, 3)")
    except:
        pass

    db.commit()
    db.close()


def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    if 'user_id' not in session:
        return None
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return user


# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/devices')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        pw_hash = hashlib.sha256(password).hexdigest()
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                          (username, pw_hash)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['level'] = user['level']
            return redirect('/devices')
        error = 'Invalid credentials'

    return make_response('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LibreNMS - Login</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body { background-color: #060606; color: #fff; font-family: 'Helvetica Neue', sans-serif; }
        .login-container { max-width: 400px; margin: 100px auto; padding: 30px; background: #1a1a2e; border-radius: 4px; }
        .login-container h2 { color: #e73c3e; text-align: center; margin-bottom: 25px; }
        .login-container .form-control { background: #16213e; border: 1px solid #333; color: #fff; }
        .login-container .btn-primary { background-color: #e73c3e; border-color: #e73c3e; width: 100%; }
        .login-container .btn-primary:hover { background-color: #c0392b; }
        .alert-danger { background: #5a1a1a; border-color: #e73c3e; color: #ff6b6b; }
    </style>
</head>
<body>
    <div class="login-container">
        <h2><i class="glyphicon glyphicon-signal"></i> LibreNMS</h2>
        ''' + ('<div class="alert alert-danger">{}</div>'.format(error) if error else '') + '''
        <form method="post">
            <div class="form-group">
                <label>Username</label>
                <input type="text" class="form-control" name="username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" class="form-control" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
    </div>
</body>
</html>''')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/devices')
@require_auth
def devices():
    db = get_db()
    devs = db.execute('SELECT * FROM devices ORDER BY hostname').fetchall()
    user = get_current_user()
    rows = ''
    for d in devs:
        status_label = '<span class="label label-success">Up</span>' if d['status'] else '<span class="label label-danger">Down</span>'
        rows += '<tr><td><a href="/device/{0}">{1}</a></td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td></tr>'.format(
            d['device_id'], d['hostname'], d['sysName'] or '', d['os'], d['type'], d['hardware'] or '', status_label
        )

    return make_response(render_page('Devices', '''
        <div class="panel panel-default">
            <div class="panel-heading"><h3 class="panel-title">Devices</h3></div>
            <div class="panel-body">
                <table class="table table-striped table-condensed">
                    <thead><tr><th>Hostname</th><th>sysName</th><th>OS</th><th>Type</th><th>Hardware</th><th>Status</th></tr></thead>
                    <tbody>''' + rows + '''</tbody>
                </table>
            </div>
        </div>
    ''', user))


@app.route('/device/<int:device_id>')
@require_auth
def device_detail(device_id):
    db = get_db()
    device = db.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,)).fetchone()
    if not device:
        return make_response('Device not found', 404)
    user = get_current_user()

    ports = db.execute('SELECT * FROM ports WHERE device_id = ?', (device_id,)).fetchall()
    port_rows = ''
    for p in ports:
        status_class = 'success' if p['ifOperStatus'] == 'up' else 'danger'
        port_rows += '<tr><td><a href="/device/{0}/port/{1}/edit">{2}</a></td><td>{3}</td><td>{4}</td><td><span class="label label-{5}">{6}</span></td></tr>'.format(
            device_id, p['port_id'], p['ifName'], p['ifAlias'] or '', p['ifDescr'] or '', status_class, p['ifOperStatus']
        )

    return make_response(render_page(device['hostname'], '''
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">''' + device['hostname'] + '''</h3>
            </div>
            <div class="panel-body">
                <dl class="dl-horizontal">
                    <dt>sysName</dt><dd>''' + (device['sysName'] or '') + '''</dd>
                    <dt>OS</dt><dd>''' + device['os'] + '''</dd>
                    <dt>Hardware</dt><dd>''' + (device['hardware'] or '') + '''</dd>
                    <dt>IP</dt><dd>''' + (device['ip'] or '') + '''</dd>
                </dl>
                <h4>Ports</h4>
                <table class="table table-striped table-condensed">
                    <thead><tr><th>Port</th><th>Alias</th><th>Description</th><th>Status</th></tr></thead>
                    <tbody>''' + port_rows + '''</tbody>
                </table>
                <a href="/device/''' + str(device_id) + '''/edit-ports" class="btn btn-primary btn-sm">Port Settings</a>
            </div>
        </div>
    ''', user))


@app.route('/device/<int:device_id>/edit-ports')
@require_auth
def edit_ports(device_id):
    """Port Settings page for editing port group assignments"""
    db = get_db()
    device = db.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,)).fetchone()
    if not device:
        return make_response('Device not found', 404)
    user = get_current_user()

    ports = db.execute('SELECT * FROM ports WHERE device_id = ?', (device_id,)).fetchall()
    all_groups = db.execute('SELECT * FROM port_groups').fetchall()

    table_rows = ''
    for port in ports:
        # Get groups assigned to this port
        assigned = db.execute(
            'SELECT pg.* FROM port_groups pg JOIN port_group_port pgp ON pg.id = pgp.port_group_id WHERE pgp.port_id = ?',
            (port['port_id'],)).fetchall()

        # Build port group options
        port_group_options = ''
        for group in assigned:
            port_group_options += '<option value="' + str(group['id']) + '" selected>' + group['name'] + '</option>'

        # Add unassigned groups as available options
        assigned_ids = [g['id'] for g in assigned]
        for group in all_groups:
            if group['id'] not in assigned_ids:
                port_group_options += '<option value="' + str(group['id']) + '">' + group['name'] + '</option>'

        port_group_select = '<div class="form-group"><select class="form-control port-group-select" name="port_groups_' + str(port['port_id']) + '" multiple>' + port_group_options + '</select></div>'

        status_class = 'success' if port['ifOperStatus'] == 'up' else 'danger'
        table_rows += '''<tr>
            <td>{0}</td>
            <td>{1}</td>
            <td><span class="label label-{2}">{3}</span></td>
            <td>{4}</td>
        </tr>'''.format(
            port['ifName'],
            port['ifAlias'] or '',
            status_class,
            port['ifOperStatus'],
            port_group_select
        )

    return make_response(render_page('Port Settings - ' + device['hostname'], '''
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Port Settings - ''' + device['hostname'] + '''</h3>
            </div>
            <div class="panel-body">
                <form method="post" action="/device/''' + str(device_id) + '''/edit-ports/save">
                    <table class="table table-striped table-condensed">
                        <thead><tr><th>Port</th><th>Alias</th><th>Status</th><th>Port Group</th></tr></thead>
                        <tbody>''' + table_rows + '''</tbody>
                    </table>
                    <button type="submit" class="btn btn-primary btn-sm">Save</button>
                </form>
            </div>
        </div>
    ''', user))


@app.route('/device/<int:device_id>/edit-ports/save', methods=['POST'])
@require_auth
def save_port_settings(device_id):
    db = get_db()
    ports = db.execute('SELECT * FROM ports WHERE device_id = ?', (device_id,)).fetchall()
    for port in ports:
        key = 'port_groups_' + str(port['port_id'])
        groups = request.form.getlist(key)
        db.execute('DELETE FROM port_group_port WHERE port_id = ?', (port['port_id'],))
        for gid in groups:
            try:
                db.execute('INSERT INTO port_group_port (port_group_id, port_id) VALUES (?, ?)', (int(gid), port['port_id']))
            except:
                pass
    db.commit()
    return redirect('/device/' + str(device_id) + '/edit-ports')


@app.route('/port-groups')
@require_auth
def port_groups_list():
    db = get_db()
    user = get_current_user()
    groups = db.execute('SELECT pg.*, COUNT(pgp.port_id) as port_count FROM port_groups pg LEFT JOIN port_group_port pgp ON pg.id = pgp.port_group_id GROUP BY pg.id').fetchall()

    rows = ''
    for g in groups:
        rows += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td><a href="/port-groups/{0}/edit" class="btn btn-xs btn-default">Edit</a> <a href="/port-groups/{0}/delete" class="btn btn-xs btn-danger" onclick="return confirm(\'Delete this group?\')">Delete</a></td></tr>'.format(
            g['id'], g['name'], g['port_count']
        )

    return make_response(render_page('Port Groups', '''
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Port Groups
                    <a href="/port-groups/create" class="btn btn-primary btn-xs pull-right">Create Port Group</a>
                </h3>
            </div>
            <div class="panel-body">
                <table class="table table-striped table-condensed">
                    <thead><tr><th>ID</th><th>Name</th><th>Ports</th><th>Actions</th></tr></thead>
                    <tbody>''' + rows + '''</tbody>
                </table>
            </div>
        </div>
    ''', user))


@app.route('/port-groups/create', methods=['GET', 'POST'])
@require_auth
def port_group_create():
    user = get_current_user()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('desc', '').strip()
        if not name:
            return make_response(render_page('Create Port Group', '''
                <div class="alert alert-danger">Name is required.</div>
            ''' + port_group_form('', ''), user))

        db = get_db()
        db.execute('INSERT INTO port_groups (name, desc_text) VALUES (?, ?)', (name, desc))
        db.commit()

        # Simulate admin reviewing port settings after group creation
        new_group_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        # Auto-assign to first port of first device for visibility
        first_port = db.execute('SELECT port_id FROM ports LIMIT 1').fetchone()
        if first_port:
            try:
                db.execute('INSERT INTO port_group_port (port_group_id, port_id) VALUES (?, ?)',
                           (new_group_id, first_port['port_id']))
                db.commit()
            except:
                pass

        trigger_admin_review()
        return redirect('/port-groups')

    return make_response(render_page('Create Port Group', port_group_form('', ''), user))


@app.route('/port-groups/<int:group_id>/edit', methods=['GET', 'POST'])
@require_auth
def port_group_edit(group_id):
    db = get_db()
    user = get_current_user()
    group = db.execute('SELECT * FROM port_groups WHERE id = ?', (group_id,)).fetchone()
    if not group:
        return make_response('Port Group not found', 404)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('desc', '').strip()
        if name:
            db.execute('UPDATE port_groups SET name = ?, desc_text = ? WHERE id = ?', (name, desc, group_id))
            db.commit()
            trigger_admin_review()
        return redirect('/port-groups')

    return make_response(render_page('Edit Port Group', port_group_form(group['name'], group['desc_text'] or ''), user))


@app.route('/port-groups/<int:group_id>/delete')
@require_auth
def port_group_delete(group_id):
    db = get_db()
    db.execute('DELETE FROM port_group_port WHERE port_group_id = ?', (group_id,))
    db.execute('DELETE FROM port_groups WHERE id = ?', (group_id,))
    db.commit()
    return redirect('/port-groups')


@app.route('/port-groups/<int:group_id>/assign', methods=['POST'])
@require_auth
def port_group_assign(group_id):
    db = get_db()
    port_id = request.form.get('port_id')
    if port_id:
        try:
            db.execute('INSERT INTO port_group_port (port_group_id, port_id) VALUES (?, ?)',
                       (group_id, int(port_id)))
            db.commit()
        except:
            pass
    return redirect('/port-groups')


@app.route('/settings')
@require_auth
def settings():
    user = get_current_user()
    return make_response(render_page('Global Settings', '''
        <div class="panel panel-default">
            <div class="panel-heading"><h3 class="panel-title">Global Settings</h3></div>
            <div class="panel-body">
                <dl class="dl-horizontal">
                    <dt>Poller Interval</dt><dd>300 seconds</dd>
                    <dt>Discovery Threads</dt><dd>4</dd>
                    <dt>Alert Transport</dt><dd>Email</dd>
                    <dt>Syslog Enabled</dt><dd>Yes</dd>
                    <dt>SNMP Version</dt><dd>v2c</dd>
                    <dt>Auth Backend</dt><dd>MySQL</dd>
                </dl>
            </div>
        </div>
    ''', user))


# API endpoint for table data (mirrors EditPortsController)
@app.route('/ajax/table/edit-ports', methods=['GET'])
@require_auth
def ajax_edit_ports():
    device_id = request.args.get('device_id', 1, type=int)
    db = get_db()
    ports = db.execute('SELECT * FROM ports WHERE device_id = ?', (device_id,)).fetchall()

    data = []
    for port in ports:
        assigned = db.execute(
            'SELECT pg.* FROM port_groups pg JOIN port_group_port pgp ON pg.id = pgp.port_group_id WHERE pgp.port_id = ?',
            (port['port_id'],)).fetchall()

        port_group_options = ''
        for group in assigned:
            # Render group name in option tag
            port_group_options += '<option value="' + str(group['id']) + '" selected>' + group['name'] + '</option>'

        data.append({
            'ifName': port['ifName'],
            'ifAlias': port['ifAlias'] or '',
            'ifOperStatus': port['ifOperStatus'],
            'portGroup': '<div class="form-group has-feedback"><select class="form-control" multiple>' + port_group_options + '</select></div>'
        })

    return jsonify({'data': data})


def port_group_form(name_val, desc_val):
    return '''
        <div class="panel panel-default">
            <div class="panel-heading"><h3 class="panel-title">Port Group</h3></div>
            <div class="panel-body">
                <form method="post">
                    <div class="form-group">
                        <label for="name">Name</label>
                        <input type="text" class="form-control" id="name" name="name" value="''' + name_val.replace('"', '&quot;') + '''" required>
                    </div>
                    <div class="form-group">
                        <label for="desc">Description</label>
                        <input type="text" class="form-control" id="desc" name="desc" value="''' + desc_val.replace('"', '&quot;') + '''">
                    </div>
                    <button type="submit" class="btn btn-primary">Save</button>
                    <a href="/port-groups" class="btn btn-default">Cancel</a>
                </form>
            </div>
        </div>
    '''


def render_page(title, content, user=None):
    username = user['username'] if user else ''
    nav_items = '''
        <li><a href="/devices">Devices</a></li>
        <li><a href="/port-groups">Port Groups</a></li>
        <li><a href="/settings">Settings</a></li>
    ''' if user else ''

    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>''' + title + ''' - LibreNMS</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body { background-color: #060606; color: #c5c5c5; padding-top: 50px; }
        .navbar { background-color: #1a1a2e; border-color: #333; }
        .navbar-brand { color: #e73c3e !important; font-weight: bold; }
        .navbar-nav > li > a { color: #c5c5c5 !important; }
        .navbar-nav > li > a:hover { color: #e73c3e !important; }
        .panel { background-color: #1a1a2e; border-color: #333; }
        .panel-heading { background-color: #16213e !important; border-color: #333; }
        .panel-title { color: #e73c3e; }
        .table { color: #c5c5c5; }
        .table-striped > tbody > tr:nth-of-type(odd) { background-color: #16213e; }
        .form-control { background-color: #16213e; border-color: #333; color: #fff; }
        a { color: #5dade2; }
        .container-fluid { max-width: 1200px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-default navbar-fixed-top">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/devices">LibreNMS</a>
            </div>
            <ul class="nav navbar-nav">''' + nav_items + '''</ul>
            ''' + ('<ul class="nav navbar-nav navbar-right"><li><a href="/logout"><i class="glyphicon glyphicon-log-out"></i> ' + username + '</a></li></ul>' if user else '') + '''
        </div>
    </nav>
    <div class="container-fluid">
        ''' + content + '''
    </div>
</body>
</html>'''


def trigger_admin_review():
    """Admin periodic review of port settings changes"""
    def do_review():
        time.sleep(3)
        try:
            flag = open('/app/flag.txt').read().strip()
            base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
            # Admin reviews port settings for device 1
            proc = subprocess.Popen(
                ["timeout", "10", "phantomjs", "--ignore-ssl-errors=true", "/app/admin_review.js",
                 base_url, flag],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate()
        except Exception as e:
            pass
    t = threading.Thread(target=do_review)
    t.daemon = True
    t.start()


@app.route('/collect', methods=['GET', 'POST'])
def collect_data():
    """Webhook endpoint for alert notifications and integrations"""
    data = request.args.get('data', '') or request.form.get('data', '') or ''
    if data:
        try:
            with open('/app/data/webhook_log.txt', 'a') as f:
                f.write(data + '\n')
        except:
            pass
    return 'OK'


@app.route('/collect/view')
@require_auth
def view_collected():
    """View webhook/alert notification log"""
    user = get_current_user()
    try:
        with open('/app/data/webhook_log.txt', 'r') as f:
            log_data = f.read()
    except:
        log_data = ''

    return make_response(render_page('Webhook Log', '''
        <div class="panel panel-default">
            <div class="panel-heading"><h3 class="panel-title">Alert Notification Log</h3></div>
            <div class="panel-body">
                <pre>''' + log_data.replace('<', '&lt;').replace('>', '&gt;') + '''</pre>
                <form method="post" action="/collect/clear">
                    <button type="submit" class="btn btn-danger btn-xs">Clear Log</button>
                </form>
            </div>
        </div>
    ''', user))


@app.route('/collect/clear', methods=['POST'])
@require_auth
def clear_collected():
    try:
        with open('/app/data/webhook_log.txt', 'w') as f:
            f.write('')
    except:
        pass
    return redirect('/collect/view')


@app.route('/ping')
def health_ping():
    return 'OK'


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
