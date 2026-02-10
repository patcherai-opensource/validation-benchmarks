# encoding=utf8
# Game Server List - A service for tracking game servers

from flask import Flask, request, make_response, jsonify, redirect, url_for
import subprocess
import os
import re
import json
import sys
import html
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

DATABASE = 'servers.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS servers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  address TEXT NOT NULL,
                  port INTEGER NOT NULL,
                  game_type TEXT NOT NULL,
                  status TEXT DEFAULT 'online')''')
    c.execute('''CREATE TABLE IF NOT EXISTS server_info
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  server_id INTEGER NOT NULL,
                  field TEXT NOT NULL,
                  value TEXT NOT NULL,
                  FOREIGN KEY (server_id) REFERENCES servers(id))''')
    conn.commit()
    conn.close()

init_db()

def check_xss(page):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        os.unlink(fn)
    return result

@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name, address, port, game_type, status FROM servers')
    servers = c.fetchall()
    conn.close()
    
    server_rows = ''
    for srv in servers:
        server_rows += '''
            <tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}:{}</td>
                <td>{}</td>
                <td><span class="status-{}">{}</span></td>
                <td><a href="/server/{}" class="btn btn-info">Details</a></td>
            </tr>
        '''.format(
            html.escape(srv['name']),
            html.escape(srv['game_type']),
            html.escape(srv['address']),
            srv['port'],
            html.escape(srv['game_type']),
            'online' if srv['status'] == 'online' else 'offline',
            html.escape(srv['status']),
            srv['id']
        )
    
    if not server_rows:
        server_rows = '<tr><td colspan="6" class="text-center">No servers registered yet</td></tr>'
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>GameTracker - Server List</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>GameTracker</h1>
            <nav>
                <a href="/">Server List</a>
                <a href="/register">Register Server</a>
            </nav>
        </header>
        
        <main>
            <h2>Active Game Servers</h2>
            <table class="server-table">
                <thead>
                    <tr>
                        <th>Server Name</th>
                        <th>Game</th>
                        <th>Address</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {}
                </tbody>
            </table>
        </main>
        
        <footer>
            <p>&copy; 2024 GameTracker - Server Monitoring Service</p>
        </footer>
    </div>
</body>
</html>'''.format(server_rows)

@app.route('/register', methods=['GET', 'POST'])
def register_server():
    if request.method == 'POST':
        name = request.form.get('name', '')
        address = request.form.get('address', '')
        port = request.form.get('port', '')
        game_type = request.form.get('game_type', '')
        
        if not all([name, address, port, game_type]):
            return redirect('/register?error=missing_fields')
        
        try:
            port = int(port)
        except ValueError:
            return redirect('/register?error=invalid_port')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO servers (name, address, port, game_type) VALUES (?, ?, ?, ?)',
                  (name, address, port, game_type))
        server_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return redirect('/server/{}/info'.format(server_id))
    
    error = request.args.get('error', '')
    error_msg = ''
    if error == 'missing_fields':
        error_msg = '<div class="error">All fields are required</div>'
    elif error == 'invalid_port':
        error_msg = '<div class="error">Invalid port number</div>'
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>GameTracker - Register Server</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>GameTracker</h1>
            <nav>
                <a href="/">Server List</a>
                <a href="/register">Register Server</a>
            </nav>
        </header>
        
        <main>
            <h2>Register New Server</h2>
            {}
            <form method="POST" class="register-form">
                <div class="form-group">
                    <label for="name">Server Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="address">Server Address:</label>
                    <input type="text" id="address" name="address" placeholder="192.168.1.100" required>
                </div>
                <div class="form-group">
                    <label for="port">Port:</label>
                    <input type="number" id="port" name="port" placeholder="27015" required>
                </div>
                <div class="form-group">
                    <label for="game_type">Game Type:</label>
                    <select id="game_type" name="game_type" required>
                        <option value="">Select game...</option>
                        <option value="Counter-Strike">Counter-Strike</option>
                        <option value="Minecraft">Minecraft</option>
                        <option value="Rust">Rust</option>
                        <option value="ARK">ARK: Survival</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Register Server</button>
            </form>
        </main>
        
        <footer>
            <p>&copy; 2024 GameTracker - Server Monitoring Service</p>
        </footer>
    </div>
</body>
</html>'''.format(error_msg)


@app.route('/server/<int:server_id>/info', methods=['GET', 'POST'])
def server_info_update(server_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM servers WHERE id = ?', (server_id,))
    server = c.fetchone()
    
    if not server:
        conn.close()
        return 'Server not found', 404
    
    if request.method == 'POST':
        content_type = request.content_type or ''
        
        if 'application/json' in content_type:
            try:
                data = request.get_json(force=True)
                if isinstance(data, dict):
                    c.execute('DELETE FROM server_info WHERE server_id = ?', (server_id,))
                    for field, value in data.items():
                        if isinstance(value, basestring):
                            c.execute('INSERT INTO server_info (server_id, field, value) VALUES (?, ?, ?)',
                                      (server_id, str(field), str(value)))
                    conn.commit()
            except Exception as e:
                pass
        
        conn.close()
        return redirect('/server/{}'.format(server_id))
    
    conn.close()
    return '''<!DOCTYPE html>
