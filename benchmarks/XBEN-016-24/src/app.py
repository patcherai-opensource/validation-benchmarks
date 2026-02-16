# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for, session, jsonify
import string
import subprocess
import os
import re
import json
import sqlite3
import sys
import hashlib
import time
import cgi

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_value = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24).encode('hex')

phantom = Phantom()

DB_PATH = '/app/data/netwatch.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'viewer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT NOT NULL,
        os_type TEXT DEFAULT 'linux',
        status TEXT DEFAULT 'up',
        uptime INTEGER DEFAULT 0,
        last_polled TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS interfaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER NOT NULL,
        if_name TEXT NOT NULL,
        if_alias TEXT DEFAULT '',
        if_speed INTEGER DEFAULT 1000,
        if_admin_status TEXT DEFAULT 'up',
        if_oper_status TEXT DEFAULT 'up',
        disabled INTEGER DEFAULT 0,
        FOREIGN KEY(device_id) REFERENCES devices(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS interface_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT DEFAULT ''
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS interface_group_membership (
        interface_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        PRIMARY KEY(interface_id, group_id),
        FOREIGN KEY(interface_id) REFERENCES interfaces(id),
        FOREIGN KEY(group_id) REFERENCES interface_groups(id)
    )''')
    # Seed default admin user (password: admin)
    admin_hash = hashlib.sha256('admin').hexdigest()
    try:
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  ('admin', admin_hash, 'admin'))
    except sqlite3.IntegrityError:
        pass
    # Seed some devices and interfaces
    try:
        c.execute("INSERT INTO devices (hostname, os_type, status, uptime) VALUES (?, ?, ?, ?)",
                  ('core-switch-01.internal', 'cisco-ios', 'up', 8640000))
        c.execute("INSERT INTO devices (hostname, os_type, status, uptime) VALUES (?, ?, ?, ?)",
                  ('edge-router-02.internal', 'junos', 'up', 4320000))
        c.execute("INSERT INTO devices (hostname, os_type, status, uptime) VALUES (?, ?, ?, ?)",
                  ('fw-01.internal', 'panos', 'up', 2160000))
        dev1_id = 1
        dev2_id = 2
        dev3_id = 3
        ifaces = [
            (dev1_id, 'GigabitEthernet0/0', 'Uplink to ISP', 10000, 'up', 'up'),
            (dev1_id, 'GigabitEthernet0/1', 'Server VLAN', 1000, 'up', 'up'),
            (dev1_id, 'GigabitEthernet0/2', 'Management', 1000, 'up', 'down'),
            (dev1_id, 'GigabitEthernet0/3', 'User VLAN', 1000, 'up', 'up'),
            (dev2_id, 'ge-0/0/0', 'WAN Link', 10000, 'up', 'up'),
            (dev2_id, 'ge-0/0/1', 'LAN Trunk', 1000, 'up', 'up'),
            (dev2_id, 'ge-0/0/2', 'DMZ', 1000, 'up', 'up'),
            (dev3_id, 'ethernet1/1', 'Outside', 10000, 'up', 'up'),
            (dev3_id, 'ethernet1/2', 'Inside', 1000, 'up', 'up'),
            (dev3_id, 'ethernet1/3', 'DMZ Zone', 1000, 'down', 'down'),
        ]
        for iface in ifaces:
            c.execute("INSERT INTO interfaces (device_id, if_name, if_alias, if_speed, if_admin_status, if_oper_status) VALUES (?, ?, ?, ?, ?, ?)", iface)
        # Create a default interface group
        c.execute("INSERT INTO interface_groups (name, description) VALUES (?, ?)",
                  ('Uplinks', 'Uplink interfaces'))
        c.execute("INSERT INTO interface_group_membership (interface_id, group_id) VALUES (?, ?)", (1, 1))
        c.execute("INSERT INTO interface_group_membership (interface_id, group_id) VALUES (?, ?)", (5, 1))
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()

init_db()

# --- Auth helpers ---

def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    if 'user_id' in session:
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        db.close()
        return user
    return None

# --- Layout ---

LAYOUT_HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - NetWatch NMS</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #1a1c2e; color: #e0e0e0; }}
.navbar {{ background: #252840; padding: 10px 20px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #3a3d5c; }}
.navbar .brand {{ color: #4fc3f7; font-size: 18px; font-weight: bold; text-decoration: none; }}
.navbar .nav-links {{ display: flex; gap: 15px; align-items: center; }}
.navbar .nav-links a {{ color: #b0b0b0; text-decoration: none; font-size: 14px; padding: 5px 10px; border-radius: 4px; }}
.navbar .nav-links a:hover {{ color: #fff; background: #3a3d5c; }}
.navbar .nav-links a.active {{ color: #4fc3f7; }}
.container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
.panel {{ background: #252840; border-radius: 8px; border: 1px solid #3a3d5c; margin-bottom: 20px; }}
.panel-header {{ padding: 15px 20px; border-bottom: 1px solid #3a3d5c; font-size: 16px; font-weight: 600; }}
.panel-body {{ padding: 20px; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 10px 15px; text-align: left; border-bottom: 1px solid #3a3d5c; font-size: 14px; }}
th {{ background: #1e2038; color: #888; font-weight: 500; text-transform: uppercase; font-size: 12px; }}
tr:hover {{ background: #2a2d4a; }}
.btn {{ display: inline-block; padding: 6px 16px; border-radius: 4px; font-size: 14px; text-decoration: none; cursor: pointer; border: none; }}
.btn-primary {{ background: #4fc3f7; color: #1a1c2e; }}
.btn-primary:hover {{ background: #29b6f6; }}
.btn-danger {{ background: #ef5350; color: #fff; }}
.btn-danger:hover {{ background: #e53935; }}
.btn-sm {{ padding: 4px 10px; font-size: 12px; }}
.form-group {{ margin-bottom: 15px; }}
.form-group label {{ display: block; margin-bottom: 5px; color: #888; font-size: 14px; }}
.form-control {{ width: 100%; padding: 8px 12px; background: #1a1c2e; border: 1px solid #3a3d5c; border-radius: 4px; color: #e0e0e0; font-size: 14px; }}
.form-control:focus {{ outline: none; border-color: #4fc3f7; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
.badge-up {{ background: #43a047; color: #fff; }}
.badge-down {{ background: #ef5350; color: #fff; }}
.alert {{ padding: 12px 16px; border-radius: 4px; margin-bottom: 15px; font-size: 14px; }}
.alert-success {{ background: #1b5e20; border: 1px solid #2e7d32; color: #a5d6a7; }}
.alert-error {{ background: #b71c1c; border: 1px solid #c62828; color: #ef9a9a; }}
.login-wrapper {{ display: flex; justify-content: center; align-items: center; min-height: 80vh; }}
.login-box {{ background: #252840; border-radius: 8px; border: 1px solid #3a3d5c; padding: 40px; width: 400px; }}
.login-box h2 {{ text-align: center; margin-bottom: 25px; color: #4fc3f7; }}
select {{ padding: 6px 10px; background: #1a1c2e; border: 1px solid #3a3d5c; color: #e0e0e0; border-radius: 4px; font-size: 13px; }}
select[multiple] {{ min-height: 60px; }}
.status-indicator {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }}
.status-up {{ background: #43a047; }}
.status-down {{ background: #ef5350; }}
</style>
</head>
<body>'''

NAV_TEMPLATE = '''<nav class="navbar">
<a href="/" class="brand">NetWatch NMS</a>
<div class="nav-links">
<a href="/overview">Overview</a>
<a href="/devices">Devices</a>
<a href="/interface-groups">Interface Groups</a>
<a href="/alerts">Alerts</a>
<a href="/logout">Logout ({username})</a>
</div>
</nav>'''

LAYOUT_FOOT = '''</body></html>'''

def render_page(title, content, user=None):
    head = LAYOUT_HEAD.format(title=title)
    nav = ''
    if user:
        nav = NAV_TEMPLATE.format(username=user['username'])
    return head + nav + '<div class="container">' + content + '</div>' + LAYOUT_FOOT

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/overview')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_hash = hashlib.sha256(password.encode('utf-8') if isinstance(password, unicode) else password).hexdigest()
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?",
                          (username, password_hash)).fetchone()
        db.close()
        if user:
            session['user_id'] = user['id']
            return redirect('/overview')
        else:
            content = '''<div class="login-wrapper"><div class="login-box">
            <h2>NetWatch NMS</h2>
            <div class="alert alert-error">Invalid credentials</div>
            <form method="POST">
            <div class="form-group"><label>Username</label><input class="form-control" name="username" type="text"></div>
            <div class="form-group"><label>Password</label><input class="form-control" name="password" type="password"></div>
            <button class="btn btn-primary" type="submit" style="width:100%">Sign In</button>
            </form></div></div>'''
            return LAYOUT_HEAD.format(title='Login') + content + LAYOUT_FOOT

    content = '''<div class="login-wrapper"><div class="login-box">
    <h2>NetWatch NMS</h2>
    <form method="POST">
    <div class="form-group"><label>Username</label><input class="form-control" name="username" type="text"></div>
    <div class="form-group"><label>Password</label><input class="form-control" name="password" type="password"></div>
    <button class="btn btn-primary" type="submit" style="width:100%">Sign In</button>
    </form></div></div>'''
    return LAYOUT_HEAD.format(title='Login') + content + LAYOUT_FOOT

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/overview')
@require_auth
def overview():
    user = get_current_user()
    db = get_db()
    devices = db.execute("SELECT * FROM devices").fetchall()
    total_interfaces = db.execute("SELECT COUNT(*) as cnt FROM interfaces").fetchone()['cnt']
    up_count = db.execute("SELECT COUNT(*) as cnt FROM devices WHERE status='up'").fetchone()['cnt']
    down_count = db.execute("SELECT COUNT(*) as cnt FROM devices WHERE status!='up'").fetchone()['cnt']
    alerts_count = db.execute("SELECT COUNT(*) as cnt FROM interfaces WHERE if_oper_status='down' AND if_admin_status='up'").fetchone()['cnt']
    db.close()

    content = '''
    <div class="panel"><div class="panel-header">System Overview</div><div class="panel-body">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:15px;">
    <div class="panel" style="margin:0"><div class="panel-body" style="text-align:center"><div style="font-size:24px;color:#4fc3f7">{devices}</div><div style="color:#888;font-size:12px">DEVICES</div></div></div>
    <div class="panel" style="margin:0"><div class="panel-body" style="text-align:center"><div style="font-size:24px;color:#43a047">{up}</div><div style="color:#888;font-size:12px">UP</div></div></div>
    <div class="panel" style="margin:0"><div class="panel-body" style="text-align:center"><div style="font-size:24px;color:#ef5350">{down}</div><div style="color:#888;font-size:12px">DOWN</div></div></div>
    <div class="panel" style="margin:0"><div class="panel-body" style="text-align:center"><div style="font-size:24px;color:#ff9800">{alerts}</div><div style="color:#888;font-size:12px">ALERTS</div></div></div>
    </div></div></div>
    <div class="panel"><div class="panel-header">Devices</div><div class="panel-body">
    <table><thead><tr><th>Hostname</th><th>OS</th><th>Status</th><th>Uptime</th></tr></thead><tbody>'''.format(
        devices=len(devices), up=up_count, down=down_count, alerts=alerts_count)

    for d in devices:
        badge = '<span class="badge badge-up">UP</span>' if d['status'] == 'up' else '<span class="badge badge-down">DOWN</span>'
        uptime_days = d['uptime'] / 86400 if d['uptime'] else 0
        content += '<tr><td><a href="/devices/{id}/ports" style="color:#4fc3f7;text-decoration:none">{hostname}</a></td><td>{os}</td><td>{badge}</td><td>{uptime}d</td></tr>'.format(
            id=d['id'], hostname=d['hostname'], os=d['os_type'], badge=badge, uptime=uptime_days)

    content += '</tbody></table></div></div>'
    return render_page('Overview', content, user)

