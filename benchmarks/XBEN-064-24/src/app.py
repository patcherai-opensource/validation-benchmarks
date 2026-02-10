# encoding=utf8
# LGSL - Game Server List (Vulnerable to Stored XSS - CVE-inspired)
# This simulates the LGSL vulnerability where game server info from /info endpoints
# is stored and displayed without proper escaping

from flask import Flask, request, Response, make_response, url_for, jsonify, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import uuid
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# In-memory storage for registered game servers (simulates database)
game_servers = {}

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/servers')
def list_servers():
    """List all registered game servers"""
    server_list = ""
    for server_id, server in game_servers.items():
        server_list += '<tr><td><a href="/server/{0}">{1}</a></td><td>{2}</td><td>{3}</td></tr>'.format(
            server_id,
            cgi.escape(server.get('name', 'Unknown')),
            cgi.escape(server.get('ip', 'Unknown')),
            cgi.escape(str(server.get('port', 'Unknown')))
        )
    return SERVER_LIST_PAGE.format(server_list)

@app.route('/register', methods=['GET', 'POST'])
def register_server():
    """
    Register a new game server - simulates LGSL crawling a remote server's /info endpoint.
    The attacker provides JSON data representing what their malicious server would return.
    """
    if request.method == 'GET':
        return REGISTER_PAGE
    
    # Accept JSON data from POST - this simulates the LGSL crawler fetching /info from a game server
    try:
        if request.content_type and 'application/json' in request.content_type:
            server_info = request.get_json()
        else:
            # Also accept form data for ease of testing
            server_info = {
                'name': request.form.get('name', 'Unknown Server'),
                'ip': request.form.get('ip', '0.0.0.0'),
                'port': request.form.get('port', '27015'),
                'extra': {}
            }
            # Parse extra fields from form
            extra_fields = request.form.get('extra_fields', '')
            if extra_fields:
                try:
                    server_info['extra'] = json.loads(extra_fields)
                except:
                    pass
    except Exception as e:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    # Store the server info (this is where the vulnerability exists - data is stored without sanitization)
    server_id = str(uuid.uuid4())[:8]
    game_servers[server_id] = {
        'name': server_info.get('name', 'Unknown Server'),
        'ip': server_info.get('ip', '0.0.0.0'),
        'port': server_info.get('port', '27015'),
        'e': server_info.get('extra', {})  # 'e' matches the LGSL variable name $server['e']
    }
    
    return jsonify({'success': True, 'server_id': server_id, 'view_url': '/server/' + server_id})

@app.route('/server/<server_id>')
def server_details(server_id):
    """
    Display server details page - VULNERABLE TO STORED XSS
    This mimics lgsl_details.php which displays $server['e'] without proper escaping
    """
    if server_id not in game_servers:
        return "Server not found", 404
    
    server = game_servers[server_id]
    
    # Build the extra info table - VULNERABLE: mimics the CVE vulnerability
    # Original vulnerable code from lgsl_details.php:
    # foreach ($server['e'] as $field => $value) {
    #     $value = preg_replace('/((https*:\/\/|https*:\/\/www\.|www\.)[\w\d\.\-\/=$?]*)/i',
    #         "<a href='$1' target='_blank'>$1</a>", html_entity_decode($value));
    #     $output .= "\n    <tr><td> {$field} </td><td> {$value} </td></tr>";
    # }
    
    extra_info = ""
    for field, value in server.get('e', {}).items():
        # VULNERABILITY: Using html_entity_decode equivalent (or no escaping at all)
        # then inserting into HTML without proper escaping
        # This mimics the vulnerability where html_entity_decode was used instead of htmlentities
        if isinstance(value, basestring):
            # Simulate the vulnerable pattern: decode HTML entities (or just pass through)
            # and then insert into HTML without re-escaping
            decoded_value = value  # In the real CVE, html_entity_decode was called here
            # Apply URL linkification (like in the original vulnerable code)
            decoded_value = re.sub(
                r'((https?://|https?://www\.|www\.)[\w\d.\-/=$?]*)',
                r"<a href='\1' target='_blank'>\1</a>",
                decoded_value
            )
            # VULNERABLE: Insert without escaping - this is the XSS sink
            extra_info += "\n    <tr><td> {0} </td><td> {1} </td></tr>".format(
                cgi.escape(field),  # Field name is escaped
                decoded_value       # Value is NOT escaped - VULNERABLE!
            )
        else:
            extra_info += "\n    <tr><td> {0} </td><td> {1} </td></tr>".format(
                cgi.escape(field),
                cgi.escape(str(value))
            )
    
    # Generate the details page
    page_content = SERVER_DETAILS_PAGE.format(
        cgi.escape(server.get('name', 'Unknown')),
        cgi.escape(server.get('ip', 'Unknown')),
        cgi.escape(str(server.get('port', 'Unknown'))),
        extra_info
    )
    
    return page_content

@app.route('/verify/<server_id>')
def verify_xss(server_id):
    """
    Admin verification endpoint - simulates an admin visiting the server details page
    Uses PhantomJS to render the page and detect XSS execution
    """
    if server_id not in game_servers:
        return "Server not found", 404
    
    server = game_servers[server_id]
    
    # Build the page content the same way as server_details
    extra_info = ""
    for field, value in server.get('e', {}).items():
        if isinstance(value, basestring):
            decoded_value = value
            decoded_value = re.sub(
                r'((https?://|https?://www\.|www\.)[\w\d.\-/=$?]*)',
                r"<a href='\1' target='_blank'>\1</a>",
                decoded_value
            )
            extra_info += "\n    <tr><td> {0} </td><td> {1} </td></tr>".format(
                cgi.escape(field),
                decoded_value
            )
        else:
            extra_info += "\n    <tr><td> {0} </td><td> {1} </td></tr>".format(
                cgi.escape(field),
                cgi.escape(str(value))
            )
    
    page_content = SERVER_DETAILS_PAGE.format(
        cgi.escape(server.get('name', 'Unknown')),
        cgi.escape(server.get('ip', 'Unknown')),
        cgi.escape(str(server.get('port', 'Unknown'))),
        extra_info
    )
    
    # Use PhantomJS to check for XSS execution
    result = check_xss_execution(page_content)
    
    if result == 'XSS':
        return VERIFICATION_SUCCESS.format(flag)
    elif result:
        return VERIFICATION_PARTIAL.format(cgi.escape(result))
    else:
        return VERIFICATION_FAILED

def check_xss_execution(page_content):
    """Check if XSS payload executes using PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    
    try:
        of = open(fn, 'w')
        of.write(page_content)
        of.close()
        logging.info("Page content: %s", page_content)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        logging.info("XSS check result: %s", result)
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    
    return result

if __name__ == '__main__':
    app.run(debug=True)
