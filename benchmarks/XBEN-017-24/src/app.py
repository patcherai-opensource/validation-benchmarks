# encoding=utf8

from flask import Flask, request, redirect, jsonify
import subprocess
import os
import re
import json
import sqlite3
import cgi
import sys
import logging
from HTMLParser import HTMLParser

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

_html_parser = HTMLParser()

def _escape(s):
    """Escape HTML special characters."""
    return cgi.escape(str(s), quote=True)

def _unescape(s):
    """Unescape HTML entities (mirrors PHP html_entity_decode)."""
    return _html_parser.unescape(s)

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

DB_PATH = '/tmp/lgsl.db'

def get_flag():
    try:
        return open('secret.txt').read().strip()
    except IOError:
        return 'FLAG{placeholder}'

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL,
        port INTEGER NOT NULL,
        query_port INTEGER NOT NULL,
        game_type TEXT DEFAULT '',
        status INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS server_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER NOT NULL,
        field TEXT NOT NULL,
        value TEXT NOT NULL,
        FOREIGN KEY (server_id) REFERENCES servers(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS server_players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        score INTEGER DEFAULT 0,
        FOREIGN KEY (server_id) REFERENCES servers(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS admin_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER NOT NULL,
        output TEXT NOT NULL,
        reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (server_id) REFERENCES servers(id)
    )''')
    # Seed some default servers
    c.execute("SELECT COUNT(*) FROM servers")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO servers (ip, port, query_port, game_type) VALUES (?, ?, ?, ?)",
                  ("192.168.1.10", 27015, 27016, "source"))
        sid = c.lastrowid
        for field, value in [("hostname", "Community Gaming Server #1"),
                             ("map", "de_dust2"),
                             ("game", "Counter-Strike: Source"),
                             ("players", "12/32"),
                             ("version", "1.0.0.75"),
                             ("website", "https://example-gaming.com/server1")]:
            c.execute("INSERT INTO server_info (server_id, field, value) VALUES (?, ?, ?)",
                      (sid, field, value))
        for name, score in [("Player1", 24), ("FragMaster", 18), ("n00bSlayer", 12)]:
            c.execute("INSERT INTO server_players (server_id, name, score) VALUES (?, ?, ?)",
                      (sid, name, score))

        c.execute("INSERT INTO servers (ip, port, query_port, game_type) VALUES (?, ?, ?, ?)",
                  ("10.0.0.5", 7777, 7778, "http"))
        sid2 = c.lastrowid
        for field, value in [("hostname", "Survival World - PvE"),
                             ("map", "TheIsland"),
                             ("game", "ARK: Survival"),
                             ("players", "8/70"),
                             ("version", "354.2"),
                             ("website", "https://www.ark-survival-server.net")]:
            c.execute("INSERT INTO server_info (server_id, field, value) VALUES (?, ?, ?)",
                      (sid2, field, value))

    conn.commit()
    conn.close()

init_db()

# -------------------------------------------------------
# Rendering functions (mirrors lgsl_details.php patterns)
# -------------------------------------------------------

def lgsl_render_server_details(server_id):
    """Render server extra info fields into HTML table rows.
    Mirrors lgsl_details.php rendering logic."""
    conn = get_db()
    rows = conn.execute("SELECT field, value FROM server_info WHERE server_id = ?", (server_id,)).fetchall()
    conn.close()

    output = ""
    for row in rows:
        field = row['field']
        value = row['value']

        # Convert entities back for display (mirrors html_entity_decode in PHP)
        value = _unescape(value)

        # Auto-link URLs (mirrors preg_replace in lgsl_details.php)
        value = re.sub(
            r'((https*://|https*://www\.|www\.)[\w\d.\-/=$?]*)',
            r"<a href='\1' target='_blank'>\1</a>",
            value
        )

        output += "\n    <tr><td> {} </td><td> {} </td></tr>".format(field, value)

    return output


def lgsl_render_players(server_id):
    conn = get_db()
    players = conn.execute("SELECT name, score FROM server_players WHERE server_id = ?", (server_id,)).fetchall()
    conn.close()
    if not players:
        return "<tr><td colspan='2'>No players online</td></tr>"
    output = ""
    for p in players:
        output += "\n    <tr><td>{}</td><td>{}</td></tr>".format(
            _escape(str(p['name'])), _escape(str(p['score'])))
    return output


# -------------------------------------------------------
# Admin bot: simulates admin visiting details page
# -------------------------------------------------------

def admin_visit(server_id):
    """Simulate an admin reviewing a server details page.
    The admin's browser has the flag in a cookie.
    Returns any alert/prompt/confirm messages captured during the visit."""
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/server/{}/details'.format(host, port, server_id)
    flag = get_flag()

    try:
        proc = subprocess.Popen(
            ["timeout", "10", "phantomjs", "--ignore-ssl-errors=true", "admin_visit.js", url, flag],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        result = stdout.strip() if stdout else ""
        return result
    except Exception as e:
        logging.error("Admin visit failed: {}".format(str(e)))
        return ""


# -------------------------------------------------------
# Routes
# -------------------------------------------------------

@app.route('/')
def index():
    conn = get_db()
    servers = conn.execute("SELECT s.*, (SELECT value FROM server_info WHERE server_id=s.id AND field='hostname' LIMIT 1) as hostname, (SELECT value FROM server_info WHERE server_id=s.id AND field='game' LIMIT 1) as game, (SELECT value FROM server_info WHERE server_id=s.id AND field='players' LIMIT 1) as players, (SELECT value FROM server_info WHERE server_id=s.id AND field='map' LIMIT 1) as map FROM servers s ORDER BY s.id").fetchall()
    conn.close()

    rows_html = ""
    for s in servers:
        hostname = _escape(str(s['hostname'] or s['ip']))
        game = _escape(str(s['game'] or 'Unknown'))
        players = _escape(str(s['players'] or '-'))
        map_name = _escape(str(s['map'] or '-'))
        rows_html += """
        <tr>
            <td><a href="/server/{id}/details">{hostname}</a></td>
            <td>{game}</td>
            <td>{map}</td>
            <td>{players}</td>
            <td>{ip}:{port}</td>
        </tr>""".format(
            id=s['id'], hostname=hostname, game=game,
            map=map_name, players=players,
            ip=_escape(str(s['ip'])), port=s['port']
        )

    return """<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Live Game Server List</title>
    <link rel="stylesheet" type="text/css" href="/static/css/lgsl.css">
</head>
<body>
<div class="lgsl-wrapper">
    <div class="lgsl-header">
        <h1>Live Game Server List</h1>
        <p>Real-time game server monitoring and status</p>
    </div>
    <div class="lgsl-nav">
        <a href="/">Server List</a>
        <a href="/admin/add">Add Server</a>
    </div>
    <table class="lgsl-table">
        <thead>
            <tr>
                <th>Server Name</th>
                <th>Game</th>
                <th>Map</th>
                <th>Players</th>
                <th>Address</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    <div class="lgsl-footer">
        <p>LGSL v6.2.0 &mdash; Live Game Server Listing</p>
    </div>
</div>
</body>
</html>""".format(rows=rows_html)


@app.route('/server/<int:server_id>/details')
def server_details(server_id):
    conn = get_db()
    server = conn.execute("SELECT * FROM servers WHERE id = ?", (server_id,)).fetchone()
    if not server:
        conn.close()
        return "<h1>Server not found</h1>", 404

    reviews = conn.execute("SELECT output, reviewed_at FROM admin_reviews WHERE server_id = ? ORDER BY reviewed_at DESC LIMIT 5", (server_id,)).fetchall()
    conn.close()

    info_rows = lgsl_render_server_details(server_id)
    player_rows = lgsl_render_players(server_id)

    review_html = ""
    if reviews:
        review_html = '<div class="lgsl-detail-section"><h2>Admin Review Log</h2><table class="lgsl-table">'
        for r in reviews:
            review_html += "<tr><td>{}</td><td>{}</td></tr>".format(
                _escape(str(r['reviewed_at'])),
                _escape(str(r['output']))
            )
        review_html += "</table></div>"

    return """<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Server Details</title>
    <link rel="stylesheet" type="text/css" href="/static/css/lgsl.css">
</head>
<body>
<div class="lgsl-wrapper">
    <div class="lgsl-header">
        <h1>Server Details</h1>
    </div>
    <div class="lgsl-nav">
        <a href="/">Server List</a>
        <a href="/admin/add">Add Server</a>
    </div>
    <div class="lgsl-detail-section">
        <h2>Connection Info</h2>
        <table class="lgsl-table">
            <tr><td>IP Address</td><td>{ip}</td></tr>
            <tr><td>Game Port</td><td>{port}</td></tr>
            <tr><td>Query Port</td><td>{qport}</td></tr>
            <tr><td>Type</td><td>{gtype}</td></tr>
        </table>
    </div>
    <div class="lgsl-detail-section">
        <h2>Server Information</h2>
        <table class="lgsl-table">
            {info_rows}
        </table>
    </div>
    <div class="lgsl-detail-section">
        <h2>Online Players</h2>
        <table class="lgsl-table">
            <thead><tr><th>Name</th><th>Score</th></tr></thead>
            <tbody>
                {player_rows}
            </tbody>
        </table>
    </div>
    {review_section}
    <div class="lgsl-footer">
        <p>LGSL v6.2.0 &mdash; Live Game Server Listing</p>
    </div>
</div>
</body>
</html>""".format(
        ip=_escape(str(server['ip'])),
        port=server['port'],
        qport=server['query_port'],
        gtype=_escape(str(server['game_type'])),
        info_rows=info_rows,
        player_rows=player_rows,
        review_section=review_html
    )


@app.route('/admin/add', methods=['GET'])
def add_server_form():
    return """<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Add Server</title>
    <link rel="stylesheet" type="text/css" href="/static/css/lgsl.css">
</head>
<body>
<div class="lgsl-wrapper">
    <div class="lgsl-header">
        <h1>Add Game Server</h1>
    </div>
    <div class="lgsl-nav">
        <a href="/">Server List</a>
        <a href="/admin/add">Add Server</a>
    </div>
    <div class="lgsl-detail-section">
        <form method="POST" action="/admin/add" class="lgsl-form">
            <div class="form-group">
                <label for="ip">Server IP:</label>
                <input type="text" name="ip" id="ip" required placeholder="192.168.1.1">
            </div>
            <div class="form-group">
                <label for="port">Game Port:</label>
                <input type="number" name="port" id="port" required placeholder="27015" value="27015">
            </div>
            <div class="form-group">
                <label for="query_port">Query Port:</label>
                <input type="number" name="query_port" id="query_port" required placeholder="27016" value="27016">
            </div>
            <div class="form-group">
                <label for="game_type">Game Type:</label>
                <select name="game_type" id="game_type">
                    <option value="source">Source Engine</option>
                    <option value="http">HTTP Query (JSON)</option>
                    <option value="gamespy">GameSpy</option>
                    <option value="quake3">Quake 3</option>
                </select>
            </div>
            <div class="form-group">
                <label for="server_info">Server Info (JSON):</label>
                <textarea name="server_info" id="server_info" rows="8" cols="50" placeholder='{"hostname": "My Server", "map": "de_dust2", "game": "CS:Source", "players": "0/32"}'></textarea>
                <small>Paste the JSON response from the server's info query, or leave empty to query automatically.</small>
            </div>
            <button type="submit" class="lgsl-btn">Add Server</button>
        </form>
    </div>
    <div class="lgsl-footer">
        <p>LGSL v6.2.0 &mdash; Live Game Server Listing</p>
    </div>
</div>
</body>
</html>"""


@app.route('/admin/add', methods=['POST'])
def add_server():
    ip = request.form.get('ip', '').strip()
    port = request.form.get('port', '27015').strip()
    query_port = request.form.get('query_port', '27016').strip()
    game_type = request.form.get('game_type', 'source').strip()
    server_info_raw = request.form.get('server_info', '').strip()

    if not ip:
        return "Missing server IP", 400

    try:
        port = int(port)
        query_port = int(query_port)
    except ValueError:
        return "Invalid port number", 400

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO servers (ip, port, query_port, game_type) VALUES (?, ?, ?, ?)",
              (ip, port, query_port, game_type))
    server_id = c.lastrowid

    # Process server info JSON (simulates lgsl_query_40 fetching from /info endpoint)
    if server_info_raw:
        try:
            info_data = json.loads(server_info_raw)
            if isinstance(info_data, dict):
                for field, value in info_data.items():
                    c.execute("INSERT INTO server_info (server_id, field, value) VALUES (?, ?, ?)",
                              (server_id, str(field), str(value)))
        except (ValueError, TypeError):
            conn.rollback()
            conn.close()
            return "Invalid JSON in server info field", 400

    conn.commit()
    conn.close()

    # Trigger admin review of the newly added server
    review_output = admin_visit(server_id)

    # Store admin review results
    if review_output:
        conn2 = get_db()
        conn2.execute("INSERT INTO admin_reviews (server_id, output) VALUES (?, ?)",
                      (server_id, review_output))
        conn2.commit()
        conn2.close()

    return redirect('/server/{}/details'.format(server_id))


@app.route('/server/<int:server_id>/refresh')
def refresh_server(server_id):
    """Re-query a server and update info. Triggers admin review."""
    conn = get_db()
    server = conn.execute("SELECT * FROM servers WHERE id = ?", (server_id,)).fetchone()
    conn.close()
    if not server:
        return "Server not found", 404

    admin_visit(server_id)
    return redirect('/server/{}/details'.format(server_id))


@app.route('/ping')
def health_ping():
    return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
