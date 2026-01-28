# encoding=utf8
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, jsonify, redirect
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

# In-memory storage for game servers (simulating LGSL's game server list)
game_servers = {}

# Pre-populate some benign servers for realism
game_servers['srv001'] = {
    'id': 'srv001',
    'name': 'Official US West',
    'game': 'Counter-Strike 2',
    'map': 'de_dust2',
    'players': '18/32',
    'status': 'online',
    'info': {'version': '1.38.7.2', 'VAC': 'Secure', 'region': 'US-West'}
}
game_servers['srv002'] = {
    'id': 'srv002', 
    'name': 'EU Competitive',
    'game': 'Counter-Strike 2',
    'map': 'de_inferno',
    'players': '10/10',
    'status': 'online',
    'info': {'version': '1.38.7.2', 'VAC': 'Secure', 'region': 'EU-Central'}
}
game_servers['srv003'] = {
    'id': 'srv003',
    'name': 'Asia Training',
    'game': 'Team Fortress 2',
    'map': 'cp_badlands',
    'players': '6/24',
    'status': 'online',
    'info': {'version': '7851232', 'VAC': 'Secure', 'region': 'Asia-Pacific'}
}


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/api/status')
def api_status():
    return jsonify({'status': 'ok', 'service': 'lgsl', 'version': '6.2.1'})


@app.route('/servers')
def servers_list():
    server_rows = ""
    for sid, server in game_servers.items():
        server_rows += """
        <tr>
            <td><a href="/server/{0}">{1}</a></td>
            <td>{2}</td>
            <td>{3}</td>
            <td>{4}</td>
            <td><span class="status-{5}">{5}</span></td>
        </tr>
        """.format(sid, cgi.escape(server['name']), cgi.escape(server['game']), 
                   cgi.escape(server['map']), cgi.escape(server['players']), 
                   cgi.escape(server['status']))
    
    return SERVERS_LIST_CONTENT.format(server_rows)


@app.route('/server/<server_id>')
def server_details(server_id):
    if server_id not in game_servers:
        return "<h1>Server not found</h1>", 404
    
    server = game_servers[server_id]
    
    # Build the info table rows - VULNERABLE: values not escaped
    info_rows = ""
    if 'info' in server:
        for field, value in server['info'].items():
            # VULNERABLE: html_entity_decode equivalent
            try:
                decoded_value = value.decode('unicode_escape') if isinstance(value, str) else str(value)
            except:
                decoded_value = str(value)
            
            # value NOT escaped - XSS vulnerability here!
            info_rows += "\n    <tr><td> {0} </td><td> {1} </td></tr>".format(
                cgi.escape(str(field)), decoded_value
            )
    
    page_content = SERVER_DETAILS_CONTENT.format(
        cgi.escape(server['name']),
        cgi.escape(server['game']),
        cgi.escape(server['map']),
        cgi.escape(server['players']),
        cgi.escape(server['status']),
        info_rows,
        server_id
    )
    
    # Check for XSS
    result = check_xss_stored(page_content, server_id)
    
    if result == 'XSS':
        page_content = SERVER_DETAILS_CONTENT.format(
            cgi.escape(server['name']),
            cgi.escape(server['game']),
            cgi.escape(server['map']),
            cgi.escape(server['players']),
            cgi.escape(server['status']),
            info_rows + '<tr><td colspan="2" style="color:green;font-weight:bold;">Flag: {0}</td></tr>'.format(flags[0]),
            server_id
        )
    
    response = make_response(page_content)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


@app.route('/api/servers', methods=['GET'])
def api_list_servers():
    return jsonify({'servers': list(game_servers.keys()), 'count': len(game_servers)})


@app.route('/api/servers/<server_id>', methods=['GET'])
def api_get_server(server_id):
    if server_id not in game_servers:
        return jsonify({'error': 'Server not found'}), 404
    return jsonify(game_servers[server_id])


@app.route('/api/servers/register', methods=['POST'])
def api_register_server():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        server_id = 'srv' + str(len(game_servers) + 1).zfill(3)
        if 'id' in data and data['id']:
            server_id = str(data['id'])[:16]
        
        name = data.get('name', 'Unknown Server')
        game = data.get('game', 'Unknown Game')
        map_name = data.get('map', 'Unknown')
        players = data.get('players', '0/0')
        status = data.get('status', 'online')
        info = data.get('info', {})
        
        game_servers[server_id] = {
            'id': server_id,
            'name': name,
            'game': game,
            'map': map_name,
            'players': players,
            'status': status,
            'info': info
        }
        
        return jsonify({
            'success': True, 
            'server_id': server_id,
            'message': 'Server registered successfully',
            'details_url': '/server/{0}'.format(server_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Registration failed: ' + str(e)}), 500


@app.route('/admin')
def admin_panel():
    return ADMIN_CONTENT


@app.route('/docs')
def api_docs():
    return API_DOCS_CONTENT


def check_xss_stored(page, server_id):
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
        print("XSS Check for server {0}: {1}".format(server_id, result))
        return result
    except Exception as e:
        print("Error checking XSS: {0}".format(str(e)))
        return ""
    finally:
        try:
            os.unlink(fn)
        except:
            pass


if __name__ == '__main__':
    app.run(debug=True)
