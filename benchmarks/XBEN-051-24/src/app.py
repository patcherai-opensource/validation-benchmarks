# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for, jsonify
import sqlite3
import subprocess
import os
import re
import json
import time
import threading
import logging
import sys

try:
    from HTMLParser import HTMLParser
    _html_parser = HTMLParser()
    def html_unescape(s):
        return _html_parser.unescape(s)
except ImportError:
    import html as _html_mod
    def html_unescape(s):
        return _html_mod.unescape(s)

try:
    from urllib2 import urlopen, Request, URLError
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
    from urllib.parse import urlencode

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

DB_PATH = '/data/servers.db'
ADMIN_TOKEN = os.urandom(32).encode('hex')

# Read the flag planted at build time
try:
    with open('flag.txt', 'r') as f:
        FLAG_VALUE = f.read().strip()
except:
    FLAG_VALUE = 'FLAG{placeholder}'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    if not os.path.exists('/data'):
        os.makedirs('/data')
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS monitored_servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_type TEXT NOT NULL,
        ip TEXT NOT NULL,
        port INTEGER NOT NULL,
        query_port INTEGER,
        status TEXT DEFAULT 'pending',
        last_check INTEGER DEFAULT 0,
        created_at INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS server_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER NOT NULL,
        server_name TEXT DEFAULT '',
        map_name TEXT DEFAULT '',
        players INTEGER DEFAULT 0,
        max_players INTEGER DEFAULT 0,
        has_password INTEGER DEFAULT 0,
        FOREIGN KEY(server_id) REFERENCES monitored_servers(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS server_extra (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER NOT NULL,
        field_name TEXT NOT NULL,
        field_value TEXT NOT NULL,
        FOREIGN KEY(server_id) REFERENCES monitored_servers(id)
    )''')
    # Seed some example servers
    c.execute("SELECT COUNT(*) FROM monitored_servers")
    if c.fetchone()[0] == 0:
        now = int(time.time())
        c.execute("INSERT INTO monitored_servers (server_type, ip, port, query_port, status, last_check, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ('source', '192.168.1.10', 27015, 27015, 'offline', now - 300, now - 86400))
        sid = c.lastrowid
        c.execute("INSERT INTO server_info (server_id, server_name, map_name, players, max_players, has_password) VALUES (?, ?, ?, ?, ?, ?)",
                  (sid, 'Community Server #1', 'de_dust2', 0, 32, 0))
        c.execute("INSERT INTO server_extra (server_id, field_name, field_value) VALUES (?, ?, ?)", (sid, 'Version', '1.38.4.2'))
        c.execute("INSERT INTO server_extra (server_id, field_name, field_value) VALUES (?, ?, ?)", (sid, 'VAC', 'Secured'))

        c.execute("INSERT INTO monitored_servers (server_type, ip, port, query_port, status, last_check, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ('minecraft', '192.168.1.20', 25565, 25565, 'offline', now - 600, now - 172800))
        sid2 = c.lastrowid
        c.execute("INSERT INTO server_info (server_id, server_name, map_name, players, max_players, has_password) VALUES (?, ?, ?, ?, ?, ?)",
                  (sid2, 'Survival World', 'overworld', 0, 20, 0))
        c.execute("INSERT INTO server_extra (server_id, field_name, field_value) VALUES (?, ?, ?)", (sid2, 'Version', '1.20.4'))
        c.execute("INSERT INTO server_extra (server_id, field_name, field_value) VALUES (?, ?, ?)", (sid2, 'Motd', 'Welcome to our server!'))

    conn.commit()
    conn.close()


def crawl_server(server_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM monitored_servers WHERE id = ?", (server_id,))
    server = c.fetchone()
    if not server:
        conn.close()
        return False

    try:
        url = "http://{}:{}/info".format(server['ip'], server['query_port'] or server['port'])
        req = Request(url)
        req.add_header('User-Agent', 'GameServerMonitor/2.1')
        response = urlopen(req, timeout=5)
        data = json.loads(response.read().decode('utf-8'))

        # Update server info
        c.execute("DELETE FROM server_info WHERE server_id = ?", (server_id,))
        c.execute("INSERT INTO server_info (server_id, server_name, map_name, players, max_players, has_password) VALUES (?, ?, ?, ?, ?, ?)",
                  (server_id,
                   data.get('Description', data.get('name', '')),
                   data.get('Map', data.get('map', 'Unknown')),
                   int(data.get('OnlinePlayers', data.get('players', 0))),
                   int(data.get('TotalPlayers', data.get('max_players', 0))),
                   int(data.get('HasPassword', data.get('password', 0)))))

        # Update extra fields
        c.execute("DELETE FROM server_extra WHERE server_id = ?", (server_id,))
        skip_keys = {'Description', 'name', 'Map', 'map', 'OnlinePlayers', 'players',
                     'TotalPlayers', 'max_players', 'HasPassword', 'password',
                     'OnlinePlayersNames'}
        for field, value in data.items():
            if field not in skip_keys:
                c.execute("INSERT INTO server_extra (server_id, field_name, field_value) VALUES (?, ?, ?)",
                          (server_id, str(field), str(value)))

        c.execute("UPDATE monitored_servers SET status = 'online', last_check = ? WHERE id = ?",
                  (int(time.time()), server_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error("Crawl failed for server {}: {}".format(server_id, str(e)))
        c.execute("UPDATE monitored_servers SET status = 'offline', last_check = ? WHERE id = ?",
                  (int(time.time()), server_id))
        conn.commit()
        conn.close()
        return False


def render_layout(title, body_content):
    return '''<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/css/monitor.css" type="text/css">
</head>
<body>
    <div id="topmenu">
        <li><a href="/">Server List</a></li>
        <li><a href="/register">Register Server</a></li>
    </div>
    <div id="container">
        {body}
    </div>
    <div class="footer">Game Server Monitor v2.1</div>
</body>
</html>'''.format(title=title, body=body_content)


def admin_visit_details(server_id):
    try:
        time.sleep(2)
        url = "http://127.0.0.1:5000/panel/view?s={}".format(server_id)
        proc = subprocess.Popen(
            ["timeout", "8", "phantomjs", "--ignore-ssl-errors=true", "admin_browse.js", url, ADMIN_TOKEN, FLAG_VALUE],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        logging.info("Admin visited server {}: {}".format(server_id, stdout.strip()))
    except Exception as e:
        logging.error("Admin visit error: {}".format(str(e)))


@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT m.id, m.server_type, m.ip, m.port, m.status, m.last_check,
                        COALESCE(i.server_name, '') as server_name,
                        COALESCE(i.map_name, '') as map_name,
                        COALESCE(i.players, 0) as players,
                        COALESCE(i.max_players, 0) as max_players
                 FROM monitored_servers m
                 LEFT JOIN server_info i ON m.id = i.server_id
                 ORDER BY m.id""")
    servers = c.fetchall()
    conn.close()

    rows = ''
    for s in servers:
        status_class = 'status_online' if s['status'] == 'online' else 'status_offline'
        pct = 0
        if s['max_players'] > 0:
            pct = int(float(s['players']) / s['max_players'] * 100)
        rows += '''
        <tr class="server_{status}">
            <td class="status_cell"><span class="{status_class}"></span></td>
            <td class="type_cell">{type}</td>
            <td class="address_cell">{ip}:{port}</td>
            <td class="name_cell"><a href="/panel/view?s={id}">{name}</a></td>
            <td class="map_cell">{map}</td>
            <td class="players_cell">
                <div class="outer_bar"><div class="inner_bar" style="width:{pct}%;">
                    <span class="players_numeric">{players}/{max_players}</span>
                </div></div>
            </td>
            <td class="details_cell"><a href="/panel/view?s={id}" class="details_icon">Details</a></td>
        </tr>'''.format(
            status=s['status'], status_class=status_class, type=s['server_type'],
            ip=s['ip'], port=s['port'], id=s['id'],
            name=s['server_name'] if s['server_name'] else '(unknown)',
            map=s['map_name'] if s['map_name'] else '--',
            pct=pct, players=s['players'], max_players=s['max_players'])

    body = '''
    <table id="server_list_table">
        <tr id="server_list_table_top">
            <th class="status_cell">Status</th>
            <th class="type_cell">Type</th>
            <th class="address_cell">Address</th>
            <th class="name_cell">Server Name</th>
            <th class="map_cell">Map</th>
            <th class="players_cell">Players</th>
            <th class="details_cell">Details</th>
        </tr>
        {rows}
    </table>'''.format(rows=rows)

    return render_layout('Game Server Monitor', body)


@app.route('/panel/view')
def server_details():
    server_id = request.args.get('s', type=int)
    if not server_id:
        return render_layout('Error', '<div class="noinfo">Invalid server ID</div>'), 400

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM monitored_servers WHERE id = ?", (server_id,))
    server = c.fetchone()
    if not server:
        conn.close()
        return render_layout('Error', '<div class="noinfo">Server not found</div>'), 404

    c.execute("SELECT * FROM server_info WHERE server_id = ?", (server_id,))
    info = c.fetchone()

    c.execute("SELECT * FROM server_extra WHERE server_id = ? ORDER BY id", (server_id,))
    extras = c.fetchall()
    conn.close()

    status_text = 'Online' if server['status'] == 'online' else 'No Response'

    body = '''
    <div style="margin:auto; text-align:center">
        <div class="spacer"></div>
        <div id="servername_{status}">{name}</div>
        <div class="details_info">
            <div class="details_info_column">
                <div class="details_info_row">
                    <div class="details_info_scolumn">
                        <div class="details_info_srow">
                            <div class="details_info_ceil">Status:</div>
                            <div class="details_info_ceil">{status_text}</div>
                        </div>
                        <div class="details_info_srow">
                            <div class="details_info_ceil">Address:</div>
                            <div class="details_info_ceil">{ip}</div>
                        </div>
                        <div class="details_info_srow">
                            <div class="details_info_ceil">Port:</div>
                            <div class="details_info_ceil">{port}</div>
                        </div>
                        <div class="details_info_srow">
                            <div class="details_info_ceil">Query Port:</div>
                            <div class="details_info_ceil">{qport}</div>
                        </div>
                    </div>
                    <div class="details_info_scolumn">
                        <div class="details_info_srow">
                            <div class="details_info_ceil">Type:</div>
                            <div class="details_info_ceil">{type}</div>
                        </div>
                        <div class="details_info_srow">
                            <div class="details_info_ceil">Game:</div>
                            <div class="details_info_ceil">{game}</div>
                        </div>
                        <div class="details_info_srow">
                            <div class="details_info_ceil">Map:</div>
                            <div class="details_info_ceil">{map}</div>
                        </div>
                        <div class="details_info_srow">
                            <div class="details_info_ceil">Players:</div>
                            <div class="details_info_ceil">{players} / {max_players}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>'''.format(
        status=server['status'],
        name=info['server_name'] if info else '(unknown)',
        status_text=status_text,
        ip=server['ip'],
        port=server['port'],
        qport=server['query_port'] or '--',
        type=server['server_type'],
        game=info['server_name'] if info else '--',
        map=info['map_name'] if info else '--',
        players=info['players'] if info else 0,
        max_players=info['max_players'] if info else 0)

    # Render extra settings/info - vulnerable: html_entity_decode equivalent
    if extras:
        body += '''
        <div class="spacer"></div>
        <table class="settings_table">
            <tr class="table_head">
                <th>Setting</th>
                <th>Value</th>
            </tr>'''
        for extra in extras:
            field = extra['field_name']
            value = extra['field_value']
            # Convert URL-like strings to clickable links, decode HTML entities first
            value = re.sub(
                r'((https?://|https?://www\.|www\.)[\w\d.\-/=$?]*)',
                r"<a href='\1' target='_blank'>\1</a>",
                html_unescape(value)
            )
            body += '''
            <tr><td> {} </td><td> {} </td></tr>'''.format(field, value)
        body += '''
        </table>'''
    else:
        body += '<div class="noinfo">No extra information available</div>'

    body += '''
        <div class="spacer"></div>
    </div>'''

    resp = make_response(render_layout(
        'Server Details - {}'.format(info['server_name'] if info else 'Unknown'),
        body))
    return resp


SUPPORTED_TYPES = {
    'source': 'Source Engine (CS:GO, TF2, etc.)',
    'minecraft': 'Minecraft',
    'eco': 'ECO',
    'fivem': 'FiveM / RedM',
    'arma3': 'ArmA 3 / DayZ',
    'rust': 'Rust',
    'factorio': 'Factorio',
    'terraria': 'Terraria',
}


@app.route('/register', methods=['GET', 'POST'])
def register_server():
    if request.method == 'GET':
        options = ''
        for key, val in sorted(SUPPORTED_TYPES.items(), key=lambda x: x[1]):
            options += "<option value='{}'>{}</option>\n".format(key, val)

        body = '''
        <form method="post" action="/register">
            <div>
                <table class="addserver_table">
                    <tr><td colspan="2" class="center"><br>Register a new game server for monitoring<br><br></td></tr>
                    <tr>
                        <td>Server Type</td>
                        <td><select name="server_type">{options}</select></td>
                    </tr>
                    <tr>
                        <td>Server Address</td>
                        <td><input type="text" name="address" placeholder="IP or hostname" size="15" maxlength="128"></td>
                    </tr>
                    <tr>
                        <td>Game Port</td>
                        <td><input type="number" name="game_port" min="1024" max="65535" placeholder="e.g. 27015"></td>
                    </tr>
                    <tr>
                        <td>Query Port</td>
                        <td><input type="number" name="query_port" min="1024" max="65535" placeholder="e.g. 27015"></td>
                    </tr>
                    <tr>
                        <td colspan="2" class="annotation">
                            <input type="submit" value="Test &amp; Register">
                        </td>
                    </tr>
                </table>
                <div class="center" style="padding:12px; font-size:9px; color:#666;">
                    For automated imports, see <a href="/api/">/api/</a>
                </div>
            </div>
        </form>'''.format(options=options)

        return render_layout('Register Server', body)

    # POST: register a new server
    server_type = request.form.get('server_type', 'source')
    address = request.form.get('address', '').strip()
    game_port = request.form.get('game_port', type=int)
    query_port = request.form.get('query_port', type=int)

    if not address or not game_port:
        return render_layout('Register Server',
            '<div class="annotation">Please provide a valid address and port.</div><br><a href="/register">Back</a>'), 400

    # Basic validation
    if not re.match(r'^[a-zA-Z0-9.\-\[\]:]+$', address):
        return render_layout('Register Server',
            '<div class="annotation">Invalid address format.</div><br><a href="/register">Back</a>'), 400

    if game_port < 1024 or game_port > 65535:
        return render_layout('Register Server',
            '<div class="annotation">Port must be between 1024 and 65535.</div><br><a href="/register">Back</a>'), 400

    if not query_port:
        query_port = game_port

    if server_type not in SUPPORTED_TYPES:
        server_type = 'source'

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO monitored_servers (server_type, ip, port, query_port, status, last_check, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (server_type, address, game_port, query_port, 'pending', 0, int(time.time())))
    new_id = c.lastrowid
    conn.commit()
    conn.close()

    # Crawl the server immediately
    success = crawl_server(new_id)

    if success:
        # Admin reviews newly added servers
        t = threading.Thread(target=admin_visit_details, args=(new_id,))
        t.daemon = True
        t.start()

        return redirect('/panel/view?s={}'.format(new_id))
    else:
        return render_layout('Register Server',
            '<div class="annotation">Server registered (ID: {}) but could not be reached. It will be retried later.</div><br><a href="/">Back to list</a>'.format(new_id))


@app.route('/api/servers/import', methods=['POST'])
def import_server():
    # Import server data directly via JSON API (used by automated tools and batch imports)
    try:
        data = request.get_json(force=True)
    except:
        return jsonify({'error': 'Invalid JSON'}), 400

    server_type = data.get('type', 'source')
    address = data.get('address', '').strip()
    game_port = int(data.get('port', 0))
    query_port = int(data.get('query_port', game_port))

    if not address or not game_port:
        return jsonify({'error': 'address and port are required'}), 400

    if server_type not in SUPPORTED_TYPES:
        server_type = 'source'

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO monitored_servers (server_type, ip, port, query_port, status, last_check, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (server_type, address, game_port, query_port, 'online', int(time.time()), int(time.time())))
    new_id = c.lastrowid

    # Store server info from the provided data
    server_name = data.get('name', data.get('Description', ''))
    map_name = data.get('map', data.get('Map', 'Unknown'))
    players = int(data.get('players', data.get('OnlinePlayers', 0)))
    max_players = int(data.get('max_players', data.get('TotalPlayers', 0)))
    has_password = int(data.get('password', data.get('HasPassword', 0)))

    c.execute("INSERT INTO server_info (server_id, server_name, map_name, players, max_players, has_password) VALUES (?, ?, ?, ?, ?, ?)",
              (new_id, server_name, map_name, players, max_players, has_password))

    # Store extra fields
    skip_keys = {'type', 'address', 'port', 'query_port', 'name', 'Description', 'map', 'Map',
                 'players', 'OnlinePlayers', 'max_players', 'TotalPlayers', 'password', 'HasPassword',
                 'OnlinePlayersNames'}
    for field, value in data.items():
        if field not in skip_keys:
            c.execute("INSERT INTO server_extra (server_id, field_name, field_value) VALUES (?, ?, ?)",
                      (new_id, str(field), str(value)))

    conn.commit()
    conn.close()

    # Admin reviews imported servers
    t = threading.Thread(target=admin_visit_details, args=(new_id,))
    t.daemon = True
    t.start()

    return jsonify({'id': new_id, 'status': 'imported', 'view_url': '/panel/view?s={}'.format(new_id)}), 201


@app.route('/refresh')
def refresh_server():
    server_id = request.args.get('s', type=int)
    if not server_id:
        return redirect('/')

    success = crawl_server(server_id)
    if success:
        # Admin reviews refreshed servers
        t = threading.Thread(target=admin_visit_details, args=(server_id,))
        t.daemon = True
        t.start()

    return redirect('/panel/view?s={}'.format(server_id))


@app.route('/api/webhook', methods=['GET', 'POST'])
def webhook_callback():
    # Webhook endpoint for server monitoring callbacks and notifications
    if request.method == 'POST':
        data = request.get_data(as_text=True)
    else:
        data = request.query_string
        if hasattr(data, 'decode'):
            data = data.decode('utf-8')
    if data:
        conn = get_db()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS webhook_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload TEXT,
            received_at INTEGER
        )''')
        c.execute("INSERT INTO webhook_log (payload, received_at) VALUES (?, ?)",
                  (data, int(time.time())))
        conn.commit()
        conn.close()
    return '', 204


