# encoding=utf8

from flask import Flask, request, redirect, url_for
import subprocess
import os
import sys
import json
import uuid
import re
import cgi

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

SERVERS_FILE = 'servers.json'

def load_servers():
    if os.path.exists(SERVERS_FILE):
        with open(SERVERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_servers(servers):
    with open(SERVERS_FILE, 'w') as f:
        json.dump(servers, f)

def simulate_admin_visit(server_id):
    servers = load_servers()
    if server_id not in servers:
        return None
    
    server = servers[server_id]
    
    page_content = generate_server_details_page(server)
    
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], 
                           stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    
    try:
        with open(fn, 'w') as of:
            of.write(page_content)
        
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        if os.path.exists(fn):
            os.unlink(fn)
    
    return result

def generate_server_details_page(server):
    rows = ""
    for field, value in server.get('extra', {}).items():
        value = re.sub(
            r'((https*://|https*://www\.|www\.)[\w\d.\-/=$?]*)',
            r"<a href='\1' target='_blank'>\1</a>",
            html_entity_decode(value)
        )
        rows += "\n    <tr><td> {0} </td><td> {1} </td></tr>".format(field, value)
    
    return SERVER_DETAILS_PAGE.format(
        name=cgi.escape(server.get('name', 'Unknown')),
        address=cgi.escape(server.get('address', 'Unknown')),
        game=cgi.escape(server.get('game', 'Unknown')),
        players=cgi.escape(str(server.get('players', '0/0'))),
        extra_rows=rows
    )

def html_entity_decode(s):
    import HTMLParser
    h = HTMLParser.HTMLParser()
    return h.unescape(s)