@app.route('/devices')
@require_auth
def devices_list():
    user = get_current_user()
    db = get_db()
    devices = db.execute("SELECT d.*, (SELECT COUNT(*) FROM interfaces WHERE device_id=d.id) as iface_count FROM devices d").fetchall()
    db.close()
    content = '''<div class="panel"><div class="panel-header">Devices</div><div class="panel-body">
    <table><thead><tr><th>ID</th><th>Hostname</th><th>OS</th><th>Interfaces</th><th>Status</th><th>Actions</th></tr></thead><tbody>'''
    for d in devices:
        badge = '<span class="badge badge-up">UP</span>' if d['status'] == 'up' else '<span class="badge badge-down">DOWN</span>'
        content += '<tr><td>{id}</td><td>{hostname}</td><td>{os}</td><td>{ifaces}</td><td>{badge}</td><td><a href="/devices/{id}/ports" class="btn btn-primary btn-sm">Ports</a></td></tr>'.format(
            id=d['id'], hostname=d['hostname'], os=d['os_type'], ifaces=d['iface_count'], badge=badge)
    content += '</tbody></table></div></div>'
    return render_page('Devices', content, user)

@app.route('/devices/<int:device_id>/ports')
@require_auth
def device_ports(device_id):
    user = get_current_user()
    db = get_db()
    device = db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
    if not device:
        db.close()
        return render_page('Not Found', '<div class="alert alert-error">Device not found</div>', user), 404

    interfaces = db.execute("SELECT * FROM interfaces WHERE device_id = ?", (device_id,)).fetchall()
    all_groups = db.execute("SELECT * FROM interface_groups ORDER BY name").fetchall()
    db.close()

    content = '<div class="panel"><div class="panel-header">{hostname} - Port Settings</div><div class="panel-body">'.format(hostname=device['hostname'])
    content += '<div style="margin-bottom:15px"><a href="/devices/{id}/verify-config" class="btn btn-primary">Verify Configuration</a></div>'.format(id=device_id)
    content += '<table><thead><tr><th>ifIndex</th><th>ifName</th><th>Admin</th><th>Oper</th><th>Speed</th><th>Alias</th><th>Interface Group</th></tr></thead><tbody>'

    for iface in interfaces:
        admin_badge = '<span class="badge badge-up">{}</span>'.format(iface['if_admin_status']) if iface['if_admin_status'] == 'up' else '<span class="badge badge-down">{}</span>'.format(iface['if_admin_status'])
        oper_badge = '<span class="badge badge-up">{}</span>'.format(iface['if_oper_status']) if iface['if_oper_status'] == 'up' else '<span class="badge badge-down">{}</span>'.format(iface['if_oper_status'])

        # Build group select - THIS IS THE VULNERABLE SINK
        # Group names are rendered directly without escaping (mirrors the LibreNMS vulnerability)
        group_options = ''
        db2 = get_db()
        memberships = db2.execute("SELECT g.id, g.name FROM interface_groups g INNER JOIN interface_group_membership m ON g.id = m.group_id WHERE m.interface_id = ?", (iface['id'],)).fetchall()
        db2.close()
        for grp in memberships:
            group_options += '<option value="' + str(grp['id']) + '" selected>' + grp['name'] + '</option>'

        for grp in all_groups:
            already = any(m['id'] == grp['id'] for m in memberships)
            if not already:
                group_options += '<option value="' + str(grp['id']) + '">' + grp['name'] + '</option>'

        group_select = '<select class="form-control" name="iface_group_{id}[]" multiple>{opts}</select>'.format(
            id=iface['id'], opts=group_options)

        content += '<tr><td>{idx}</td><td>{name}</td><td>{admin}</td><td>{oper}</td><td>{speed}</td><td>{alias}</td><td>{groups}</td></tr>'.format(
            idx=iface['id'], name=iface['if_name'], admin=admin_badge, oper=oper_badge,
            speed=iface['if_speed'], alias=iface['if_alias'], groups=group_select)

    content += '</tbody></table></div></div>'
    return render_page(device['hostname'] + ' - Ports', content, user)