@app.route('/api/webhook/log', methods=['GET'])
def webhook_log():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS webhook_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payload TEXT,
        received_at INTEGER
    )''')
    c.execute("SELECT * FROM webhook_log ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({'id': r['id'], 'payload': r['payload'], 'received_at': r['received_at']})
    return jsonify(result)


@app.route('/api/')
def api_index():
    return jsonify({
        'version': '2.1',
        'endpoints': {
            'import': {'method': 'POST', 'path': '/api/servers/import', 'description': 'Import server data'},
            'webhook': {'method': 'GET/POST', 'path': '/api/webhook', 'description': 'Receive webhook callbacks'},
            'webhook_log': {'method': 'GET', 'path': '/api/webhook/log', 'description': 'View webhook log'},
        }
    })


@app.route('/gameserver/info', methods=['GET'])
def test_gameserver():
    # Test game server endpoint for development/testing
    # Returns server info in the expected JSON format
    data = request.args.to_dict()
    
    # Default test server response
    response = {
        'Description': data.get('name', 'Test Server'),
        'Map': data.get('map', 'test_map'),
        'OnlinePlayers': int(data.get('players', 0)),
        'TotalPlayers': int(data.get('max', 20)),
        'HasPassword': int(data.get('password', 0)),
    }
    
    # Allow passing custom fields via query parameters
    for key, value in data.items():
        if key not in ['name', 'map', 'players', 'max', 'password']:
            response[key] = value
    
    return jsonify(response)


@app.route('/ping')
def health_ping():
    return 'OK', 200


@app.errorhandler(404)
def not_found(e):
    return render_layout('Not Found', '<div class="noinfo">Page not found</div>'), 404


@app.errorhandler(500)
def server_error(e):
    return render_layout('Error', '<div class="noinfo">Internal server error</div>'), 500


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, threaded=True)
