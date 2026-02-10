# encoding=utf8

from flask import Flask, request, make_response, redirect, session
import os
import re
import json
import sqlite3
import sys
import HTMLParser
import urllib2

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')

DATABASE = 'servers.db'
FLAG_VALUE = None

def get_flag():
    global FLAG_VALUE
    if FLAG_VALUE is None:
        FLAG_VALUE = open('secret.txt').read().strip()
    return FLAG_VALUE

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS game_servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        game_type TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS server_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        field_name TEXT,
        field_value TEXT,
        FOREIGN KEY (server_id) REFERENCES game_servers(id)
    )''')
    conn.commit()
    conn.close()

init_db()

ADMIN_PASSWORD = 'lgsl_admin_2024_secure'

def is_admin():
    return session.get('admin') == True

@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM game_servers WHERE status = 'active' ORDER BY created_at DESC")
    servers = c.fetchall()
    conn.close()
    
    servers_html = ""
    for server in servers:
        servers_html += '''
        <tr>
            <td><a href="/server/{0}">{1}</a></td>
            <td>{2}</td>
            <td>{3}</td>
            <td><span class="status-active">Online</span></td>
        </tr>
        '''.format(server['id'], server['name'], server['address'], server['game_type'] or 'Unknown')
    
    if not servers_html:
        servers_html = '<tr><td colspan="4" style="text-align:center;">No servers registered yet</td></tr>'
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Live Game Server List</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #4ecca3; }}
        .nav {{ background: #16213e; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
        .nav a {{ color: #4ecca3; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 5px; overflow: hidden; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #1a1a2e; }}
        th {{ background: #0f3460; color: #4ecca3; }}
        tr:hover {{ background: #1a1a2e; }}
        a {{ color: #4ecca3; }}
        .status-active {{ color: #4ecca3; }}
        .btn {{ background: #4ecca3; color: #1a1a2e; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }}
        .btn:hover {{ background: #3db892; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/register">Register Server</a>
            <a href="/admin">Admin Panel</a>
        </div>
        <h1>Live Game Server List</h1>
        <p>Browse and discover game servers from our community.</p>
        <table>
            <thead>
                <tr>
                    <th>Server Name</th>
                    <th>Address</th>
                    <th>Game Type</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {0}
            </tbody>
        </table>
    </div>
</body>
</html>'''.format(servers_html)


def crawl_server_info(server_id, address):
    conn = get_db()
    c = conn.cursor()
    try:
        req = urllib2.Request(address)
        req.add_header('User-Agent', 'LGSL/1.0 Server Crawler')
        response = urllib2.urlopen(req, timeout=10)
        data = json.loads(response.read())
        
        c.execute("DELETE FROM server_info WHERE server_id = ?", (server_id,))
        
        for field, value in data.items():
            c.execute("INSERT INTO server_info (server_id, field_name, field_value) VALUES (?, ?, ?)",
                     (server_id, str(field), str(value)))
        
        conn.commit()
        return True
    except Exception as e:
        logging.error("Failed to crawl server {}: {}".format(server_id, str(e)))
        return False
    finally:
        conn.close()


