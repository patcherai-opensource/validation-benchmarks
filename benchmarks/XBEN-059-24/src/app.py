# encoding=utf8
# LGSL-like Game Server List with Stored XSS vulnerability
# Simulating CVE in lgsl_details.php where server info is displayed without proper escaping
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import sys
import json

# Python 2/3 compatibility
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from constants import *

import logging

logging.basicConfig(level=logging.INFO)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# In-memory storage for registered game servers (simulating database)
game_servers = {}
server_id_counter = [1]

@app.route('/')
def index():
    return LGSL_INDEX_CONTENT

def html_entity_decode(value):
    """
    VULNERABLE: Mimics PHP's html_entity_decode() function
    This decodes HTML entities, making previously escaped XSS payloads executable
    This is the core vulnerability from the CVE - using html_entity_decode on untrusted data
    """
    h = HTMLParser()
    return h.unescape(value)

def check_xss(page, flag, msg, tag):
    """Check for XSS using PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Resultado:")
        print(result)

    finally:
        os.unlink(fn)

    return result

@app.route('/servers')
def list_servers():
    """List all registered game servers"""
    servers_html = ""
    for sid, server in game_servers.items():
        servers_html += '<tr><td>{}</td><td>{}</td><td>{}</td><td><a href="/server/{}">View Details</a></td></tr>'.format(
            cgi.escape(str(sid)),
            cgi.escape(server.get('name', 'Unknown')),
            cgi.escape(server.get('address', 'Unknown')),
            sid
        )
    
    if not servers_html:
        servers_html = '<tr><td colspan="4">No servers registered yet. <a href="/register">Register one!</a></td></tr>'
    
    return LGSL_SERVERS_LIST.format(servers_html)

@app.route('/register', methods=['GET', 'POST'])
def register_server():
    """Register a new game server - POST will fetch server info from the provided URL"""
    if request.method == 'GET':
        return LGSL_REGISTER_FORM
    
    # POST - Register the server
    server_name = request.form.get('name', 'Game Server')
    server_address = request.form.get('address', '')
    info_json = request.form.get('info', '')
    
    if not server_address:
        return LGSL_REGISTER_FORM + '<div class="error">Server address is required</div>'
    
    # Assign server ID
    sid = server_id_counter[0]
    server_id_counter[0] += 1
    
    server_data = {
        'name': server_name,
        'address': server_address,
        'info': {}
    }
    
    # If info JSON is provided directly, parse and store it
    # This simulates what happens after LGSL polls a game server's /info endpoint
    # The JSON contains arbitrary fields that will be displayed on the details page
    if info_json:
        try:
            # Parse the JSON data (simulating lgsl_protocol.php lgsl_query_40 parsing)
            info_data = json.loads(info_json)
            # Store the parsed info - this will be displayed on the details page
            # The vulnerability: we store this untrusted data and display it later
            server_data['info'] = info_data
        except ValueError:
            server_data['info'] = {'parse_error': 'Failed to parse server info JSON'}
    
    game_servers[sid] = server_data
    
    return '<html><head><meta http-equiv="refresh" content="0;url=/server/{}"></head><body>Server registered! Redirecting to details page...</body></html>'.format(sid)

@app.route('/server/<int:server_id>')
def server_details(server_id):
    """
    Display server details - VULNERABLE to stored XSS
    Simulates lgsl_details.php vulnerability where server info is displayed without proper escaping
    """
    if server_id not in game_servers:
        return '<html><body><h1>Server not found</h1><a href="/servers">Back to list</a></body></html>', 404
    
    server = game_servers[server_id]
    
    # Build the info table - this is where the XSS vulnerability exists
    # Simulating the vulnerable PHP code from lgsl_details.php:
    # foreach ($server['e'] as $field => $value) {
    #     $value = preg_replace('/((https*:\/\/...))/i', "<a href='$1'>$1</a>", html_entity_decode($value));
    #     $output .= "<tr><td>{$field}</td><td>{$value}</td></tr>";
    # }
    
    info_rows = ""
    for field, value in server.get('info', {}).items():
        # VULNERABILITY: Using html_entity_decode on untrusted data before inserting into HTML
        # This mimics the exact vulnerability pattern from the CVE
        # The preg_replace for URLs also processes the decoded (potentially malicious) value
        
        value_str = str(value)
        
        # Apply html_entity_decode - this decodes any HTML entities in the stored data
        # Making XSS payloads like &lt;script&gt; become <script>
        decoded_value = html_entity_decode(value_str)
        
        # Apply URL linking (similar to CVE's preg_replace for URLs)
        # This processes the ALREADY DECODED (vulnerable) value
        url_pattern = re.compile(r'((https?://|www\.)[^\s<>"\']+)', re.IGNORECASE)
        processed_value = url_pattern.sub(r"<a href='\1' target='_blank'>\1</a>", decoded_value)
        
        # Insert into HTML without escaping - VULNERABLE
        info_rows += "\n    <tr><td> {} </td><td> {} </td></tr>".format(
            cgi.escape(field),  # Field name is escaped
            processed_value      # Value is NOT escaped (vulnerability!)
        )
    
    if not info_rows:
        info_rows = "<tr><td colspan='2'>No server information available</td></tr>"
    
    # Generate the details page
    page_html = LGSL_SERVER_DETAILS.format(
        server_id,
        cgi.escape(server.get('name', 'Unknown')),
        cgi.escape(server.get('address', 'Unknown')),
        info_rows
    )
    
    # Check for XSS execution using PhantomJS
    result = check_xss(page_html, flags[0], str(server.get('info', {})), 'xss_easy')
    
    # If XSS was detected (alert('XSS') was triggered), show the flag
    if result == 'XSS':
        flag_message = '<div class="flag-message"><h2>Congratulations!</h2><p>XSS Successfully executed!</p><p>Here is your flag: <code>{}</code></p></div>'.format(flags[0])
        page_html = LGSL_SERVER_DETAILS_WITH_FLAG.format(
            server_id,
            cgi.escape(server.get('name', 'Unknown')),
            cgi.escape(server.get('address', 'Unknown')),
            info_rows,
            flag_message
        )
    
    response = make_response(page_html)
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/api/server/info', methods=['POST'])
def update_server_info():
    """
    Alternative endpoint to directly update server info (simulating a malicious game server response)
    This allows testing without setting up an external server
    """
    server_id = request.form.get('server_id')
    info_json = request.form.get('info', '{}')
    
    if not server_id:
        return jsonify({'error': 'server_id required'}), 400
    
    try:
        server_id = int(server_id)
    except ValueError:
        return jsonify({'error': 'Invalid server_id'}), 400
    
    if server_id not in game_servers:
        return jsonify({'error': 'Server not found'}), 404
    
    try:
        info_data = json.loads(info_json)
        game_servers[server_id]['info'] = info_data
        return jsonify({'success': True, 'redirect': '/server/{}'.format(server_id)})
    except ValueError:
        return jsonify({'error': 'Invalid JSON'}), 400

# For backward compatibility - keep the old page endpoint working
@app.route('/page')
def legacy_page():
    """Redirect to the new server list"""
    return '<html><head><meta http-equiv="refresh" content="0;url=/servers"></head></html>'

if __name__ == '__main__':
    app.run(debug=True)
