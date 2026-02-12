# encoding=utf8

from flask import Flask, request, redirect, jsonify
import subprocess
import os
import re
import json
import sys
import sqlite3
import HTMLParser

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

DB_PATH = '/python-docker/data/lgsl.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS lgsl_servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL,
        port INTEGER NOT NULL,
        type TEXT DEFAULT 'unknown',
        status INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS lgsl_server_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER NOT NULL,
        field TEXT NOT NULL,
        value TEXT NOT NULL,
        FOREIGN KEY (server_id) REFERENCES lgsl_servers(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS lgsl_config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')
    # Seed some default servers
    c.execute("SELECT COUNT(*) FROM lgsl_servers")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO lgsl_servers (ip, port, type, status) VALUES (?, ?, ?, ?)",
                  ("192.168.1.10", 27015, "source", 1))
        sid = c.lastrowid
        for field, value in [("hostname", "Community Server #1"), ("map", "de_dust2"),
                             ("players", "12/32"), ("game", "Counter-Strike: Source"),
                             ("version", "1.0.0.78"), ("website", "https://example-community.com")]:
            c.execute("INSERT INTO lgsl_server_info (server_id, field, value) VALUES (?, ?, ?)",
                      (sid, field, value))
        c.execute("INSERT INTO lgsl_servers (ip, port, type, status) VALUES (?, ?, ?, ?)",
                  ("10.0.0.5", 7777, "samp", 1))
        sid = c.lastrowid
        for field, value in [("hostname", "RP World Server"), ("map", "San Andreas"),
                             ("players", "87/200"), ("gamemode", "Roleplay v4.2"),
                             ("language", "English"), ("website", "https://www.rpworld-sa.net/forums")]:
            c.execute("INSERT INTO lgsl_server_info (server_id, field, value) VALUES (?, ?, ?)",
                      (sid, field, value))
    conn.commit()
    conn.close()

init_db()


def lgsl_details_render(server_id):
    """Build the details page content for a given server."""
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM lgsl_servers WHERE id = ?", (server_id,))
    server = c.fetchone()
    if not server:
        conn.close()
        return None

    c.execute("SELECT field, value FROM lgsl_server_info WHERE server_id = ?", (server_id,))
    info_rows = c.fetchall()
    conn.close()

    detail_rows = ""
    for row in info_rows:
        field = row['field']
        value = row['value']

        # Decode HTML entities for display
        h = HTMLParser.HTMLParser()
        value = h.unescape(value)

        # Auto-link URLs in values
        value = re.sub(
            r'((https?://|https?://www\.|www\.)[\w\d.\-/=$?]*)',
            r"<a href='\1' target='_blank'>\1</a>",
            value
        )

        detail_rows += "\n    <tr><td> {0} </td><td> {1} </td></tr>".format(field, value)

    return {
        'server': server,
        'detail_rows': detail_rows
    }


@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM lgsl_servers ORDER BY id")
    servers = c.fetchall()
    conn.close()

    server_rows = ""
    for s in servers:
        status_class = "online" if s['status'] == 1 else "offline"
        status_text = "Online" if s['status'] == 1 else "Offline"
        server_rows += """
        <tr>
            <td>{id}</td>
            <td>{ip}:{port}</td>
            <td>{type}</td>
            <td><span class="status-{sc}">{st}</span></td>
            <td><a href="/server/{id}">Details</a></td>
        </tr>""".format(id=s['id'], ip=s['ip'], port=s['port'],
                        type=s['type'], sc=status_class, st=status_text)

    return """<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Live Game Server List</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }}
        .container {{ max-width: 960px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #e94560; margin-bottom: 5px; }}
        .subtitle {{ color: #888; margin-bottom: 20px; font-size: 0.9em; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 4px; overflow: hidden; }}
        th {{ background: #0f3460; padding: 12px 15px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px 15px; border-bottom: 1px solid #1a1a2e; }}
        tr:hover {{ background: #1a2744; }}
        a {{ color: #e94560; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .status-online {{ color: #4ecca3; font-weight: bold; }}
        .status-offline {{ color: #e94560; }}
        .nav {{ background: #0f3460; padding: 10px 0; margin-bottom: 20px; }}
        .nav .container {{ display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }}
        .nav a {{ color: #eee; margin-left: 15px; font-size: 0.9em; }}
        .nav-brand {{ font-weight: bold; color: #e94560 !important; font-size: 1.1em; }}
    </style>
</head>
<body>
    <div class="nav">
        <div class="container">
            <a href="/" class="nav-brand">LGSL v6.2.1</a>
            <div>
                <a href="/">Server List</a>
                <a href="/add">Add Server</a>
                <a href="/admin">Admin</a>
            </div>
        </div>
    </div>
    <div class="container">
        <h1>Game Server List</h1>
        <p class="subtitle">Live Game Server List - Monitoring {count} servers</p>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Address</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Info</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</body>
</html>""".format(count=len(servers), rows=server_rows)


