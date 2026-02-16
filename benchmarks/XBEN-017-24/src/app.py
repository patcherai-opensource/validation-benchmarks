# encoding=utf8

from flask import Flask, request, make_response, redirect, url_for, jsonify
import subprocess
import os
import re
import json
import time
import urllib2
import sys
import sqlite3
import threading

try:
    from HTMLParser import HTMLParser
    html_unescape = HTMLParser().unescape
except:
    import html
    html_unescape = html.unescape

import cgi

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

DATABASE = '/python-docker/data/servers.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db_dir = os.path.dirname(DATABASE)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS monitored_hosts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        host_type TEXT NOT NULL,
        address TEXT NOT NULL,
        query_port INTEGER NOT NULL,
        connect_port INTEGER NOT NULL,
        zone INTEGER DEFAULT 0,
        disabled INTEGER DEFAULT 0,
        comment TEXT DEFAULT '',
        cache TEXT DEFAULT '{}',
        cache_time INTEGER DEFAULT 0
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS collector_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        req_id TEXT NOT NULL,
        payload TEXT NOT NULL,
        created_at INTEGER NOT NULL
    )''')
    db.commit()
    db.close()

def read_flag():
    try:
        with open('/python-docker/secret.txt') as f:
            return f.read().strip()
    except:
        return 'FLAG{placeholder}'

def sanitize_server_value(value):
    """HTML-encode server data values for safe storage"""
    if isinstance(value, basestring):
        return cgi.escape(value, quote=True)
    elif isinstance(value, list):
        return [sanitize_server_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: sanitize_server_value(v) for k, v in value.items()}
    return value

def sanitize_server_data(data):
    """Process and sanitize all server data fields"""
    result = {}
    for key, value in data.items():
        result[key] = sanitize_server_value(value)
    return result

def fetch_host_data(address, query_port, host_type):
    """Crawl host info endpoint and return parsed data"""
    try:
        url = 'http://{}:{}/info'.format(address, query_port)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'ServerMonitor/2.1')
        response = urllib2.urlopen(req, timeout=5)
        raw = response.read()
        data = json.loads(raw)
        return sanitize_server_data(data)
    except Exception:
        return None

def refresh_host_cache(host_id):
    db = get_db()
    row = db.execute('SELECT * FROM monitored_hosts WHERE id = ?', (host_id,)).fetchone()
    if not row:
        db.close()
        return False

    data = fetch_host_data(row['address'], row['query_port'], row['host_type'])
    if data:
        db.execute('UPDATE monitored_hosts SET cache = ?, cache_time = ? WHERE id = ?',
                   (json.dumps(data), int(time.time()), host_id))
        db.commit()
        db.close()
        return True
    db.close()
    return False

def render_field_value(value):
    """Process field value for display - linkify URLs"""
    if not isinstance(value, basestring):
        value = str(value)
    decoded = html_unescape(value)
    linked = re.sub(
        r'((https?://|https?://www\.|www\.)[\w\d.\-/=$?]*)',
        r"<a href='\1' target='_blank'>\1</a>",
        decoded
    )
    return linked


STYLE_CSS = """
body {
  background-color: #191919;
  font-size: 11px;
  font-family: verdana, tahoma, arial;
  word-wrap: break-word;
  color: white;
  font-weight: bold;
  margin: 0;
  padding: 0;
}
a:link, a:visited { text-decoration: none; color: #0088DD; }
a:hover { color: #adcef1; }
#topmenu { padding: 1em; border-bottom: 2px dashed black; }
#topmenu li { display: inline-block; padding: 0 10px; list-style: none; }
#topmenu li:before { content: '\\25BA '; }
#container { padding: 20px; }
.spacer { height: 20px; }
table { border-collapse: collapse; margin: auto; }
th, td { padding: 8px; border: 1px solid #22252f; }
tr:nth-child(even) { background-color: rgba(26, 28, 34, 0.2); }
tr:nth-child(odd) { background-color: rgba(26, 28, 34, 0.1); }
.table_head { background-color: #22252f; }
.table_head th { text-align: left; }
.center { text-align: center; }
.status_online { color: #00cc00; }
.status_offline { color: #cc0000; }
.noinfo { text-align: center; padding: 20px; color: #888; }
input[type="text"], input[type="number"], select, textarea {
  background-color: #282828; color: white; border: 1px solid #444; padding: 4px 8px;
}
input[type="submit"] {
  background-color: #0088DD; color: white; border: none; padding: 8px 16px; cursor: pointer;
}
input[type="submit"]:hover { background-color: #006aaa; }
.annotation { text-align: center; background-color: #282828; padding: 17px; }
.settings_table { max-width: 600px; margin: auto; }
.settings_table td { white-space: pre-wrap; }
.details_info { margin: 10px auto; max-width: 500px; }
.details_info td:first-child { font-weight: bold; width: 120px; }
#servername_online { font-size: 18px; color: #0f0; text-align: center; padding: 10px; }
#servername_offline { font-size: 18px; color: #f00; text-align: center; padding: 10px; }
.players_table { margin: auto; }
.outer_bar { background: #333; width: 100px; height: 16px; display: inline-block; }
.inner_bar { background: #0088DD; height: 100%; }
.footer { text-align: center; font-family: tahoma; font-size: 9px; padding: 33px 0 11px 0; }
.addserver_table { margin: auto; }
.addserver_table td { padding: 6px; }
"""

def page_header(title="Live Server Monitor"):
    return """<!DOCTYPE html>
<html>
<head>
  <title>{title}</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>{css}</style>
</head>
<body>
  <ul id="topmenu">
    <li><a href="/">Server List</a></li>
    <li><a href="/register">Add Server</a></li>
  </ul>
  <div id="container">
""".format(title=title, css=STYLE_CSS)

def page_footer():
    return """
  </div>
  <div class="footer"><a href="#" style="text-decoration:none">Live Server Monitor v2.1.0</a></div>
</body>
</html>"""


@app.route('/')
def server_list():
    db = get_db()
    hosts = db.execute('SELECT * FROM monitored_hosts WHERE disabled = 0 ORDER BY id').fetchall()
    db.close()

    output = page_header("Live Server Monitor")
    output += """
    <table id="server_list_table" style="width:100%">
      <tr class="table_head">
        <th>Status</th>
        <th>Address</th>
        <th>Server Name</th>
        <th>Map</th>
        <th>Players</th>
        <th>Details</th>
      </tr>"""

    for host in hosts:
        cache = json.loads(host['cache']) if host['cache'] else {}
        name = cache.get('Description', cache.get('name', 'Unknown'))
        smap = cache.get('map', cache.get('Map', 'N/A'))
        players = cache.get('OnlinePlayers', cache.get('players', 0))
        playersmax = cache.get('TotalPlayers', cache.get('playersmax', 0))
        online = host['cache_time'] > 0 and cache

        status_class = 'status_online' if online else 'status_offline'
        status_text = 'Online' if online else 'Offline'

        output += """
      <tr>
        <td class="{status_class}">{status_text}</td>
        <td>{address}:{connect_port}</td>
        <td>{name}</td>
        <td>{smap}</td>
        <td>{players}/{playersmax}</td>
        <td><a href="/details?s={host_id}">View</a></td>
      </tr>""".format(
            status_class=status_class,
            status_text=status_text,
            address=host['address'],
            connect_port=host['connect_port'],
            name=name[:50] if isinstance(name, basestring) else str(name)[:50],
            smap=str(smap)[:30],
            players=players,
            playersmax=playersmax,
            host_id=host['id']
        )

    if not hosts:
        output += '<tr><td colspan="6" class="noinfo">No servers registered yet. <a href="/register">Add one</a>.</td></tr>'

    output += """
    </table>"""
    output += page_footer()
    return output


@app.route('/details')
def host_details():
    host_id = request.args.get('s', '')
    try:
        host_id = int(host_id)
    except (ValueError, TypeError):
        return page_header("Error") + '<div class="noinfo">Invalid server ID</div>' + page_footer(), 400

    db = get_db()
    row = db.execute('SELECT * FROM monitored_hosts WHERE id = ?', (host_id,)).fetchone()
    db.close()

    if not row:
        return page_header("Error") + '<div class="noinfo">Server not found</div>' + page_footer(), 404

    cache = json.loads(row['cache']) if row['cache'] else {}

    name = cache.get('Description', cache.get('name', 'Unknown'))
    smap = cache.get('map', cache.get('Map', 'N/A'))
    players = cache.get('OnlinePlayers', cache.get('players', 0))
    playersmax = cache.get('TotalPlayers', cache.get('playersmax', 0))
    game = cache.get('game', cache.get('Game', row['host_type']))
    online = row['cache_time'] > 0 and cache

    status_text = 'Online' if online else 'No Response'

    output = page_header("{} | {}".format("Live Server Monitor", name))

    output += '<div style="margin:auto; text-align:center">'
    output += '<div class="spacer"></div>'

    if online:
        output += '<div id="servername_online"> {} </div>'.format(name)
    else:
        output += '<div id="servername_offline"> {} </div>'.format(name)

    output += """
    <table class="details_info">
      <tr><td>Status</td><td>{status}</td></tr>
      <tr><td>Address</td><td>{address}</td></tr>
      <tr><td>Connect Port</td><td>{c_port}</td></tr>
      <tr><td>Query Port</td><td>{q_port}</td></tr>
      <tr><td>Type</td><td>{host_type}</td></tr>
      <tr><td>Game</td><td>{game}</td></tr>
      <tr><td>Map</td><td>{smap}</td></tr>
      <tr><td>Players</td><td>{players} / {playersmax}</td></tr>
    </table>""".format(
        status=status_text,
        address=row['address'],
        c_port=row['connect_port'],
        q_port=row['query_port'],
        host_type=row['host_type'],
        game=game,
        smap=smap,
        players=players,
        playersmax=playersmax
    )

    output += '<div class="spacer"></div>'

    # Players list
    online_names = cache.get('OnlinePlayersNames', cache.get('player_names', []))
    if online_names and isinstance(online_names, list):
        output += '<table class="players_table">'
        output += '<tr class="table_head"><th>Player Name</th></tr>'
        for pname in online_names:
            output += '<tr><td> {} </td></tr>'.format(pname)
        output += '</table>'
    else:
        output += '<div class="noinfo">No player information available</div>'

    output += '<div class="spacer"></div>'

    # Server settings/extras - renders untrusted data with html_unescape
    skip_keys = {'Description', 'name', 'map', 'Map', 'OnlinePlayers', 'TotalPlayers',
                 'players', 'playersmax', 'game', 'Game', 'HasPassword', 'password',
                 'OnlinePlayersNames', 'player_names'}

    extras = {k: v for k, v in cache.items() if k not in skip_keys}

    if extras:
        output += """
        <table class="settings_table">
          <tr class="table_head">
            <th>Setting</th>
            <th>Value</th>
          </tr>"""

        for field, value in extras.items():
            rendered_value = render_field_value(value)
            output += """
          <tr><td> {} </td><td> {} </td></tr>""".format(field, rendered_value)

        output += """
        </table>"""
    else:
        output += '<div class="noinfo">No extended information available</div>'

    output += '<div class="spacer"></div>'

    # Refresh and report links
    output += '<div class="center">'
    output += '<a href="/crawl?s={}&redirect=1">Refresh Data</a>'.format(host_id)
    output += ' | <a href="/report?s={}">Report Server</a>'.format(host_id)
    output += '</div>'

    output += '<div class="spacer"></div>'
    output += '</div>'
    output += page_footer()
    return output


@app.route('/register', methods=['GET', 'POST'])
def register_host():
    if request.method == 'GET':
        type_list = [
            ('source', 'Source Engine (HL2, CS:GO, etc.)'),
            ('minecraft', 'Minecraft'),
            ('fivem', 'FiveM / RedM'),
            ('eco', 'ECO'),
            ('arma3', 'ArmA 3 / DayZ'),
            ('farmsim', 'Farming Simulator'),
            ('factorio', 'Factorio'),
            ('terraria', 'Terraria'),
            ('palworld', 'Palworld'),
            ('beammp', 'BeamMP'),
            ('rust', 'Rust'),
            ('valheim', 'Valheim'),
        ]

        output = page_header("Add Server | Live Server Monitor")
        output += """
        <form method="post" action="/register">
          <table class="addserver_table">
            <tr><td colspan="2" class="center"><br>Register a new server to be monitored<br><br></td></tr>
            <tr>
              <td>Type</td>
              <td><select name="host_type">"""
        for key, val in type_list:
            output += '<option value="{}">{}</option>'.format(key, val)

        output += """</select></td>
            </tr>
            <tr><td>Address</td><td><input type="text" name="address" size="15" maxlength="128" placeholder="192.168.1.1"></td></tr>
            <tr><td>Connect Port</td><td><input type="number" name="connect_port" min="1024" max="65535" value="27015"></td></tr>
            <tr><td>Query Port</td><td><input type="number" name="query_port" min="1024" max="65535" value="27015"></td></tr>
            <tr><td colspan="2" class="annotation"><input type="submit" name="submit_test" value="Test &amp; Add Server"></td></tr>
          </table>
        </form>"""
        output += page_footer()
        return output

    host_type = request.form.get('host_type', 'source')
    address = request.form.get('address', '').strip()
    connect_port = request.form.get('connect_port', '27015')
    query_port = request.form.get('query_port', '27015')

    try:
        connect_port = int(connect_port)
        query_port = int(query_port)
    except ValueError:
        return page_header("Error") + '<div class="annotation">Invalid port numbers</div>' + page_footer(), 400

    if not address:
        return page_header("Error") + '<div class="annotation">Address is required</div>' + page_footer(), 400

    if connect_port < 1024 or connect_port > 65535 or query_port < 1024 or query_port > 65535:
        return page_header("Error") + '<div class="annotation">Port must be between 1024 and 65535</div>' + page_footer(), 400

    data = fetch_host_data(address, query_port, host_type)

    output = page_header("Add Server | Live Server Monitor")

    if data:
        db = get_db()
        db.execute(
            'INSERT INTO monitored_hosts (host_type, address, query_port, connect_port, cache, cache_time) VALUES (?, ?, ?, ?, ?, ?)',
            (host_type, address, query_port, connect_port, json.dumps(data), int(time.time()))
        )
        db.commit()
        new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        db.close()

        name = data.get('Description', data.get('name', 'Unknown'))
        output += '<div class="annotation">Server added successfully!</div>'
        output += '<div class="center"><br>'
        output += '<strong>{}</strong> at {}:{}'.format(name, address, connect_port)
        output += '<br><br><a href="/details?s={}">View Server Details</a>'.format(new_id)
        output += ' | <a href="/">Back to List</a>'
        output += '</div>'
    else:
        output += '<div class="annotation">Could not connect to server at {}:{}. Please check the address and port.</div>'.format(address, query_port)
        output += '<div class="center"><br><a href="/register">Try Again</a></div>'

    output += page_footer()
    return output


@app.route('/api/v1/submit', methods=['POST'])
def api_submit_data():
    """API endpoint for game servers to push their status data directly.
    Used by server plugins that push data instead of waiting for crawl."""
    try:
        data = request.get_json(force=True)
    except:
        return jsonify({'error': 'Invalid JSON'}), 400

    if not data:
        return jsonify({'error': 'Empty payload'}), 400

    address = data.pop('_address', request.remote_addr)
    port = data.pop('_port', 27015)
    host_type = data.pop('_type', 'source')

    try:
        port = int(port)
    except (ValueError, TypeError):
        port = 27015

    data = sanitize_server_data(data)

    db = get_db()
    existing = db.execute(
        'SELECT id FROM monitored_hosts WHERE address = ? AND query_port = ?',
        (address, port)
    ).fetchone()

    if existing:
        db.execute('UPDATE monitored_hosts SET cache = ?, cache_time = ? WHERE id = ?',
                   (json.dumps(data), int(time.time()), existing['id']))
        db.commit()
        host_id = existing['id']
    else:
        db.execute(
            'INSERT INTO monitored_hosts (host_type, address, query_port, connect_port, cache, cache_time) VALUES (?, ?, ?, ?, ?, ?)',
            (host_type, address, port, port, json.dumps(data), int(time.time()))
        )
        db.commit()
        host_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]

    db.close()
    return jsonify({'status': 'ok', 'id': host_id})


@app.route('/crawl')
def crawl_host():
    host_id = request.args.get('s', '')
    try:
        host_id = int(host_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid server ID'}), 400

    success = refresh_host_cache(host_id)

    if request.args.get('redirect'):
        return redirect('/details?s={}'.format(host_id))

    if success:
        return jsonify({'status': 'ok', 'message': 'Server data refreshed'})
    else:
        return jsonify({'status': 'error', 'message': 'Could not reach server'}), 502


@app.route('/report')
def report_page():
    """Report a server for admin review. The monitoring bot will visit the server's details page."""
    host_id = request.args.get('s', '')
    try:
        host_id = int(host_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid server ID'}), 400

    db = get_db()
    row = db.execute('SELECT * FROM monitored_hosts WHERE id = ?', (host_id,)).fetchone()
    db.close()

    if not row:
        return jsonify({'error': 'Server not found'}), 404

    flag = read_flag()

    def run_bot():
        try:
            host = os.environ.get('APP_HOST', 'localhost')
            port = os.environ.get('APP_PORT', '5000')
            details_url = 'http://{}:{}/details?s={}'.format(host, port, host_id)

            proc = subprocess.Popen(
                ['timeout', '15', 'phantomjs', '--ignore-ssl-errors=true', 'bot_visit.js', details_url, flag],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            proc.wait()
        except Exception:
            pass

    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()

    return jsonify({'status': 'ok', 'message': 'Report received. An administrator will review this server shortly.'})


@app.route('/collector', methods=['GET', 'POST'])
def collector_endpoint():
    """Webhook endpoint for monitoring alerts and notifications"""
    req_id = request.args.get('id', '')

    if request.method == 'POST':
        if not req_id:
            req_id = os.urandom(8).encode('hex')
        payload = request.get_data()
        db = get_db()
        db.execute('INSERT INTO collector_log (req_id, payload, created_at) VALUES (?, ?, ?)',
                   (req_id, payload, int(time.time())))
        db.commit()
        db.close()
        return jsonify({'status': 'stored', 'id': req_id})

    else:
        data_param = request.args.get('data', '')
        if data_param and req_id:
            db = get_db()
            db.execute('INSERT INTO collector_log (req_id, payload, created_at) VALUES (?, ?, ?)',
                       (req_id, data_param, int(time.time())))
            db.commit()
            db.close()
            resp = make_response('', 204)
            return resp

        if not req_id:
            return jsonify({'error': 'Missing id parameter'}), 400

        db = get_db()
        rows = db.execute('SELECT * FROM collector_log WHERE req_id = ? ORDER BY created_at DESC', (req_id,)).fetchall()
        db.close()

        if not rows:
            return jsonify({'entries': []})

        entries = [{'payload': r['payload'], 'created_at': r['created_at']} for r in rows]
        return jsonify({'entries': entries})


@app.route('/api/v1/status')
def api_status():
    """API health and version endpoint"""
    db = get_db()
    count = db.execute('SELECT COUNT(*) FROM monitored_hosts WHERE disabled = 0').fetchone()[0]
    db.close()
    return jsonify({
        'service': 'Live Server Monitor',
        'version': '2.1.0',
        'monitored_servers': count,
        'api': '/api/v1'
    })


@app.route('/api/v1')
def api_docs():
    """API reference"""
    return jsonify({
        'submit': {'method': 'POST', 'path': '/api/v1/submit', 'description': 'Push server status data. JSON body with server fields. Use _address, _port, _type for server metadata.'},
        'status': {'method': 'GET', 'path': '/api/v1/status', 'description': 'Service health check'},
        'collector': {'method': 'GET/POST', 'path': '/collector?id=<req_id>', 'description': 'Webhook collector for monitoring alerts. POST to store, GET to retrieve.'},
    })


@app.route('/ping')
def health_ping():
    return 'OK'


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, threaded=True)
