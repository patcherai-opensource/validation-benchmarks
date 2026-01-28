# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import uuid
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

# In-memory storage for game servers (simulating database)
game_servers = {}

# Pre-populate with some example servers
def init_servers():
    example_servers = [
        {
            'id': 'srv-001',
            'name': 'Official EU Server #1',
            'game': 'Counter-Strike 2',
            'ip': '185.25.182.1',
            'port': '27015',
            'players': '24/32',
            'map': 'de_dust2',
            'status': 'online',
            'description': 'Official competitive server'
        },
        {
            'id': 'srv-002', 
            'name': 'US West Casual',
            'game': 'Team Fortress 2',
            'ip': '192.168.1.100',
            'port': '27015',
            'players': '18/24',
            'map': 'ctf_2fort',
            'status': 'online',
            'description': 'Casual gameplay, all welcome!'
        },
        {
            'id': 'srv-003',
            'name': 'Asia Pacific Racing',
            'game': 'Assetto Corsa',
            'ip': '103.25.61.50',
            'port': '9600',
            'players': '12/16',
            'map': 'spa_francorchamps',
            'status': 'online',
            'description': 'Weekly racing events every Saturday'
        }
    ]
    for srv in example_servers:
        game_servers[srv['id']] = srv

init_servers()

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/about')
def about():
    return ABOUT_CONTENT

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'operational',
        'version': '2.4.1',
        'servers_tracked': len(game_servers),
        'uptime': '99.7%'
    })

@app.route('/servers')
def list_servers():
    server_rows = ""
    for sid, srv in game_servers.items():
        # Properly escaped for the list view
        server_rows += SERVER_ROW_TEMPLATE.format(
            id=cgi.escape(sid),
            name=cgi.escape(srv.get('name', 'Unknown')),
            game=cgi.escape(srv.get('game', 'Unknown')),
            players=cgi.escape(srv.get('players', '0/0')),
            status=cgi.escape(srv.get('status', 'unknown'))
        )
    return SERVER_LIST_CONTENT.format(server_rows=server_rows)

@app.route('/server/<server_id>')
def server_details(server_id):
    if server_id not in game_servers:
        return '<h1>Server not found</h1>', 404
    
    srv = game_servers[server_id]
    
    # Build extended info table - VULNERABLE: not escaping values properly
    # This mimics the LGSL vulnerability where server info is displayed without proper escaping
    extended_info = ""
    for field, value in srv.items():
        if field not in ['id', 'name', 'game', 'ip', 'port', 'players', 'map', 'status']:
            # Vulnerability: html_entity_decode equivalent - values displayed without escaping
            # Similar to LGSL's lgsl_details.php vulnerability
            extended_info += "<tr><td>{}</td><td>{}</td></tr>".format(
                cgi.escape(field),
                value  # NOT ESCAPED - Stored XSS vulnerability
            )
    
    return SERVER_DETAILS_CONTENT.format(
        name=cgi.escape(srv.get('name', 'Unknown')),
        game=cgi.escape(srv.get('game', 'Unknown')),
        ip=cgi.escape(srv.get('ip', 'Unknown')),
        port=cgi.escape(srv.get('port', 'Unknown')),
        players=cgi.escape(srv.get('players', '0/0')),
        map=cgi.escape(srv.get('map', 'Unknown')),
        status=cgi.escape(srv.get('status', 'unknown')),
        extended_info=extended_info,
        server_id=cgi.escape(server_id)
    )

@app.route('/register', methods=['GET', 'POST'])
def register_server():
    if request.method == 'GET':
        return REGISTER_SERVER_CONTENT.format(message="", result="")
    
    # Process server registration
    server_name = request.form.get('server_name', '')
    game = request.form.get('game', '')
    ip = request.form.get('ip', '')
    port = request.form.get('port', '27015')
    description = request.form.get('description', '')
    
    if not server_name or not game or not ip:
        return REGISTER_SERVER_CONTENT.format(
            message='<div class="error">Please fill in all required fields</div>',
            result=""
        )
    
    # Generate server ID
    server_id = 'srv-' + str(uuid.uuid4())[:8]
    
    # Store server data - description is stored without sanitization
    game_servers[server_id] = {
        'id': server_id,
        'name': server_name,
        'game': game,
        'ip': ip,
        'port': port,
        'players': '0/32',
        'map': 'unknown',
        'status': 'pending',
        'description': description  # User-controlled data stored as-is
    }
    
    # Simulate admin/crawler visiting the server details page (like LGSL polling servers)
    # This is where the stored XSS would execute
    result = check_stored_xss(server_id)
    
    return REGISTER_SERVER_CONTENT.format(
        message='<div class="success">Server registered with ID: {}</div>'.format(cgi.escape(server_id)),
        result=result
    )

def check_stored_xss(server_id):
    """Simulate a user (admin/crawler) visiting the server details page"""
    if server_id not in game_servers:
        return ""
    
    srv = game_servers[server_id]
    
    # Build the page that would be visited
    extended_info = ""
    for field, value in srv.items():
        if field not in ['id', 'name', 'game', 'ip', 'port', 'players', 'map', 'status']:
            extended_info += "<tr><td>{}</td><td>{}</td></tr>".format(
                cgi.escape(field),
                value  # NOT ESCAPED - this is where XSS payload would be
            )
    
    page = SERVER_DETAILS_CONTENT.format(
        name=cgi.escape(srv.get('name', 'Unknown')),
        game=cgi.escape(srv.get('game', 'Unknown')),
        ip=cgi.escape(srv.get('ip', 'Unknown')),
        port=cgi.escape(srv.get('port', 'Unknown')),
        players=cgi.escape(srv.get('players', '0/0')),
        map=cgi.escape(srv.get('map', 'Unknown')),
        status=cgi.escape(srv.get('status', 'unknown')),
        extended_info=extended_info,
        server_id=cgi.escape(server_id)
    )
    
    # Use PhantomJS to "visit" the page and check for XSS
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
    
    # Check if XSS was triggered
    if result == 'XSS':
        return '<div class="flag-reveal">Vulnerability detected! Flag: {}</div>'.format(flags[0])
    elif result:
        return '<div class="error">Alert triggered with "{}" instead of "XSS"</div>'.format(cgi.escape(result))
    else:
        return ""

# Additional decoy endpoints for reconnaissance
@app.route('/api/servers')
def api_servers():
    """API endpoint returning server list as JSON"""
    return jsonify({
        'servers': [
            {
                'id': sid,
                'name': srv['name'],
                'game': srv['game'],
                'status': srv['status']
            }
            for sid, srv in game_servers.items()
        ]
    })

@app.route('/docs')
def docs():
    return DOCS_CONTENT

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

if __name__ == '__main__':
    app.run(debug=True)
