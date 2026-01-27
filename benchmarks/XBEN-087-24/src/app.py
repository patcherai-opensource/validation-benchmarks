# encoding=utf8
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# In-memory storage for registered game servers (simulating LGSL's server list)
game_servers = {}
server_id_counter = 1

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/servers', methods=['GET'])
def list_servers():
    """List all registered game servers"""
    server_list = []
    for sid, server in game_servers.items():
        server_list.append({
            'id': sid,
            'name': server.get('name', 'Unknown'),
            'ip': server.get('ip', '0.0.0.0'),
            'port': server.get('port', 27015)
        })
    return jsonify({'servers': server_list})

@app.route('/api/servers', methods=['POST'])
def register_server():
    """Register a new game server - simulates LGSL polling a server's /info endpoint"""
    global server_id_counter
    
    try:
        if request.is_json:
            data = request.get_json()
        else:
            # Accept form data or raw JSON string
            data = json.loads(request.data) if request.data else {}
    except:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    if not data:
        return jsonify({'error': 'No server data provided'}), 400
    
    # Store the server info - THIS IS THE VULNERABLE PART
    # Server data (especially extra fields) is stored without sanitization
    # just like LGSL stored data from game servers' /info endpoints
    server_id = server_id_counter
    server_id_counter += 1
    
    game_servers[server_id] = {
        'name': data.get('name', 'Unnamed Server'),
        'ip': data.get('ip', '127.0.0.1'),
        'port': data.get('port', 27015),
        'map': data.get('map', 'unknown'),
        'players': data.get('players', 0),
        'maxplayers': data.get('maxplayers', 32),
        'game': data.get('game', 'Unknown Game'),
        # Extra fields from server info - these are the attack vector
        # In LGSL, these came from $server['e'] (extra server fields)
        'extra': data.get('extra', {})
    }
    
    return jsonify({'success': True, 'server_id': server_id, 'message': 'Server registered successfully'})

def check_xss(page, flag, payload, tag):
    """Check if XSS payload executed successfully using PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Result:")
        print(result)

    finally:
        os.unlink(fn)

    return result

@app.route('/server/<int:server_id>')
def server_details(server_id):
    """Display server details - VULNERABLE TO STORED XSS
    
    This mimics lgsl_details.php which displays server info without proper escaping.
    The extra fields from server registration are rendered directly into HTML,
    allowing stored XSS attacks.
    """
    if server_id not in game_servers:
        return SERVER_NOT_FOUND_CONTENT, 404
    
    server = game_servers[server_id]
    
    # Build the extra fields table - THIS IS WHERE THE XSS VULNERABILITY IS
    # Just like in LGSL's lgsl_details.php, we're using html_entity_decode()
    # which reverses HTML entity encoding, allowing XSS
    extra_rows = ""
    for field, value in server.get('extra', {}).items():
        # Vulnerable: value is inserted directly without proper escaping
        # This mimics the LGSL vulnerability where html_entity_decode was used
        # instead of htmlentities
        extra_rows += "\n    <tr><td class='field-name'> {0} </td><td class='field-value'> {1} </td></tr>".format(
            cgi.escape(str(field)),  # Field name is escaped
            str(value)  # Value is NOT escaped - VULNERABLE!
        )
    
    # Build the page content
    page_content = SERVER_DETAILS_CONTENT.format(
        server_id=server_id,
        server_name=cgi.escape(server.get('name', 'Unknown')),
        server_ip=cgi.escape(server.get('ip', '0.0.0.0')),
        server_port=server.get('port', 27015),
        server_map=cgi.escape(server.get('map', 'unknown')),
        server_players=server.get('players', 0),
        server_maxplayers=server.get('maxplayers', 32),
        server_game=cgi.escape(server.get('game', 'Unknown')),
        extra_fields=extra_rows
    )
    
    # Check for XSS execution
    result = check_xss(page_content, flags[0], str(server.get('extra', {})), 'xss_hard')
    
    # Determine the message to display
    if result == 'XSS':
        status_msg = '<div class="alert alert-success"><strong>Challenge Complete!</strong><br>Flag: {0}</div>'.format(flags[0])
    elif result:
        status_msg = '<div class="alert alert-info">Detected alert: {0}</div>'.format(cgi.escape(result))
    else:
        status_msg = ''
    
    # Rebuild page with status message
    final_content = SERVER_DETAILS_CONTENT_WITH_STATUS.format(
        server_id=server_id,
        server_name=cgi.escape(server.get('name', 'Unknown')),
        server_ip=cgi.escape(server.get('ip', '0.0.0.0')),
        server_port=server.get('port', 27015),
        server_map=cgi.escape(server.get('map', 'unknown')),
        server_players=server.get('players', 0),
        server_maxplayers=server.get('maxplayers', 32),
        server_game=cgi.escape(server.get('game', 'Unknown')),
        extra_fields=extra_rows,
        status_message=status_msg
    )
    
    response = make_response(final_content)
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/servers')
def servers_page():
    """HTML page showing all registered servers"""
    server_rows = ""
    for sid, server in game_servers.items():
        server_rows += """
        <tr>
            <td>{0}</td>
            <td><a href="/server/{0}">{1}</a></td>
            <td>{2}:{3}</td>
            <td>{4}</td>
            <td>{5}/{6}</td>
        </tr>
        """.format(
            sid,
            cgi.escape(server.get('name', 'Unknown')),
            cgi.escape(server.get('ip', '0.0.0.0')),
            server.get('port', 27015),
            cgi.escape(server.get('game', 'Unknown')),
            server.get('players', 0),
            server.get('maxplayers', 32)
        )
    
    return SERVER_LIST_CONTENT.format(server_rows=server_rows if server_rows else "<tr><td colspan='5'>No servers registered yet</td></tr>")

if __name__ == '__main__':
    app.run(debug=True)
