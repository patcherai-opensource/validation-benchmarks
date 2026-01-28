# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, jsonify, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import urllib2
import sys
import json
import time
import hashlib
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# In-memory storage for game servers (simulates a database)
game_servers = {}

# Sample pre-populated servers for realism
game_servers['server_001'] = {
    'id': 'server_001',
    'name': 'Official EU Server',
    'game': 'Counter-Strike 2',
    'address': '192.168.1.100:27015',
    'players': '24/32',
    'map': 'de_dust2',
    'info_url': None,
    'extra_info': {
        'version': '1.38.7.9',
        'VAC_Secured': 'Yes',
        'Server_Type': 'Dedicated'
    },
    'last_updated': '2024-01-15 14:32:00'
}

game_servers['server_002'] = {
    'id': 'server_002', 
    'name': 'US West Gaming',
    'game': 'Team Fortress 2',
    'address': '10.0.0.55:27015',
    'players': '18/24',
    'map': 'ctf_2fort',
    'info_url': None,
    'extra_info': {
        'version': '8.1.2.3',
        'VAC_Secured': 'Yes',
        'Pure_Server': 'Enabled'
    },
    'last_updated': '2024-01-15 12:15:00'
}

game_servers['server_003'] = {
    'id': 'server_003',
    'name': 'Asia Pacific Hub',
    'game': 'Minecraft',
    'address': '172.16.0.200:25565', 
    'players': '45/100',
    'map': 'survival_world',
    'info_url': None,
    'extra_info': {
        'version': '1.20.4',
        'Whitelist': 'Disabled',
        'GameMode': 'Survival'
    },
    'last_updated': '2024-01-15 08:45:00'
}

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/about')
def about():
    return ABOUT_CONTENT

@app.route('/api/status')
def api_status():
    """API health check endpoint"""
    return jsonify({
        'status': 'online',
        'version': '2.1.4',
        'servers_tracked': len(game_servers),
        'uptime': '99.97%'
    })

@app.route('/servers')
def server_list():
    """List all monitored game servers"""
    server_rows = ""
    for sid, server in game_servers.items():
        server_rows += """
        <tr>
            <td><a href="/server/{0}">{1}</a></td>
            <td>{2}</td>
            <td>{3}</td>
            <td>{4}</td>
            <td>{5}</td>
        </tr>
        """.format(sid, cgi.escape(server['name']), cgi.escape(server['game']), 
                   cgi.escape(server['address']), cgi.escape(server['players']), 
                   cgi.escape(server['map']))
    
    return SERVER_LIST_CONTENT.format(server_rows)

@app.route('/server/<server_id>')
def server_details(server_id):
    """View detailed information for a specific server"""
    if server_id not in game_servers:
        return ERROR_CONTENT.format("Server not found", "The requested server ID does not exist in our database."), 404
    
    server = game_servers[server_id]
    
    # Build extra info table - VULNERABLE: Displays stored data without escaping
    # This mimics the lgsl vulnerability where html_entity_decode is used 
    # instead of htmlentities, allowing stored XSS
    extra_info_rows = ""
    if server.get('extra_info'):
        for field, value in server['extra_info'].items():
            # VULNERABLE: Uses html_entity_decode equivalent - allows XSS
            # The value is directly inserted without proper escaping
            # This mirrors: $value = html_entity_decode($value); from lgsl
            try:
                decoded_value = value.decode('unicode_escape') if isinstance(value, str) else str(value)
            except:
                decoded_value = str(value)
            extra_info_rows += """
            <tr><td class="info-label">{0}</td><td class="info-value">{1}</td></tr>
            """.format(cgi.escape(str(field)), decoded_value)  # Note: value NOT escaped!
    
    details_html = SERVER_DETAILS_CONTENT.format(
        cgi.escape(server['name']),
        cgi.escape(server['game']),
        cgi.escape(server['address']),
        cgi.escape(server['players']),
        cgi.escape(server['map']),
        server.get('last_updated', 'Unknown'),
        extra_info_rows,
        server_id
    )
    
    # Check for XSS execution (the flag reward mechanism)
    result = check_xss_in_page(details_html, server_id)
    
    response = make_response(details_html + result)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response