# --- Interface Groups (renamed from Port Groups) ---

@app.route('/interface-groups')
@require_auth
def interface_groups_index():
    user = get_current_user()
    db = get_db()
    groups = db.execute('''SELECT g.*, (SELECT COUNT(*) FROM interface_group_membership WHERE group_id=g.id) as member_count
                           FROM interface_groups g ORDER BY g.name''').fetchall()
    db.close()
    content = '''<div class="panel"><div class="panel-header">Interface Groups</div><div class="panel-body">
    <div style="margin-bottom:15px"><a href="/interface-groups/create" class="btn btn-primary">New Interface Group</a></div>
    <table><thead><tr><th>Name</th><th>Description</th><th>Interfaces</th><th>Actions</th></tr></thead><tbody>'''
    for g in groups:
        content += '<tr><td>{name}</td><td>{desc}</td><td>{count}</td><td><a href="/interface-groups/{id}/edit" class="btn btn-primary btn-sm">Edit</a> <a href="/interface-groups/{id}/delete" class="btn btn-danger btn-sm" onclick="return confirm(\'Delete this group?\')">Delete</a></td></tr>'.format(
            id=g['id'], name=cgi.escape(g['name']), desc=cgi.escape(g['description']), count=g['member_count'])
    content += '</tbody></table></div></div>'
    return render_page('Interface Groups', content, user)

