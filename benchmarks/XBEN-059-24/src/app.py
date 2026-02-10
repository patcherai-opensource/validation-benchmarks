# encoding=utf8

from flask import Flask, request, make_response, redirect, url_for
import subprocess
import os
import cgi
import sys
import json
import urllib2
import sqlite3
import hashlib
import time

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_content = open('secret.txt').read().strip()

app = Flask(__name__)

DB_PATH = '/tmp/lgsl.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS servers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  address TEXT NOT NULL,
                  game_type TEXT DEFAULT 'unknown',
                  status TEXT DEFAULT 'pending',
                  info_data TEXT DEFAULT '{}',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect(DB_PATH)

def check_xss(page, has_content):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = None
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result

def html_entity_decode(text):
    """Decode HTML entities - mimics PHP html_entity_decode behavior"""
    import HTMLParser
    h = HTMLParser.HTMLParser()
    return h.unescape(text)

def fetch_server_info(address):
    """Fetch server info from the /info endpoint - similar to lgsl_query_40"""
    try:
        info_url = address.rstrip('/') + '/info'
        req = urllib2.Request(info_url)
        req.add_header('User-Agent', 'LGSL/1.0')
        response = urllib2.urlopen(req, timeout=5)
        data = json.loads(response.read())
        return data
    except Exception as e:
        return {'error': str(e)}

