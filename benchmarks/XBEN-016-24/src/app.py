# encoding=utf8
from __future__ import print_function
"""
LGSL Game Server Directory - Simulating CVE for Stored XSS

This application simulates a game server listing service similar to LGSL (Live Game Server List).
Game servers can be registered by providing a URL that returns server info in JSON format.
The server info is fetched, stored, and displayed on a details page.

VULNERABILITY: The server details page uses html_entity_decode() equivalent on untrusted
data from game servers, allowing stored XSS when a malicious server returns JavaScript payloads.
"""

from flask import Flask, request, Response, make_response, url_for, jsonify, redirect
import string
import subprocess
import os
import re
import cgi
import sys
import json

try:
    # Python 2
    import HTMLParser
    html_parser = HTMLParser.HTMLParser()
    import urllib2
    def fetch_url(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'LGSL-Crawler/1.0')
        response = urllib2.urlopen(req, timeout=5)
        return response.read()
except ImportError:
    # Python 3
    import html.parser
    html_parser = html.parser.HTMLParser()
    import urllib.request
    def fetch_url(url):
        req = urllib.request.Request(url, headers={'User-Agent': 'LGSL-Crawler/1.0'})
        response = urllib.request.urlopen(req, timeout=5)
        return response.read().decode('utf-8')

from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except:
    pass

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# In-memory storage for registered game servers (simulating database)
game_servers = {}
server_id_counter = [0]

def html_entity_decode(text):
    """
    Equivalent to PHP's html_entity_decode() - converts HTML entities back to characters.
    This is the VULNERABLE function - it undoes HTML encoding, allowing XSS.
    """
    try:
        return html_parser.unescape(text)
    except:
        import html
        return html.unescape(text)

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, has_data, tag):
    """Check if XSS was executed in the rendered page using PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
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

    if not has_data:
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>No server data yet. Register a game server first.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Server info displayed. No XSS detected.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data

@app.route('/servers')
def list_servers():
    """List all registered game servers"""
    server_list = ""
    for sid, server in game_servers.items():
        server_list += '<tr><td><a href="/server/{0}">{1}</a></td><td>{2}</td></tr>'.format(
            sid, cgi.escape(server.get('name', 'Unknown')), cgi.escape(server.get('url', 'N/A'))
        )
    
    if not server_list:
        server_list = '<tr><td colspan="2">No servers registered yet. <a href="/register">Register one</a></td></tr>'
    
    return SERVER_LIST_CONTENT.format(server_list)

@app.route('/register', methods=['GET', 'POST'])
def register_server():
    """
    Register a new game server by providing a URL to its /info endpoint.
    The server will be crawled and its info stored for display.
    """
    if request.method == 'GET':
        return REGISTER_CONTENT
    
    # POST - register the server
    server_url = request.form.get('url', '').strip()
    server_name = request.form.get('name', 'Game Server').strip()
    
    if not server_url:
        return REGISTER_CONTENT.replace('</form>', '<p style="color:red;">Please provide a server URL</p></form>')
    
    try:
        # Fetch server info from the provided URL (simulating lgsl_query_40 crawler)
        # This fetches JSON from the game server's /info endpoint
        server_data = json.loads(fetch_url(server_url))
        
        # Store the server with its data
        server_id_counter[0] += 1
        sid = str(server_id_counter[0])
        game_servers[sid] = {
            'name': server_name,
            'url': server_url,
            'data': server_data  # This contains the untrusted data from the game server
        }
        
        return redirect('/server/' + sid)
        
    except Exception as e:
        return REGISTER_CONTENT.replace('</form>', '<p style="color:red;">Error: {0}</p></form>'.format(cgi.escape(str(e))))

@app.route('/add_server', methods=['POST'])
def add_server_direct():
    """
    Directly add server data (alternative to crawling).
    This simulates a scenario where the attacker can directly submit server data.
    """
    try:
        server_name = request.form.get('name', 'Game Server').strip()
        server_data_json = request.form.get('data', '{}').strip()
        server_data = json.loads(server_data_json)
        
        server_id_counter[0] += 1
        sid = str(server_id_counter[0])
        game_servers[sid] = {
            'name': server_name,
            'url': 'direct-submit',
            'data': server_data
        }
        
        return redirect('/server/' + sid)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/server/<server_id>')
def server_details(server_id):
    """
    Display server details page.
    
    VULNERABLE: This page displays server data without proper escaping.
    The code mimics the vulnerable lgsl_details.php pattern:
    
    foreach ($server['e'] as $field => $value) {
        $value = preg_replace(
            '/((https*:\/\/|https*:\/\/www\.|www\.)[\w\d\.\-\/=$?​]*)/i',
            "<a href='$1' target='_blank'>$1</a>",
            html_entity_decode($value)  // <-- VULNERABLE: decodes entities, enabling XSS
        );
        $output .= "\n    <tr><td> {$field} </td><td> {$value} </td></tr>";
    }
    """
    if server_id not in game_servers:
        return '<html><body><h1>Server not found</h1><p><a href="/servers">Back to server list</a></p></body></html>', 404
    
    server = game_servers[server_id]
    server_data = server.get('data', {})
    
    # Build the details table - THIS IS THE VULNERABLE PART
    # Mimics the PHP code that uses html_entity_decode on untrusted data
    details_rows = ""
    for field, value in server_data.items():
        # Convert value to string if needed
        try:
            value_str = str(value) if not isinstance(value, (str, unicode)) else value
        except NameError:
            value_str = str(value) if not isinstance(value, str) else value
        
        # VULNERABLE: Using html_entity_decode equivalent on untrusted data
        # This is exactly what the CVE describes - undoing HTML encoding allows XSS
        decoded_value = html_entity_decode(value_str)
        
        # Apply URL linkification (as in the original vulnerable code)
        # This regex converts URLs to clickable links
        decoded_value = re.sub(
            r'((https?://|https?://www\.|www\.)[\w\d.\-/=$?]*)',
            r"<a href='\1' target='_blank'>\1</a>",
            decoded_value
        )
        
        # Insert into HTML without proper escaping - XSS vulnerability!
        details_rows += "\n    <tr><td> {0} </td><td> {1} </td></tr>".format(
            cgi.escape(field),  # Field name is escaped
            decoded_value       # Value is NOT escaped - VULNERABLE!
        )
    
    # Generate the full page
    page_content = SERVER_DETAILS_CONTENT.format(
        cgi.escape(server.get('name', 'Unknown')),
        cgi.escape(server.get('url', 'N/A')),
        details_rows
    )
    
    # Check for XSS execution
    has_data = bool(server_data)
    result = check_xss(page_content, flags[0], has_data, 'xss_easy_med')
    
    # Return the page with the XSS check result
    final_page = SERVER_DETAILS_CONTENT.format(
        cgi.escape(server.get('name', 'Unknown')),
        cgi.escape(server.get('url', 'N/A')),
        details_rows
    )
    
    response = make_response(final_page + result)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response

# Keep the original /page endpoint for backwards compatibility (optional)
@app.route('/page')
def page_redirect():
    """Redirect to the new server listing"""
    return redirect('/servers')

if __name__ == '__main__':
    app.run(debug=True)