@app.route('/interface-groups/create', methods=['GET', 'POST'])
@require_auth
def interface_group_create():
    user = get_current_user()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('desc', '').strip()
        if not name:
            content = '''<div class="panel"><div class="panel-header">Create Interface Group</div><div class="panel-body">
            <div class="alert alert-error">Name is required</div>
            <form method="POST">
            <div class="form-group"><label>Name</label><input class="form-control" name="name" type="text"></div>
            <div class="form-group"><label>Description</label><input class="form-control" name="desc" type="text"></div>
            <button class="btn btn-primary" type="submit">Save</button>
            <a href="/interface-groups" class="btn btn-danger">Cancel</a>
            </form></div></div>'''
            return render_page('Create Interface Group', content, user)

        db = get_db()
        try:
            db.execute("INSERT INTO interface_groups (name, description) VALUES (?, ?)", (name, desc))
            db.commit()
        except sqlite3.IntegrityError:
            db.close()
            content = '''<div class="panel"><div class="panel-header">Create Interface Group</div><div class="panel-body">
            <div class="alert alert-error">A group with this name already exists</div>
            <form method="POST">
            <div class="form-group"><label>Name</label><input class="form-control" name="name" type="text"></div>
            <div class="form-group"><label>Description</label><input class="form-control" name="desc" type="text"></div>
            <button class="btn btn-primary" type="submit">Save</button>
            <a href="/interface-groups" class="btn btn-danger">Cancel</a>
            </form></div></div>'''
            return render_page('Create Interface Group', content, user)
        db.close()
        return redirect('/interface-groups')

    content = '''<div class="panel"><div class="panel-header">Create Interface Group</div><div class="panel-body">
    <form method="POST">
    <div class="form-group"><label>Name</label><input class="form-control" name="name" type="text"></div>
    <div class="form-group"><label>Description</label><input class="form-control" name="desc" type="text"></div>
    <button class="btn btn-primary" type="submit">Save</button>
    <a href="/interface-groups" class="btn btn-danger">Cancel</a>
    </form></div></div>'''
    return render_page('Create Interface Group', content, user)