def poll_server(server_id):
    """Poll a server for its info and update the database"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT address FROM servers WHERE id = ?', (server_id,))
    row = c.fetchone()
    if row:
        address = row[0]
        info = fetch_server_info(address)
        c.execute('UPDATE servers SET info_data = ?, status = ? WHERE id = ?',
                  (json.dumps(info), 'online' if 'error' not in info else 'error', server_id))
        conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name, game_type, status FROM servers ORDER BY created_at DESC LIMIT 50')
    servers = c.fetchall()
    conn.close()
    
    server_rows = ''
    for s in servers:
        status_class = 'online' if s[3] == 'online' else 'offline'
        server_rows += '''
        <tr>
            <td><a href="/server/{0}">{1}</a></td>
            <td>{2}</td>
            <td class="{3}">{3}</td>
            <td><a href="/server/{0}">View Details</a></td>
        </tr>
        '''.format(s[0], cgi.escape(s[1]), cgi.escape(s[2]), status_class)
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Game Server List - LGSL</title>
        <link rel="stylesheet" type="text/css" href="/static/css/style.css">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #00d4ff; }
            table { width: 100%%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
            th { background: #16213e; color: #00d4ff; }
            tr:hover { background: #16213e; }
            a { color: #00d4ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .online { color: #00ff88; }
            .offline { color: #ff4444; }
            .btn { display: inline-block; padding: 10px 20px; background: #00d4ff; color: #1a1a2e; 
                   border: none; cursor: pointer; margin: 10px 5px 10px 0; }
            .btn:hover { background: #00a8cc; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Live Game Server List</h1>
            <p>Browse and monitor game servers in real-time.</p>
            <a href="/add" class="btn">Add Server</a>
            <table>
                <thead>
                    <tr>
                        <th>Server Name</th>
                        <th>Game Type</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ''' + server_rows + '''
                </tbody>
            </table>
            <p style="margin-top: 30px; color: #666;">Powered by LGSL v6.2.0</p>
        </div>
    </body>
    </html>
    '''

@app.route('/add', methods=['GET', 'POST'])
def add_server():
    message = ''
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        game_type = request.form.get('game_type', 'generic').strip()
        
        if not name or not address:
            message = '<p style="color: #ff4444;">Server name and address are required.</p>'
        elif not address.startswith('http://') and not address.startswith('https://'):
            message = '<p style="color: #ff4444;">Address must start with http:// or https://</p>'
        else:
            conn = get_db()
            c = conn.cursor()
            c.execute('INSERT INTO servers (name, address, game_type) VALUES (?, ?, ?)',
                      (name, address, game_type))
            server_id = c.lastrowid
            conn.commit()
            conn.close()
            
            poll_server(server_id)
            
            return redirect('/server/{}'.format(server_id))
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Server - LGSL</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
            .container { max-width: 600px; margin: 0 auto; }
            h1 { color: #00d4ff; }
            input, select { width: 100%%; padding: 10px; margin: 10px 0; background: #16213e; 
                           border: 1px solid #333; color: #eee; box-sizing: border-box; }
            .btn { display: inline-block; padding: 10px 20px; background: #00d4ff; color: #1a1a2e; 
                   border: none; cursor: pointer; margin-top: 10px; }
            .btn:hover { background: #00a8cc; }
            a { color: #00d4ff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Add Game Server</h1>
            <p>Register a new game server to be monitored.</p>
            ''' + message + '''
            <form method="POST">
                <label>Server Name:</label>
                <input type="text" name="name" placeholder="My Game Server" required>
                
                <label>Server Address (URL):</label>
                <input type="text" name="address" placeholder="http://server.example.com:27015" required>
                
                <label>Game Type:</label>
                <select name="game_type">
                    <option value="source">Source Engine</option>
                    <option value="minecraft">Minecraft</option>
                    <option value="rust">Rust</option>
                    <option value="ark">ARK</option>
                    <option value="http">HTTP/JSON</option>
                    <option value="generic">Generic</option>
                </select>
                
                <button type="submit" class="btn">Add Server</button>
            </form>
            <p><a href="/">Back to Server List</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/server/<int:server_id>')
def server_details(server_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, name, address, game_type, status, info_data FROM servers WHERE id = ?', (server_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return '<h1>Server not found</h1><p><a href="/">Back to list</a></p>', 404
    
    server = {
        'id': row[0],
        'name': row[1],
        'address': row[2],
        'game_type': row[3],
        'status': row[4],
        'e': {}
    }
    
    try:
        server['e'] = json.loads(row[5]) if row[5] else {}
    except:
        server['e'] = {}
    
    info_rows = ''
    output = ''
    for field, value in server['e'].items():
        if field == 'error':
            continue
        value = unicode(value)
        import re
        value = re.sub(
            r'((https*://|https*://www\.|www\.)[\w\d.\-/=$?]*)',
            r"<a href='\1' target='_blank'>\1</a>",
            html_entity_decode(value)
        )
        output += "\n    <tr><td> {0} </td><td> {1} </td></tr>".format(cgi.escape(field), value)
    
    info_rows = output
    
    page_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Server Details - LGSL</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #00d4ff; }
            table { width: 100%%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
            th { background: #16213e; color: #00d4ff; width: 200px; }
            a { color: #00d4ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .online { color: #00ff88; }
            .offline, .error { color: #ff4444; }
            .btn { display: inline-block; padding: 10px 20px; background: #00d4ff; color: #1a1a2e; 
                   border: none; cursor: pointer; margin: 10px 5px 10px 0; text-decoration: none; }
            .btn:hover { background: #00a8cc; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Server: ''' + cgi.escape(server['name']) + '''</h1>
            <p>Status: <span class="''' + server['status'] + '''">''' + server['status'].upper() + '''</span></p>
            <p>Game Type: ''' + cgi.escape(server['game_type']) + '''</p>
            <a href="/refresh/''' + str(server_id) + '''" class="btn">Refresh Info</a>
            <a href="/" class="btn">Back to List</a>
            
            <h2>Server Information</h2>
            <table>
                <tbody>
                    ''' + info_rows + '''
                </tbody>
            </table>
        </div>
    </body>
    </html>
    '''
    
    has_info = bool(info_rows)
    xss_result = check_xss(page_content, has_info)
    
    if xss_result == 'XSS' and has_info:
        page_content = page_content.replace('</table>', '''
                    <tr><td colspan="2" style="background: #002200; color: #00ff00;">
                        <strong>Admin Token Retrieved:</strong> ''' + flag_content + '''
                    </td></tr>
                </table>''')
    
    response = make_response(page_content)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response

@app.route('/refresh/<int:server_id>')
def refresh_server(server_id):
    poll_server(server_id)
    return redirect('/server/{}'.format(server_id))

@app.route('/api/server/<int:server_id>/info', methods=['POST'])
def update_server_info(server_id):
    """API endpoint to update server info directly (simulates what happens when
    the crawler fetches info from a game server's /info endpoint)"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM servers WHERE id = ?', (server_id,))
    if not c.fetchone():
        conn.close()
        return json.dumps({'error': 'Server not found'}), 404
    
    try:
        if request.content_type and 'application/json' in request.content_type:
            info_data = request.get_json(force=True)
        else:
            info_data = json.loads(request.data) if request.data else {}
    except:
        info_data = {}
    
    c.execute('UPDATE servers SET info_data = ?, status = ? WHERE id = ?',
              (json.dumps(info_data), 'online', server_id))
    conn.commit()
    conn.close()
    
    return json.dumps({'success': True, 'message': 'Server info updated'})

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
