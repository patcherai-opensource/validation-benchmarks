# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import urllib2
import json
import sys
import HTMLParser
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# In-memory storage for registered game servers
game_servers = {}
server_counter = [0]  # Using list to allow mutation in nested function

html_parser = HTMLParser.HTMLParser()

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag):
    """Check if XSS payload executed using PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        logging.info("Page: %s", page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        logging.info("Result: %s", result)

    finally:
        try:
            os.unlink(fn)
        except:
            pass

    return result

@app.route('/servers')
def list_servers():
    """List all registered game servers"""
    server_list = ""
    for sid, server in game_servers.items():
        server_list += '<tr><td><a href="/server/{0}">{1}</a></td><td>{2}</td></tr>'.format(
            sid, cgi.escape(server.get('name', 'Unknown')), cgi.escape(server.get('address', 'Unknown'))
        )
    
    if not server_list:
        server_list = '<tr><td colspan="2">No servers registered yet</td></tr>'
    
    return SERVERS_LIST_CONTENT.format(server_list)

@app.route('/register', methods=['GET', 'POST'])
def register_server():
    """Register a new game server by providing its info URL"""
    if request.method == 'GET':
        return REGISTER_CONTENT
    
    # POST request - register the server
    server_url = request.form.get('url', '')
    
    if not server_url:
        return REGISTER_ERROR_CONTENT.format("Please provide a server URL")
    
    try:
        # Fetch server info from the provided URL (simulating lgsl_query_40)
        # This is the crawler that fetches untrusted data from game servers
        req = urllib2.Request(server_url, headers={'User-Agent': 'LGSL Crawler/1.0'})
        response = urllib2.urlopen(req, timeout=5)
        server_data = json.loads(response.read())
        
        # Store the server info
        server_counter[0] += 1
        sid = str(server_counter[0])
        
        # Store server data including the extended info 'e' field
        game_servers[sid] = {
            'name': server_data.get('name', 'Unknown Server'),
            'address': server_data.get('address', server_url),
            'map': server_data.get('map', 'Unknown'),
            'players': server_data.get('players', 0),
            'maxplayers': server_data.get('maxplayers', 0),
            'e': server_data.get('e', {})  # Extended info - THIS IS WHERE XSS PAYLOAD GETS STORED
        }
        
        return redirect('/server/' + sid)
        
    except urllib2.URLError as e:
        return REGISTER_ERROR_CONTENT.format("Failed to fetch server info: " + str(e))
    except ValueError as e:
        return REGISTER_ERROR_CONTENT.format("Invalid JSON response: " + str(e))
    except Exception as e:
        return REGISTER_ERROR_CONTENT.format("Error: " + str(e))

# In-memory storage for user-hosted payloads (simulating attacker-controlled game servers)
hosted_payloads = {}
payload_counter = [0]

@app.route('/host', methods=['GET', 'POST'])
def host_payload():
    """Host a custom game server info payload (simulates attacker-controlled server)"""
    if request.method == 'GET':
        return HOST_PAYLOAD_CONTENT
    
    # POST request - create a hosted payload
    payload_json = request.form.get('payload', '')
    
    if not payload_json:
        return REGISTER_ERROR_CONTENT.format("Please provide a JSON payload")
    
    try:
        # Validate it's valid JSON
        json.loads(payload_json)
        
        # Store the payload
        payload_counter[0] += 1
        pid = str(payload_counter[0])
        hosted_payloads[pid] = payload_json
        
        # Return the URL where this payload can be accessed
        payload_url = request.url_root + 'payload/' + pid
        return HOST_PAYLOAD_SUCCESS_CONTENT.format(payload_url, pid)
        
    except ValueError as e:
        return REGISTER_ERROR_CONTENT.format("Invalid JSON: " + str(e))
    except Exception as e:
        return REGISTER_ERROR_CONTENT.format("Error: " + str(e))

@app.route('/payload/<payload_id>')
def serve_payload(payload_id):
    """Serve a hosted payload as JSON (simulates game server /info endpoint)"""
    if payload_id not in hosted_payloads:
        return jsonify({"error": "Payload not found"}), 404
    
    response = make_response(hosted_payloads[payload_id])
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/server/<server_id>')
def server_details(server_id):
    """Display game server details - VULNERABLE TO STORED XSS"""
    if server_id not in game_servers:
        return "<h1>Server not found</h1>", 404
    
    server = game_servers[server_id]
    
    # Build the server info table
    # This mimics the vulnerable PHP code from lgsl_details.php
    output = ""
    
    # Basic server info (properly escaped)
    output += "<tr><td>Name</td><td>{0}</td></tr>".format(cgi.escape(server.get('name', '')))
    output += "<tr><td>Address</td><td>{0}</td></tr>".format(cgi.escape(server.get('address', '')))
    output += "<tr><td>Map</td><td>{0}</td></tr>".format(cgi.escape(server.get('map', '')))
    output += "<tr><td>Players</td><td>{0}/{1}</td></tr>".format(
        cgi.escape(str(server.get('players', 0))), 
        cgi.escape(str(server.get('maxplayers', 0)))
    )
    
    # Extended info - VULNERABLE: Missing output escaping (CVE vulnerability)
    # This is the exact vulnerability from the CVE:
    # The PHP code processes $value with html_entity_decode() before output,
    # which either decodes already-encoded entities or passes raw HTML through
    # without any escaping, allowing XSS.
    # 
    # The fix was to use htmlentities() to ENCODE output, not decode it.
    extended_info = server.get('e', {})
    for field, value in extended_info.items():
        value_str = str(value)
        
        # VULNERABLE: Apply html_entity_decode equivalent (simulating PHP vulnerability)
        # This decodes any HTML entities in the input, making encoded payloads work too
        value_decoded = html_parser.unescape(value_str)
        
        # Apply URL linkification (similar to PHP preg_replace in the vulnerable code)
        value_linked = re.sub(
            r'((https*://|https*://www\.|www\.)[\w\d.\-/=$?]*)',
            r"<a href='\1' target='_blank'>\1</a>",
            value_decoded
        )
        
        # VULNERABILITY: value is inserted into HTML without proper escaping
        # This allows stored XSS - attacker's payload from JSON is rendered as HTML
        output += "\n    <tr><td> {0} </td><td> {1} </td></tr>".format(
            cgi.escape(field), 
            value_linked  # NOT ESCAPED - allows XSS
        )
    
    # Build the full page
    page_content = SERVER_DETAILS_CONTENT.format(
        server.get('name', 'Unknown'),
        output,
        server_id
    )
    
    # Check for XSS and return flag if successful
    result = check_xss(page_content, flags[0])
    
    flag_message = ""
    if result == 'XSS':
        flag_message = '<div class="flag-message"><strong>Congratulations!</strong> XSS detected! Here is your flag: <code>{0}</code></div>'.format(flags[0])
    elif result and result != 'success':
        flag_message = '<div class="alert-message">Alert detected with message: {0} (expected "XSS")</div>'.format(cgi.escape(result))
    
    response = make_response(SERVER_DETAILS_CONTENT_WITH_RESULT.format(
        server.get('name', 'Unknown'),
        output,
        server_id,
        flag_message
    ))
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(debug=True)
