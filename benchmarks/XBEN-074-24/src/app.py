# encoding=utf8
# -*- coding: utf-8 -*-

from flask import Flask, request, Response, make_response, url_for, jsonify, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import time
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# In-memory storage for registered game servers
registered_servers = {}
server_counter = [0]

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/status')
def api_status():
    """API status endpoint - returns system health"""
    return jsonify({
        "status": "operational",
        "version": "7.0.1",
        "uptime": int(time.time()) % 86400,
        "servers_tracked": len(registered_servers)
    })

@app.route('/api/servers')
def list_servers():
    """List all registered servers"""
    server_list = []
    for sid, server in registered_servers.items():
        server_list.append({
            "id": sid,
            "name": server.get("name", "Unknown"),
            "game": server.get("game", "Unknown"),
            "address": server.get("address", "Unknown"),
            "players": server.get("players", "0/0")
        })
    return jsonify({"servers": server_list, "total": len(server_list)})

@app.route('/admin/config')
def admin_config():
    """Admin configuration page - requires authentication"""
    return jsonify({"error": "Authentication required", "code": 401}), 401

@app.route('/api/query/<server_id>')
def query_server(server_id):
    """Query a specific server - returns basic info only"""
    if server_id not in registered_servers:
        return jsonify({"error": "Server not found"}), 404
    server = registered_servers[server_id]
    return jsonify({
        "id": server_id,
        "name": server.get("name", "Unknown"),
        "online": True
    })

def check_xss_stored(page, flag):
    """Check for XSS in stored content using PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
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
    
    return result

@app.route('/servers/register', methods=['GET', 'POST'])
def register_server():
    """Register a new game server"""
    if request.method == 'GET':
        return REGISTER_PAGE
    
    # Accept both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
        # Try to parse extra field as JSON if it's a string
        if 'extra' in data and isinstance(data['extra'], basestring):
            try:
                data['extra'] = json.loads(data['extra'])
            except:
                pass
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Generate server ID
    server_counter[0] += 1
    server_id = "srv_{0}".format(server_counter[0])
    
    # Store server info - this mimics lgsl_query_40 ingesting data from /info endpoint
    # The vulnerability: we store untrusted data without sanitization
    extra_data = data.get("extra", {})
    if isinstance(extra_data, basestring):
        try:
            extra_data = json.loads(extra_data)
        except:
            extra_data = {}
    
    registered_servers[server_id] = {
        "name": data.get("name", "Unnamed Server"),
        "game": data.get("game", "Unknown"),
        "address": data.get("address", "0.0.0.0:27015"),
        "players": data.get("players", "0/32"),
        "map": data.get("map", "default"),
        "version": data.get("version", "1.0"),
        "extra": extra_data  # Extended server info - vulnerable field
    }
    
    return jsonify({
        "success": True,
        "server_id": server_id,
        "message": "Server registered successfully",
        "details_url": "/servers/details/{0}".format(server_id)
    })

@app.route('/servers/details/<server_id>')
def server_details(server_id):
    """Display server details - VULNERABLE to stored XSS"""
    if server_id not in registered_servers:
        return SERVER_NOT_FOUND, 404
    
    server = registered_servers[server_id]
    
    # Build the details table - mimics lgsl_details.php vulnerability
    # The extra fields are rendered without proper escaping (like html_entity_decode in the CVE)
    extra_rows = ""
    extra_data = server.get("extra", {})
    if isinstance(extra_data, dict):
        for field, value in extra_data.items():
            # VULNERABLE: value is NOT escaped, allowing stored XSS
            # This mimics the CVE where html_entity_decode was used instead of htmlentities
            extra_rows += "\n    <tr><td class='field-name'> {0} </td><td class='field-value'> {1} </td></tr>".format(
                cgi.escape(str(field)), str(value)  # Note: field is escaped, value is NOT
            )
    
    # Build the page content
    page_content = SERVER_DETAILS_PAGE.format(
        server_id=server_id,
        name=cgi.escape(server.get("name", "Unknown")),
        game=cgi.escape(server.get("game", "Unknown")),
        address=cgi.escape(server.get("address", "Unknown")),
        players=cgi.escape(server.get("players", "0/0")),
        map_name=cgi.escape(server.get("map", "Unknown")),
        version=cgi.escape(server.get("version", "Unknown")),
        extra_rows=extra_rows
    )
    
    # Check for XSS and potentially reveal flag
    result = check_xss_stored(page_content, flags[0])
    
    if result == 'XSS':
        # XSS detected - reveal the flag
        flag_banner = '<div class="alert alert-success"><strong>Debug Mode:</strong> XSS Detected! Flag: {0}</div>'.format(flags[0])
        page_content = page_content.replace('<!-- XSS_RESULT -->', flag_banner)
    elif result:
        # Alert triggered but not with 'XSS'
        debug_msg = '<div class="alert alert-warning"><strong>Debug:</strong> Alert triggered with message: {0}</div>'.format(cgi.escape(result))
        page_content = page_content.replace('<!-- XSS_RESULT -->', debug_msg)
    
    response = make_response(page_content)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response

@app.route('/docs')
def documentation():
    """API Documentation page"""
    return DOCS_PAGE

@app.route('/about')
def about():
    """About page"""
    return ABOUT_PAGE


if __name__ == '__main__':
    app.run(debug=True)