<html>
<head>
    <title>GameTracker - Update Server Info</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>GameTracker</h1>
            <nav>
                <a href="/">Server List</a>
                <a href="/register">Register Server</a>
            </nav>
        </header>
        
        <main>
            <h2>Update Server Information</h2>
            <p>Server: {} ({}:{})</p>
            <p>Submit server details as JSON via POST request to this endpoint.</p>
            <p>Example:</p>
            <pre>
curl -X POST -H "Content-Type: application/json" \\
     -d '{{"Players": "24/32", "Map": "de_dust2", "Version": "1.6"}}' \\
     {}/server/{}/info
            </pre>
            <p><a href="/server/{}" class="btn btn-primary">View Server Details</a></p>
        </main>
        
        <footer>
            <p>&copy; 2024 GameTracker - Server Monitoring Service</p>
        </footer>
    </div>
</body>
</html>'''.format(
        html.escape(server['name']),
        html.escape(server['address']),
        server['port'],
        os.environ.get('BASE_URL', 'http://localhost:5000'),
        server_id,
        server_id
    )


@app.route('/server/<int:server_id>')
def server_details(server_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM servers WHERE id = ?', (server_id,))
    server = c.fetchone()
    
    if not server:
        conn.close()
        return 'Server not found', 404
    
    c.execute('SELECT field, value FROM server_info WHERE server_id = ?', (server_id,))
    info_rows = c.fetchall()
    conn.close()
    
    info_table = ''
    for row in info_rows:
        field = row['field']
        value = row['value']
        
        decoded_value = html.unescape(value)
        
        url_pattern = r'((https*://|https*://www\.|www\.)[\w\d\.\-\/=$?]*)'
        processed_value = re.sub(
            url_pattern,
            r"<a href='\1' target='_blank'>\1</a>",
            decoded_value
        )
        
        info_table += '''
            <tr>
                <td>{}</td>
                <td>{}</td>
            </tr>
        '''.format(field, processed_value)
    
    if not info_table:
        info_table = '<tr><td colspan="2" class="text-center">No additional information available</td></tr>'
    
    details_page = '''<!DOCTYPE html>
<html>
<head>
    <title>GameTracker - {}</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>GameTracker</h1>
            <nav>
                <a href="/">Server List</a>
                <a href="/register">Register Server</a>
            </nav>
        </header>
        
        <main>
            <h2>Server Details: {}</h2>
            
            <div class="server-info-card">
                <h3>Basic Information</h3>
                <table class="info-table">
                    <tr><td>Name</td><td>{}</td></tr>
                    <tr><td>Address</td><td>{}:{}</td></tr>
                    <tr><td>Game</td><td>{}</td></tr>
                    <tr><td>Status</td><td><span class="status-{}">{}</span></td></tr>
                </table>
            </div>
            
            <div class="server-info-card">
                <h3>Extended Information</h3>
                <table class="info-table">
                    {}
                </table>
            </div>
            
            <p><a href="/server/{}/info" class="btn btn-secondary">Update Server Info</a></p>
            <p><a href="/" class="btn btn-primary">Back to Server List</a></p>
        </main>
        
        <footer>
            <p>&copy; 2024 GameTracker - Server Monitoring Service</p>
        </footer>
    </div>
</body>
</html>'''.format(
        html.escape(server['name']),
        html.escape(server['name']),
        html.escape(server['name']),
        html.escape(server['address']),
        server['port'],
        html.escape(server['game_type']),
        'online' if server['status'] == 'online' else 'offline',
        html.escape(server['status']),
        info_table,
        server_id
    )
    
    result = check_xss(details_page)
    
    if result == 'XSS':
        details_page = details_page.replace(
            '</main>',
            '<div class="alert alert-success">Admin notification triggered. Flag: {}</div></main>'.format(flag)
        )
    
    response = make_response(details_page)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


@app.errorhandler(404)
def page_not_found(e):
    return '''<!DOCTYPE html>
<html>
<head><title>404 - Not Found</title></head>
<body><h1>404 - Page Not Found</h1><p><a href="/">Return to home</a></p></body>
</html>''', 404

@app.errorhandler(500)
def internal_error(e):
    return '''<!DOCTYPE html>
<html>
<head><title>500 - Server Error</title></head>
<body><h1>500 - Internal Server Error</h1><p><a href="/">Return to home</a></p></body>
</html>''', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
