# encoding=utf8
# Game Server Listing System (GSLS) - Server monitoring dashboard
# Inspired by LGSL game server listing software

from flask import Flask, request, Response, make_response, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json as jsonlib
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

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, has_content, tag):
    """Check if page contains XSS payload execution"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host/port, fallback to localhost:5000 for local dev
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print "Page:"
        print page
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "Result:"
        print result

    finally:
        os.unlink(fn)

    if not has_content:
        return None, None
    else:
        if result == 'XSS':
            return True, flag
        elif result:
            return False, result
        else:
            return False, None


@app.route('/api/servers', methods=['GET'])
def list_servers():
    """List all registered game servers"""
    server_list = []
    for server_id, data in game_servers.items():
        server_list.append({
            'id': server_id,
            'name': data.get('name', 'Unknown'),
            'game': data.get('game', 'Unknown'),
            'address': data.get('address', 'Unknown')
        })
    return jsonify({'servers': server_list, 'count': len(server_list)})


@app.route('/api/servers/register', methods=['POST'])
def register_server():
    """Register a new game server - simulates LGSL crawling a server's /info endpoint"""
    try:
        # Accept JSON data from "game server" (attacker-controlled source)
        # This simulates lgsl_query_40 in lgsl_protocol.php ingesting untrusted fields
        if request.is_json:
            server_data = request.get_json()
        else:
            server_data = request.form.to_dict()
        
        if not server_data:
            return jsonify({'error': 'No server data provided'}), 400
        
        # Generate server ID
        server_id = len(game_servers) + 1
        
        # Store all fields from the server (simulating untrusted data ingestion)
        # The vulnerability: we store data without sanitization
        game_servers[server_id] = {
            'name': server_data.get('name', 'Game Server'),
            'game': server_data.get('game', 'Unknown'),
            'address': server_data.get('address', '0.0.0.0:27015'),
            'players': server_data.get('players', '0/32'),
            'map': server_data.get('map', 'unknown'),
            'extra': server_data.get('extra', {})  # Extra fields like LGSL's $server['e']
        }
        
        return jsonify({
            'success': True, 
            'message': 'Server registered successfully',
            'server_id': server_id,
            'view_url': '/server/{}'.format(server_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Invalid request: {}'.format(str(e))}), 400


@app.route('/server/<int:server_id>')
def server_details(server_id):
    """Display server details page - vulnerable to stored XSS
    
    This simulates lgsl_details.php which displays server info without proper escaping.
    The vulnerability mirrors:
        foreach ($server['e'] as $field => $value) {
            $value = preg_replace(..., html_entity_decode($value));
            $output .= "\n    <tr><td> {$field} </td><td> {$value} </td></tr>";
        }
    """
    if server_id not in game_servers:
        return SERVER_NOT_FOUND_CONTENT, 404
    
    server = game_servers[server_id]
    
    # Build the extra fields table (vulnerable - no escaping, like LGSL)
    extra_rows = ""
    extra_data = server.get('extra', {})
    if isinstance(extra_data, dict):
        for field, value in extra_data.items():
            # VULNERABILITY: html_entity_decode equivalent - data rendered without escaping
            # Just like LGSL's lgsl_details.php
            extra_rows += '<tr><td class="field-name">{}</td><td class="field-value">{}</td></tr>\n'.format(field, value)
    
    # Build the page content
    page_content = SERVER_DETAILS_CONTENT.format(
        server_id=server_id,
        name=server.get('name', 'Unknown'),
        game=server.get('game', 'Unknown'),
        address=server.get('address', 'Unknown'),
        players=server.get('players', '0/0'),
        map=server.get('map', 'unknown'),
        extra_rows=extra_rows
    )
    
    # Check for XSS execution 
    has_content = bool(extra_rows)
    xss_success, result = check_xss(page_content, flags[0], has_content, 'xss_easy')
    
    if xss_success:
        # XSS detected - return flag
        flag_content = '<div class="flag-banner">Security Check Result: XSS Detected!<br>Admin Token: {}</div>'.format(result)
        page_with_flag = SERVER_DETAILS_CONTENT.format(
            server_id=server_id,
            name=server.get('name', 'Unknown'),
            game=server.get('game', 'Unknown'),
            address=server.get('address', 'Unknown'),
            players=server.get('players', '0/0'),
            map=server.get('map', 'unknown'),
            extra_rows=extra_rows + '<tr><td colspan="2">' + flag_content + '</td></tr>'
        )
        response = make_response(page_with_flag)
    else:
        response = make_response(page_content)
    
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/admin/reset', methods=['POST'])
def reset_servers():
    """Admin endpoint to clear all servers (for testing)"""
    global game_servers
    game_servers = {}
    return jsonify({'success': True, 'message': 'All servers cleared'})


if __name__ == '__main__':
    app.run(debug=True)