def check_xss_in_page(page, server_id):
    """Check if XSS payload executes and return flag if successful"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
    
    result_html = ""
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        
        if result == 'XSS':
            result_html = '<div class="alert alert-success"><strong>Security Alert Triggered!</strong><br>XSS detected. Debug token: {0}</div>'.format(flags[0])
        elif result:
            result_html = '<div class="alert alert-warning">Unexpected script output: {0}</div>'.format(cgi.escape(result))
    except Exception as e:
        logging.error("XSS check error: %s", str(e))
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    
    return result_html

@app.route('/admin/register', methods=['GET', 'POST'])
def register_server():
    """Register a new game server to monitor"""
    if request.method == 'GET':
        return REGISTER_CONTENT
    
    # Handle server registration
    server_name = request.form.get('name', 'Unnamed Server')
    game_type = request.form.get('game', 'Unknown')
    address = request.form.get('address', '0.0.0.0:0')
    info_url = request.form.get('info_url', '')
    extra_data = request.form.get('extra_data', '')  # JSON string for extended info
    
    # Generate server ID
    server_id = 'srv_' + hashlib.md5(str(time.time()) + server_name).hexdigest()[:8]
    
    # Create new server entry
    new_server = {
        'id': server_id,
        'name': server_name[:50],  # Basic length limit
        'game': game_type[:30],
        'address': address[:50],
        'players': '0/0',
        'map': 'unknown',
        'info_url': info_url if info_url else None,
        'extra_info': {},
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Parse extra_data if provided (allows direct JSON injection for extended info)
    # VULNERABLE: Trusts user-provided JSON data which will be displayed without sanitization
    if extra_data:
        try:
            parsed_extra = json.loads(extra_data)
            if isinstance(parsed_extra, dict):
                new_server['extra_info'] = parsed_extra
                if 'players' in parsed_extra:
                    new_server['players'] = str(parsed_extra.pop('players'))
                if 'map' in parsed_extra:
                    new_server['map'] = str(parsed_extra.pop('map'))
        except:
            pass  # Silently ignore invalid JSON
    
    # If info_url provided, fetch additional data from it
    # This simulates lgsl_query_40 fetching data from game servers
    if info_url and not extra_data:
        try:
            fetched_data = fetch_server_info(info_url)
            if fetched_data:
                new_server['extra_info'] = fetched_data
                if 'players' in fetched_data:
                    new_server['players'] = str(fetched_data.pop('players'))
                if 'map' in fetched_data:
                    new_server['map'] = str(fetched_data.pop('map'))
        except Exception as e:
            logging.warning("Failed to fetch info from %s: %s", info_url, str(e))
    
    game_servers[server_id] = new_server
    
    return redirect('/server/' + server_id)

def fetch_server_info(url):
    """
    Fetch server info from external URL (simulates lgsl_query_40)
    VULNERABLE: Trusts data from external source
    """
    try:
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            return None
        
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'LGSL-Monitor/2.1.4')
        response = urllib2.urlopen(req, timeout=5)
        data = response.read()
        
        # Parse JSON response (mimics lgsl protocol parsing)
        parsed = json.loads(data)
        
        # Return the parsed data - this will be stored and displayed
        # VULNERABLE: No sanitization of the fetched values
        if isinstance(parsed, dict):
            return parsed
        return None
    except Exception as e:
        logging.error("Fetch error: %s", str(e))
        return None

@app.route('/admin/refresh/<server_id>', methods=['POST'])
def refresh_server(server_id):
    """Refresh server info by re-fetching from info_url"""
    if server_id not in game_servers:
        return jsonify({'error': 'Server not found'}), 404
    
    server = game_servers[server_id]
    if not server.get('info_url'):
        return jsonify({'error': 'No info URL configured for this server'}), 400
    
    try:
        fetched_data = fetch_server_info(server['info_url'])
        if fetched_data:
            server['extra_info'] = fetched_data
            server['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
            return jsonify({'success': True, 'message': 'Server info updated'})
    except:
        pass
    
    return jsonify({'error': 'Failed to fetch server info'}), 500

@app.route('/api/servers')
def api_servers():
    """JSON API endpoint for server list"""
    servers = []
    for sid, s in game_servers.items():
        servers.append({
            'id': sid,
            'name': s['name'],
            'game': s['game'],
            'players': s['players']
        })
    return jsonify({'servers': servers})

@app.route('/docs')
def docs():
    """API documentation page"""
    return DOCS_CONTENT

@app.route('/search')
def search():
    """Search servers - non-vulnerable endpoint for noise"""
    query = request.args.get('q', '')
    results = []
    for sid, server in game_servers.items():
        if query.lower() in server['name'].lower() or query.lower() in server['game'].lower():
            results.append(server)
    return SEARCH_RESULTS_CONTENT.format(cgi.escape(query), len(results))

if __name__ == '__main__':
    app.run(debug=True)
