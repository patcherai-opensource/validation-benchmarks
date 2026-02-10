# encoding=utf8
# -*- coding: utf-8 -*-
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, redirect
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

# Storage for port groups (simulating database)
PORT_GROUPS_FILE = '/tmp/port_groups.json'

def load_port_groups():
    """Load port groups from storage"""
    try:
        with open(PORT_GROUPS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_port_groups(groups):
    """Save port groups to storage"""
    with open(PORT_GROUPS_FILE, 'w') as f:
        json.dump(groups, f)

def add_port_group(name, description):
    """Add a new port group"""
    groups = load_port_groups()
    group_id = len(groups) + 1
    groups.append({
        'id': group_id,
        'name': name,
        'description': description
    })
    save_port_groups(groups)
    return group_id

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, has_content, tag):
    """Check if XSS is triggered when rendering the page"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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

    if not has_content:
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Create a port group to begin</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>No XSS detected.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


############## Port Group Management (Stored XSS) #################### 

@app.route('/port-groups', methods=['GET'])
def list_port_groups():
    """List all port groups - form to create new groups"""
    groups = load_port_groups()
    groups_html = ""
    for g in groups:
        # Vulnerable: name is properly escaped in the list view
        groups_html += '<li>ID: {0} - {1}</li>'.format(g['id'], cgi.escape(g['name']))
    
    return PORT_GROUP_LIST_CONTENT.format(groups_html if groups_html else "<li>No port groups created</li>")

@app.route('/port-groups', methods=['POST'])
def create_port_group():
    """Create a new port group - accepts name parameter (Stored XSS entry point)"""
    name = request.form.get('name', '')
    description = request.form.get('desc', '')
    
    if name:
        # Store the name WITHOUT sanitization (this is the vulnerability)
        # The payload gets stored and will be rendered unsanitized in port-settings
        add_port_group(name, description)
    
    return redirect('/port-groups')

@app.route('/port-settings')
def port_settings():
    """Port Settings page - renders stored port groups (Stored XSS sink)
    
    This simulates the vulnerable EditPortsController.php where group names
    are rendered directly into HTML without escaping.
    """
    groups = load_port_groups()
    
    # Build the port group options HTML - VULNERABLE: no escaping of group names
    # This mirrors the CVE vulnerability where $group->name is directly interpolated
    port_group_options = ""
    for group in groups:
        # VULNERABLE: group['name'] is inserted without htmlentities() escaping
        # Matches: '<option value="' . $group->id . '" selected>' . $group->name . '</option>'
        port_group_options += '<option value="{0}" selected>{1}</option>'.format(group['id'], group['name'])
    
    has_content = len(groups) > 0
    
    # Build the page content
    page_content = PORT_SETTINGS_CONTENT.format("10", "Port Settings", port_group_options)
    
    # Check for XSS execution in the rendered page
    result = check_xss(page_content, flags[0], has_content, 'xss_easy_med')
    
    return PORT_SETTINGS_CONTENT.format("10", "Port Settings", port_group_options) + result

@app.route('/reset-groups', methods=['POST'])
def reset_groups():
    """Reset all port groups"""
    save_port_groups([])
    return redirect('/port-groups')

if __name__ == '__main__':
    app.run(debug=True)