@app.route('/register', methods=['GET', 'POST'])
def register_server():
    message = ""
    if request.method == 'POST':
        name = request.form.get('name', '')
        address = request.form.get('address', '')
        game_type = request.form.get('game_type', '')
        
        if not name or not address:
            message = '<div class="error">Name and address are required</div>'
        else:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO game_servers (name, address, game_type, status) VALUES (?, ?, ?, 'active')",
                     (name, address, game_type))
            server_id = c.lastrowid
            conn.commit()
            conn.close()
            
            if crawl_server_info(server_id, address):
                message = '<div class="success">Server registered and info crawled! <a href="/server/{}">View your server</a></div>'.format(server_id)
            else:
                message = '<div class="success">Server registered! ID: {}. Info crawl failed - will retry later. <a href="/server/{}">View your server</a></div>'.format(server_id, server_id)
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Register Server - LGSL</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        h1 {{ color: #4ecca3; }}
        .nav {{ background: #16213e; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
        .nav a {{ color: #4ecca3; text-decoration: none; margin-right: 20px; }}
        .form-group {{ margin-bottom: 15px; }}
        label {{ display: block; margin-bottom: 5px; color: #4ecca3; }}
        input, select {{ width: 100%; padding: 10px; border: 1px solid #0f3460; background: #16213e; color: #eee; border-radius: 4px; box-sizing: border-box; }}
        .btn {{ background: #4ecca3; color: #1a1a2e; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
        .success {{ background: #4ecca3; color: #1a1a2e; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
        .error {{ background: #e94560; color: #fff; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
        .info {{ background: #0f3460; padding: 15px; border-radius: 4px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/register">Register Server</a>
            <a href="/admin">Admin Panel</a>
        </div>
        <h1>Register Your Game Server</h1>
        {0}
        <form method="POST">
            <div class="form-group">
                <label>Server Name</label>
                <input type="text" name="name" placeholder="My Awesome Server" required>
            </div>
            <div class="form-group">
                <label>Server Info URL (HTTP endpoint returning JSON)</label>
                <input type="text" name="address" placeholder="http://your-server.com:27015/info" required>
            </div>
            <div class="form-group">
                <label>Game Type</label>
                <select name="game_type">
                    <option value="minecraft">Minecraft</option>
                    <option value="csgo">CS:GO</option>
                    <option value="rust">Rust</option>
                    <option value="ark">ARK</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <button type="submit" class="btn">Register Server</button>
        </form>
        <div class="info">
            <h3>How it works</h3>
            <p>Your server must expose an HTTP endpoint that returns JSON with server information. Example:</p>
            <pre style="background:#1a1a2e;padding:10px;border-radius:4px;">
{{
  "players": "12/64",
  "map": "de_dust2",
  "version": "1.0.0",
  "description": "Welcome to our server!"
}}</pre>
            <p>After registration, an admin will approve and crawl your server to fetch the details.</p>
        </div>
    </div>
</body>
</html>'''.format(message)


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = ""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/admin/dashboard')
        else:
            error = '<div class="error">Invalid password</div>'
    
    if is_admin():
        return redirect('/admin/dashboard')
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Admin Login - LGSL</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 400px; margin: 100px auto; }}
        h1 {{ color: #4ecca3; text-align: center; }}
        .form-group {{ margin-bottom: 15px; }}
        input {{ width: 100%; padding: 10px; border: 1px solid #0f3460; background: #16213e; color: #eee; border-radius: 4px; box-sizing: border-box; }}
        .btn {{ width: 100%; background: #4ecca3; color: #1a1a2e; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
        .error {{ background: #e94560; color: #fff; padding: 10px; border-radius: 4px; margin-bottom: 15px; text-align: center; }}
        .box {{ background: #16213e; padding: 30px; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="box">
            <h1>Admin Login</h1>
            {0}
            <form method="POST">
                <div class="form-group">
                    <input type="password" name="password" placeholder="Admin Password" required>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
        </div>
    </div>
</body>
</html>'''.format(error)


@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin():
        return redirect('/admin')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM game_servers ORDER BY created_at DESC")
    servers = c.fetchall()
    c.execute("SELECT note FROM admin_notes ORDER BY id DESC LIMIT 1")
    note_row = c.fetchone()
    admin_note = note_row['note'] if note_row else 'No notes'
    conn.close()
    
    servers_html = ""
    for server in servers:
        status_class = 'status-active' if server['status'] == 'active' else 'status-pending'
        servers_html += '''
        <tr>
            <td>{0}</td>
            <td><a href="/server/{0}">{1}</a></td>
            <td>{2}</td>
            <td><span class="{5}">{3}</span></td>
            <td>
                <a href="/admin/approve/{0}" class="btn btn-small">Approve</a>
                <a href="/admin/crawl/{0}" class="btn btn-small">Crawl Info</a>
            </td>
        </tr>
        '''.format(server['id'], server['name'], server['address'], server['status'], server['game_type'], status_class)
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - LGSL</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #4ecca3; }}
        .nav {{ background: #16213e; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
        .nav a {{ color: #4ecca3; text-decoration: none; margin-right: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 5px; overflow: hidden; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #1a1a2e; }}
        th {{ background: #0f3460; color: #4ecca3; }}
        a {{ color: #4ecca3; }}
        .btn {{ background: #4ecca3; color: #1a1a2e; padding: 5px 10px; border: none; border-radius: 4px; text-decoration: none; display: inline-block; font-size: 12px; margin-right: 5px; }}
        .status-active {{ color: #4ecca3; }}
        .status-pending {{ color: #e94560; }}
        .admin-note {{ background: #0f3460; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .logout {{ float: right; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/register">Register Server</a>
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/logout" class="logout">Logout</a>
        </div>
        <h1>Admin Dashboard</h1>
        <div class="admin-note">
            <strong>Admin Note:</strong> {1}
        </div>
        <h2>Registered Servers</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Address</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {0}
            </tbody>
        </table>
    </div>
</body>
</html>'''.format(servers_html, admin_note)


@app.route('/admin/approve/<int:server_id>')
def approve_server(server_id):
    if not is_admin():
        return redirect('/admin')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE game_servers SET status = 'active' WHERE id = ?", (server_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/dashboard')


@app.route('/admin/crawl/<int:server_id>')
def crawl_server(server_id):
    if not is_admin():
        return redirect('/admin')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM game_servers WHERE id = ?", (server_id,))
    server = c.fetchone()
    conn.close()
    
    if not server:
        return redirect('/admin/dashboard')
    
    crawl_server_info(server_id, server['address'])
    return redirect('/admin/dashboard')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/')


@app.route('/api/server/<int:server_id>/info', methods=['POST'])
def update_server_info(server_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM game_servers WHERE id = ?", (server_id,))
    server = c.fetchone()
    
    if not server:
        conn.close()
        return json.dumps({"error": "Server not found"}), 404
    
    try:
        data = request.get_json(force=True)
        if not data:
            conn.close()
            return json.dumps({"error": "Invalid JSON"}), 400
        
        c.execute("DELETE FROM server_info WHERE server_id = ?", (server_id,))
        
        for field, value in data.items():
            c.execute("INSERT INTO server_info (server_id, field_name, field_value) VALUES (?, ?, ?)",
                     (server_id, str(field), str(value)))
        
        conn.commit()
        conn.close()
        return json.dumps({"success": True, "server_id": server_id})
    except Exception as e:
        conn.close()
        return json.dumps({"error": str(e)}), 400


@app.route('/server/<int:server_id>')
def server_details(server_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM game_servers WHERE id = ?", (server_id,))
    server = c.fetchone()
    
    if not server:
        conn.close()
        return "Server not found", 404
    
    c.execute("SELECT * FROM server_info WHERE server_id = ?", (server_id,))
    info_rows = c.fetchall()
    conn.close()
    
    info_html = ""
    parser = HTMLParser.HTMLParser()
    
    for row in info_rows:
        field = row['field_name']
        value = row['field_value']
        
        value = parser.unescape(value)
        
        value = re.sub(
            r'((https*://|https*://www\.|www\.)[\w\d\.\-\/=$?]*)',
            r"<a href='\1' target='_blank'>\1</a>",
            value
        )
        
        info_html += '''
        <tr>
            <td>{0}</td>
            <td>{1}</td>
        </tr>
        '''.format(field, value)
    
    if not info_html:
        info_html = '<tr><td colspan="2" style="text-align:center;">No server info available yet</td></tr>'
    
    response = make_response('''<!DOCTYPE html>
<html>
<head>
    <title>{0} - LGSL</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #4ecca3; }}
        .nav {{ background: #16213e; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
        .nav a {{ color: #4ecca3; text-decoration: none; margin-right: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 5px; overflow: hidden; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #1a1a2e; }}
        th {{ background: #0f3460; color: #4ecca3; width: 30%; }}
        a {{ color: #4ecca3; }}
        .server-header {{ background: #16213e; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .back {{ margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/register">Register Server</a>
            <a href="/admin">Admin Panel</a>
        </div>
        <div class="back"><a href="/">&larr; Back to Server List</a></div>
        <div class="server-header">
            <h1>{0}</h1>
            <p><strong>Address:</strong> {1}</p>
            <p><strong>Game:</strong> {2}</p>
        </div>
        <h2>Server Information</h2>
        <table>
            <thead>
                <tr>
                    <th>Property</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                {3}
            </tbody>
        </table>
    </div>
</body>
</html>'''.format(server['name'], server['address'], server['game_type'] or 'Unknown', info_html))
    
    flag = get_flag()
    response.set_cookie('server_session', flag, httponly=False, path='/')
    response.headers['X-XSS-Protection'] = '0'
    response.headers['Content-Security-Policy'] = ''
    return response


@app.errorhandler(404)
def not_found(e):
    return "Not Found", 404

@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