@app.route('/server/<int:server_id>')
def server_details(server_id):
    data = lgsl_details_render(server_id)
    if data is None:
        return "Server not found", 404

    server = data['server']
    detail_rows = data['detail_rows']

    return """<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Server Details</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }}
        .container {{ max-width: 960px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #e94560; margin-bottom: 5px; }}
        h2 {{ color: #ccc; font-size: 1.1em; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 4px; overflow: hidden; }}
        th {{ background: #0f3460; padding: 12px 15px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px 15px; border-bottom: 1px solid #1a1a2e; }}
        a {{ color: #e94560; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .back {{ margin-top: 20px; display: inline-block; }}
        .nav {{ background: #0f3460; padding: 10px 0; margin-bottom: 20px; }}
        .nav .container {{ display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }}
        .nav a {{ color: #eee; margin-left: 15px; font-size: 0.9em; }}
        .nav-brand {{ font-weight: bold; color: #e94560 !important; font-size: 1.1em; }}
    </style>
</head>
<body>
    <div class="nav">
        <div class="container">
            <a href="/" class="nav-brand">LGSL v6.2.1</a>
            <div>
                <a href="/">Server List</a>
                <a href="/add">Add Server</a>
                <a href="/admin">Admin</a>
            </div>
        </div>
    </div>
    <div class="container">
        <h1>Server Details</h1>
        <h2>{ip}:{port} ({type})</h2>
        <table>
            <thead>
                <tr>
                    <th>Field</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <a href="/" class="back">&larr; Back to server list</a>
    </div>
</body>
</html>""".format(
        ip=server['ip'], port=server['port'], type=server['type'],
        rows=detail_rows
    )


@app.route('/add', methods=['GET'])
def add_server_form():
    return """<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Add Server</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }}
        .container {{ max-width: 960px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #e94560; margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 5px; color: #ccc; font-size: 0.9em; }}
        input[type=text], input[type=number], select {{ width: 100%; padding: 10px; margin-bottom: 15px; background: #16213e; border: 1px solid #0f3460; color: #eee; border-radius: 4px; font-size: 0.95em; }}
        input[type=submit] {{ background: #e94560; color: #fff; border: none; padding: 12px 30px; border-radius: 4px; cursor: pointer; font-size: 1em; }}
        input[type=submit]:hover {{ background: #c43b52; }}
        .form-group {{ margin-bottom: 5px; }}
        .help-text {{ color: #666; font-size: 0.8em; margin-bottom: 15px; }}
        .nav {{ background: #0f3460; padding: 10px 0; margin-bottom: 20px; }}
        .nav .container {{ display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }}
        .nav a {{ color: #eee; margin-left: 15px; font-size: 0.9em; text-decoration: none; }}
        .nav-brand {{ font-weight: bold; color: #e94560 !important; font-size: 1.1em; }}
    </style>
</head>
<body>
    <div class="nav">
        <div class="container">
            <a href="/" class="nav-brand">LGSL v6.2.1</a>
            <div>
                <a href="/">Server List</a>
                <a href="/add">Add Server</a>
                <a href="/admin">Admin</a>
            </div>
        </div>
    </div>
    <div class="container">
        <h1>Add Game Server</h1>
        <form method="POST" action="/add">
            <div class="form-group">
                <label>Server IP / Hostname</label>
                <input type="text" name="ip" placeholder="e.g. 192.168.1.100" required>
            </div>
            <div class="form-group">
                <label>Query Port</label>
                <input type="number" name="port" placeholder="e.g. 27015" required>
            </div>
            <div class="form-group">
                <label>Server Type</label>
                <select name="type">
                    <option value="source">Source Engine</option>
                    <option value="minecraft">Minecraft</option>
                    <option value="samp">SA-MP</option>
                    <option value="fivem">FiveM</option>
                    <option value="rust">Rust</option>
                    <option value="http">HTTP JSON (type 40)</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <p class="help-text">For HTTP JSON servers (type 40), the server should respond to /info with JSON data containing server information fields.</p>
            <input type="submit" value="Add Server">
        </form>
    </div>
</body>
</html>"""


@app.route('/add', methods=['POST'])
def add_server():
    ip = request.form.get('ip', '').strip()
    port = request.form.get('port', '0').strip()
    server_type = request.form.get('type', 'other').strip()

    if not ip or not port:
        return "IP and port are required", 400

    try:
        port_int = int(port)
    except ValueError:
        return "Invalid port number", 400

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO lgsl_servers (ip, port, type, status) VALUES (?, ?, ?, ?)",
              (ip, port_int, server_type, 0))
    server_id = c.lastrowid
    conn.commit()
    conn.close()

    # Trigger initial query for the server
    lgsl_query_server(server_id)

    return redirect('/server/{0}'.format(server_id))


def lgsl_query_40(ip, port):
    """Query HTTP JSON game server (type 40). Fetches /info endpoint and parses JSON fields."""
    import urllib2
    try:
        url = "http://{0}:{1}/info".format(ip, port)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'LGSL/6.2.1')
        response = urllib2.urlopen(req, timeout=5)
        data = json.loads(response.read())
        if isinstance(data, dict):
            return data
    except Exception as e:
        logging.info("lgsl_query_40 failed for {0}:{1}: {2}".format(ip, port, str(e)))
    return None