@app.route('/interface-groups/<int:group_id>/edit', methods=['GET', 'POST'])
@require_auth
def interface_group_edit(group_id):
    user = get_current_user()
    db = get_db()
    group = db.execute("SELECT * FROM interface_groups WHERE id = ?", (group_id,)).fetchone()
    if not group:
        db.close()
        return render_page('Not Found', '<div class="alert alert-error">Group not found</div>', user), 404

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('desc', '').strip()
        if name:
            try:
                db.execute("UPDATE interface_groups SET name = ?, description = ? WHERE id = ?", (name, desc, group_id))
                db.commit()
            except sqlite3.IntegrityError:
                pass
        db.close()
        return redirect('/interface-groups')

    content = '''<div class="panel"><div class="panel-header">Edit Interface Group</div><div class="panel-body">
    <form method="POST">
    <div class="form-group"><label>Name</label><input class="form-control" name="name" type="text" value="{name}"></div>
    <div class="form-group"><label>Description</label><input class="form-control" name="desc" type="text" value="{desc}"></div>
    <button class="btn btn-primary" type="submit">Save</button>
    <a href="/interface-groups" class="btn btn-danger">Cancel</a>
    </form></div></div>'''.format(name=cgi.escape(group['name'], quote=True), desc=cgi.escape(group['description'], quote=True))
    db.close()
    return render_page('Edit Interface Group', content, user)

@app.route('/interface-groups/<int:group_id>/delete')
@require_auth
def interface_group_delete(group_id):
    db = get_db()
    db.execute("DELETE FROM interface_group_membership WHERE group_id = ?", (group_id,))
    db.execute("DELETE FROM interface_groups WHERE id = ?", (group_id,))
    db.commit()
    db.close()
    return redirect('/interface-groups')

@app.route('/interface-groups/<int:group_id>/assign', methods=['POST'])
@require_auth
def interface_group_assign(group_id):
    interface_id = request.form.get('interface_id', type=int)
    if interface_id:
        db = get_db()
        try:
            db.execute("INSERT INTO interface_group_membership (interface_id, group_id) VALUES (?, ?)",
                       (interface_id, group_id))
            db.commit()
        except sqlite3.IntegrityError:
            pass
        db.close()
    return redirect(request.referrer or '/interface-groups')


# --- Alerts page ---