INDEX_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>GameServer List - LGSL</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 20px; text-align: center; }
        .header h1 { margin: 0; color: #4cc9f0; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .nav { background: #0f3460; padding: 10px 20px; }
        .nav a { color: #4cc9f0; margin-right: 20px; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #16213e; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }
        th { background: #0f3460; color: #4cc9f0; }
        tr:hover { background: #1f4068; }
        a { color: #4cc9f0; }
        .btn { display: inline-block; padding: 8px 16px; background: #4cc9f0; color: #16213e; 
               text-decoration: none; border-radius: 4px; margin: 5px; }
        .btn:hover { background: #7dd3fc; }
        .status-online { color: #4ade80; }
        .status-offline { color: #f87171; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Live Game Server List</h1>
        <p>Track and monitor your favorite game servers</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Register Server</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <h2>Welcome to LGSL</h2>
        <p>LGSL (Live Game Server List) allows you to monitor game servers in real-time. 
           Server owners can register their servers to be listed and monitored by our system.</p>
        <p><a href="/servers" class="btn">View Server List</a> <a href="/register" class="btn">Register Your Server</a></p>
    </div>
</body>
</html>
"""

SERVER_LIST_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Server List - LGSL</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; color: #4cc9f0; }}
        .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
        .nav {{ background: #0f3460; padding: 10px 20px; }}
        .nav a {{ color: #4cc9f0; margin-right: 20px; text-decoration: none; }}
        .nav a:hover {{ text-decoration: underline; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #16213e; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #4cc9f0; }}
        tr:hover {{ background: #1f4068; }}
        a {{ color: #4cc9f0; }}
        .status-online {{ color: #4ade80; }}
        .no-servers {{ text-align: center; padding: 40px; color: #888; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Live Game Server List</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Register Server</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <h2>Registered Servers</h2>
        {content}
    </div>
</body>
</html>
"""

REGISTER_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Register Server - LGSL</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 20px; text-align: center; }
        .header h1 { margin: 0; color: #4cc9f0; }
        .container { max-width: 600px; margin: 20px auto; padding: 0 20px; }
        .nav { background: #0f3460; padding: 10px 20px; }
        .nav a { color: #4cc9f0; margin-right: 20px; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
        form { background: #16213e; padding: 30px; border-radius: 8px; margin-top: 20px; }
        label { display: block; margin-bottom: 5px; color: #4cc9f0; }
        input, textarea, select { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #0f3460; 
                  background: #1a1a2e; color: #eee; border-radius: 4px; box-sizing: border-box; }
        button { padding: 12px 24px; background: #4cc9f0; color: #16213e; border: none; 
                 border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #7dd3fc; }
        .note { font-size: 12px; color: #888; margin-bottom: 15px; }
        h3 { color: #4cc9f0; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Register Game Server</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Register Server</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <form method="POST" action="/register">
            <h3>Basic Information</h3>
            <label>Server Name:</label>
            <input type="text" name="name" required placeholder="My Awesome Server">
            
            <label>Server Address:</label>
            <input type="text" name="address" required placeholder="192.168.1.1:27015">
            
            <label>Game Type:</label>
            <select name="game">
                <option value="Counter-Strike">Counter-Strike</option>
                <option value="Minecraft">Minecraft</option>
                <option value="Rust">Rust</option>
                <option value="ARK">ARK: Survival Evolved</option>
                <option value="Other">Other</option>
            </select>
            
            <label>Current Players:</label>
            <input type="text" name="players" placeholder="12/32">
            
            <h3>Extended Server Information (JSON)</h3>
            <p class="note">Enter additional server details as JSON. These will be displayed on the server info page.
            Example: {"Map": "de_dust2", "Mode": "Competitive", "Description": "Welcome!"}</p>
            <textarea name="extra_info" rows="5" placeholder='{"Map": "de_dust2", "Mode": "Competitive"}'></textarea>
            
            <button type="submit">Register Server</button>
        </form>
    </div>
</body>
</html>
"""

SERVER_DETAILS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>{name} - Server Details</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; color: #4cc9f0; }}
        .container {{ max-width: 800px; margin: 20px auto; padding: 0 20px; }}
        .nav {{ background: #0f3460; padding: 10px 20px; }}
        .nav a {{ color: #4cc9f0; margin-right: 20px; text-decoration: none; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #16213e; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #4cc9f0; width: 30%; }}
        a {{ color: #4cc9f0; }}
        .server-header {{ background: #16213e; padding: 20px; border-radius: 8px; margin-top: 20px; }}
        .server-name {{ font-size: 24px; color: #4cc9f0; margin-bottom: 10px; }}
        h3 {{ color: #4cc9f0; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Server Details</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Register Server</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="server-header">
            <div class="server-name">{name}</div>
            <div>Address: {address}</div>
        </div>
        
        <h3>Basic Information</h3>
        <table>
            <tr><td>Game</td><td>{game}</td></tr>
            <tr><td>Players</td><td>{players}</td></tr>
            <tr><td>Address</td><td>{address}</td></tr>
        </table>
        
        <h3>Extended Information</h3>
        <table>{extra_rows}</table>
    </div>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Server Registered - LGSL</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; color: #4cc9f0; }}
        .container {{ max-width: 600px; margin: 20px auto; padding: 0 20px; text-align: center; }}
        .nav {{ background: #0f3460; padding: 10px 20px; }}
        .nav a {{ color: #4cc9f0; margin-right: 20px; text-decoration: none; }}
        .success {{ background: #16213e; padding: 30px; border-radius: 8px; margin-top: 20px; }}
        .success h2 {{ color: #4ade80; }}
        a {{ color: #4cc9f0; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #4cc9f0; color: #16213e; 
               text-decoration: none; border-radius: 4px; margin: 10px; }}
        .message {{ background: #0f3460; padding: 20px; border-radius: 4px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Server Registered</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Register Server</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="success">
            <h2>Registration Successful!</h2>
            <p>Your server has been registered with ID: <strong>{server_id}</strong></p>
            <p>An administrator will review your server shortly.</p>
            <div class="message">{message}</div>
            <p>
                <a href="/server/{server_id}" class="btn">View Server Details</a>
                <a href="/servers" class="btn">Server List</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

ABOUT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>About - LGSL</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 20px; text-align: center; }
        .header h1 { margin: 0; color: #4cc9f0; }
        .container { max-width: 800px; margin: 20px auto; padding: 0 20px; }
        .nav { background: #0f3460; padding: 10px 20px; }
        .nav a { color: #4cc9f0; margin-right: 20px; text-decoration: none; }
        .content { background: #16213e; padding: 30px; border-radius: 8px; margin-top: 20px; }
        h2 { color: #4cc9f0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>About LGSL</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Register Server</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="content">
            <h2>Live Game Server List</h2>
            <p>LGSL is a game server monitoring and listing application. Server owners can register 
            their game servers to be monitored and displayed to players looking for servers to join.</p>
            
            <h2>Features</h2>
            <ul>
                <li>Real-time server monitoring</li>
                <li>Support for multiple game types</li>
                <li>Extended server information display</li>
                <li>Easy server registration</li>
            </ul>
            
            <h2>Version</h2>
            <p>LGSL v6.2.0</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return INDEX_PAGE

@app.route('/servers')
def server_list():
    servers = load_servers()
    
    if not servers:
        content = '<div class="no-servers">No servers registered yet. <a href="/register">Register the first one!</a></div>'
    else:
        content = """
        <table>
            <tr>
                <th>Server Name</th>
                <th>Game</th>
                <th>Address</th>
                <th>Players</th>
                <th>Status</th>
            </tr>
        """
        for server_id, server in servers.items():
            content += """
            <tr>
                <td><a href="/server/{id}">{name}</a></td>
                <td>{game}</td>
                <td>{address}</td>
                <td>{players}</td>
                <td class="status-online">Online</td>
            </tr>
            """.format(
                id=server_id,
                name=cgi.escape(server.get('name', 'Unknown')),
                game=cgi.escape(server.get('game', 'Unknown')),
                address=cgi.escape(server.get('address', 'Unknown')),
                players=cgi.escape(str(server.get('players', '0/0')))
            )
        content += "</table>"
    
    return SERVER_LIST_PAGE.format(content=content)

@app.route('/server/<server_id>')
def server_details(server_id):
    servers = load_servers()
    
    if server_id not in servers:
        return "Server not found", 404
    
    server = servers[server_id]
    return generate_server_details_page(server)

@app.route('/register', methods=['GET', 'POST'])
def register_server():
    if request.method == 'GET':
        return REGISTER_PAGE
    
    name = request.form.get('name', '')
    address = request.form.get('address', '')
    game = request.form.get('game', '')
    players = request.form.get('players', '0/0')
    extra_info = request.form.get('extra_info', '{}')
    
    if not name or not address:
        return "Name and address are required", 400
    
    try:
        extra = json.loads(extra_info) if extra_info.strip() else {}
    except:
        extra = {}
    
    server_id = str(uuid.uuid4())[:8]
    
    servers = load_servers()
    servers[server_id] = {
        'name': name,
        'address': address,
        'game': game,
        'players': players,
        'extra': extra
    }
    save_servers(servers)
    
    admin_result = simulate_admin_visit(server_id)
    
    if admin_result == 'XSS':
        message = "Admin verification detected unusual activity. Security token: " + flag
    else:
        message = "Server queued for admin review."
    
    return SUCCESS_PAGE.format(server_id=server_id, message=message)

@app.route('/about')
def about():
    return ABOUT_PAGE

@app.errorhandler(404)
def not_found(e):
    return "Not Found", 404

@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