def lgsl_query_server(server_id):
    """Query a server and update its info in the database"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM lgsl_servers WHERE id = ?", (server_id,))
    server = c.fetchone()
    if not server:
        conn.close()
        return

    info = None
    if server['type'] == 'http':
        info = lgsl_query_40(server['ip'], server['port'])

    if info:
        # Clear old info
        c.execute("DELETE FROM lgsl_server_info WHERE server_id = ?", (server_id,))
        # Insert new info fields
        for field, value in info.items():
            c.execute("INSERT INTO lgsl_server_info (server_id, field, value) VALUES (?, ?, ?)",
                      (server_id, str(field), str(value)))
        c.execute("UPDATE lgsl_servers SET status = 1 WHERE id = ?", (server_id,))
    else:
        c.execute("UPDATE lgsl_servers SET status = 0 WHERE id = ?", (server_id,))

    conn.commit()
    conn.close()


@app.route('/api/query/<int:server_id>', methods=['POST'])
def api_query_server(server_id):
    """Trigger a re-query of a specific server"""
    lgsl_query_server(server_id)
    return jsonify({"status": "ok", "message": "Server queried"})


@app.route('/api/server/<int:server_id>/info', methods=['POST'])
def api_update_server_info(server_id):
    """Update server info fields via JSON POST."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM lgsl_servers WHERE id = ?", (server_id,))
    server = c.fetchone()
    if not server:
        conn.close()
        return jsonify({"error": "Server not found"}), 404

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        conn.close()
        return jsonify({"error": "Invalid JSON"}), 400

    c.execute("DELETE FROM lgsl_server_info WHERE server_id = ?", (server_id,))
    for field, value in data.items():
        c.execute("INSERT INTO lgsl_server_info (server_id, field, value) VALUES (?, ?, ?)",
                  (server_id, str(field), str(value)))
    c.execute("UPDATE lgsl_servers SET status = 1 WHERE id = ?", (server_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok", "message": "Server info updated"})


@app.route('/admin')
def admin_panel():
    return """<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Administration</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }}
        .container {{ max-width: 960px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #e94560; }}
        .info-box {{ background: #16213e; padding: 20px; border-radius: 4px; margin-top: 20px; }}
        .info-box p {{ margin: 8px 0; color: #aaa; }}
        .nav {{ background: #0f3460; padding: 10px 0; margin-bottom: 20px; }}
        .nav .container {{ display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }}
        .nav a {{ color: #eee; margin-left: 15px; font-size: 0.9em; text-decoration: none; }}
        .nav-brand {{ font-weight: bold; color: #e94560 !important; font-size: 1.1em; }}
    </style>
</head>
<body>
    <div class="nav">
        <div class="container">
            <a href="/" class="nav-brand">LGSL v6.2.1</a>
            <div>
                <a href="/">Server List</a>
                <a href="/add">Add Server</a>
                <a href="/admin">Admin</a>
            </div>
        </div>
    </div>
    <div class="container">
        <h1>Administration</h1>
        <div class="info-box">
            <p><strong>LGSL Version:</strong> 6.2.1</p>
            <p><strong>PHP Version:</strong> 7.4.33 (compatibility mode)</p>
            <p><strong>Query Interval:</strong> 60 seconds</p>
            <p><strong>Admin access is restricted.</strong> Please authenticate to manage servers.</p>
        </div>
    </div>
</body>
</html>"""


@app.route('/crawl/<int:server_id>')
def crawl_server(server_id):
    """Render server details in headless browser for monitoring checks."""
    data = lgsl_details_render(server_id)
    if data is None:
        return jsonify({"error": "Server not found"}), 404

    server = data['server']
    detail_rows = data['detail_rows']

    # Build the full page that will be rendered by PhantomJS
    page_html = """<!DOCTYPE html>
<html>
<head><title>Server Details - {ip}:{port}</title></head>
<body>
<h1>Server Details</h1>
<table>
<tr><th>Field</th><th>Value</th></tr>
{rows}
</table>
</body>
</html>""".format(ip=server['ip'], port=server['port'], rows=detail_rows)

    # Write temp file and have PhantomJS render it
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    result = ""
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()

        proc = subprocess.Popen(["timeout", "8", "phantomjs", "check.js"],
                                stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        proc.wait()
    except Exception as e:
        logging.error("Crawl error: {0}".format(str(e)))
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    flag_content = open('secret.txt').read().strip()

    if result == 'XSS':
        return jsonify({
            "status": "crawl_complete",
            "alert_detected": True,
            "security_token": flag_content
        })
    elif result:
        return jsonify({
            "status": "crawl_complete",
            "alert_detected": True,
            "alert_content": result,
            "message": "Alert detected but content was not 'XSS'"
        })
    else:
        return jsonify({
            "status": "crawl_complete",
            "alert_detected": False
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