@app.route('/alerts')
@require_auth
def alerts_page():
    user = get_current_user()
    db = get_db()
    alerts = db.execute('''SELECT i.*, d.hostname FROM interfaces i
                           JOIN devices d ON d.id = i.device_id
                           WHERE i.if_oper_status = 'down' AND i.if_admin_status = 'up' ''').fetchall()
    db.close()
    content = '''<div class="panel"><div class="panel-header">Active Alerts</div><div class="panel-body">
    <table><thead><tr><th>Device</th><th>Interface</th><th>Admin Status</th><th>Oper Status</th><th>Severity</th></tr></thead><tbody>'''
    for a in alerts:
        content += '<tr><td>{host}</td><td>{iface}</td><td><span class="badge badge-up">up</span></td><td><span class="badge badge-down">down</span></td><td><span class="badge badge-down">Critical</span></td></tr>'.format(
            host=a['hostname'], iface=a['if_name'])
    if not alerts:
        content += '<tr><td colspan="5" style="text-align:center;color:#888">No active alerts</td></tr>'
    content += '</tbody></table></div></div>'
    return render_page('Alerts', content, user)


# --- XSS Verification Endpoint (simulates admin viewing the page) ---

@app.route('/devices/<int:device_id>/verify-config')
@require_auth
def verify_device_config(device_id):
    """Admin action that renders the port settings page through the headless browser
       to verify configuration. This is the trigger for stored XSS."""
    user = get_current_user()
    db = get_db()
    device = db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
    db.close()
    if not device:
        return render_page('Error', '<div class="alert alert-error">Device not found</div>', user), 404

    # Build the page HTML as it would be rendered for port settings
    page_html = build_port_settings_html(device_id)

    # Use PhantomJS to render and check for XSS
    proc = subprocess.Popen(["timeout", "8", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn

    result = ''
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    if result == 'XSS':
        content = '<div class="panel"><div class="panel-header">Configuration Verification</div><div class="panel-body">'
        content += '<div class="alert alert-success">Configuration verified for {hostname}.</div>'.format(hostname=device['hostname'])
        content += '<p style="margin-top:10px;font-family:monospace;background:#1a1c2e;padding:10px;border-radius:4px;border:1px solid #3a3d5c;">{flag}</p>'.format(flag=flag_value)
        content += '</div></div>'
    else:
        content = '<div class="panel"><div class="panel-header">Configuration Verification</div><div class="panel-body">'
        content += '<div class="alert alert-success">Configuration verified for {hostname}. All port settings are valid.</div>'.format(hostname=device['hostname'])
        content += '</div></div>'

    return render_page('Verify Config - ' + device['hostname'], content, user)


def build_port_settings_html(device_id):
    """Build the HTML that gets rendered by PhantomJS - mirrors the device_ports view"""
    db = get_db()
    device = db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
    interfaces = db.execute("SELECT * FROM interfaces WHERE device_id = ?", (device_id,)).fetchall()
    all_groups = db.execute("SELECT * FROM interface_groups ORDER BY name").fetchall()

    html = '''<html><head><title>{hostname} - Port Settings</title></head><body>
    <h2>{hostname} - Port Settings</h2><table border="1"><tr><th>ifName</th><th>Admin</th><th>Oper</th><th>Speed</th><th>Interface Group</th></tr>'''.format(
        hostname=device['hostname'])

    for iface in interfaces:
        # Build group select - vulnerable: group names rendered without escaping
        group_options = ''
        memberships = db.execute("SELECT g.id, g.name FROM interface_groups g INNER JOIN interface_group_membership m ON g.id = m.group_id WHERE m.interface_id = ?", (iface['id'],)).fetchall()
        for grp in memberships:
            group_options += '<option value="' + str(grp['id']) + '" selected>' + grp['name'] + '</option>'
        for grp in all_groups:
            already = any(m['id'] == grp['id'] for m in memberships)
            if not already:
                group_options += '<option value="' + str(grp['id']) + '">' + grp['name'] + '</option>'

        group_select = '<select name="iface_group_{id}[]" multiple>{opts}</select>'.format(
            id=iface['id'], opts=group_options)

        html += '<tr><td>{name}</td><td>{admin}</td><td>{oper}</td><td>{speed}</td><td>{groups}</td></tr>'.format(
            name=iface['if_name'], admin=iface['if_admin_status'], oper=iface['if_oper_status'],
            speed=iface['if_speed'], groups=group_select)

    html += '</table></body></html>'
    db.close()
    return html


# --- Health check ---

@app.route('/ping')
def health_ping():
    return 'OK', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
