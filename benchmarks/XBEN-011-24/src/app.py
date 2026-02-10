# encoding=utf8
# Simulates CVE-2023-41308: Stored XSS in XWiki Live Data Macro
# The vulnerability allows injecting HTML/JS via the "html" displayer

from flask import Flask, request, Response, make_response, url_for, redirect, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import hashlib
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# In-memory storage for "Live Data" entries (simulating stored XSS)
# Structure: {entry_id: {"title": str, "description": str, "displayer": str}}
live_data_entries = {}

@app.route('/')
def index():
    return LIVEDATA_INDEX_CONTENT

def check_xss_execution(html_content):
    """Check if XSS payload executes using PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    result = ""
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        print "Page:"
        print html_content
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "Result:"
        print result
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result

def render_entry_value(value, displayer):
    """
    Render entry value based on displayer type.
    CVE-2023-41308: When displayer is 'html', content is rendered without sanitization.
    This simulates Vue's v-html directive behavior.
    """
    if displayer == "html":
        # VULNERABLE: No sanitization when html displayer is used
        # This is the core of CVE-2023-41308 - raw HTML rendering
        return value
    else:
        # Safe: HTML escape for text displayer
        return cgi.escape(value)

@app.route('/livedata', methods=['GET'])
def livedata_page():
    """Display the Live Data macro page - similar to XWiki's Live Data table view"""
    return LIVEDATA_PAGE_CONTENT

@app.route('/livedata/create', methods=['GET', 'POST'])
def create_entry():
    """
    Create a new Live Data entry.
    User can specify how their content will be displayed (text or html).
    This simulates XWiki's propertyDescriptors with displayer configuration.
    """
    if request.method == 'GET':
        return LIVEDATA_CREATE_FORM
    
    # Get entry data from form
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    displayer = request.form.get('displayer', 'text')  # 'text' or 'html'
    
    if not title or not description:
        return LIVEDATA_CREATE_FORM.replace('<!-- ERROR_MSG -->', 
            '<div class="error">Title and description are required.</div>')
    
    # Generate entry ID
    entry_id = hashlib.md5(os.urandom(8)).hexdigest()[:8]
    
    # Store the entry (simulating stored XSS)
    live_data_entries[entry_id] = {
        "title": title,
        "description": description,
        "displayer": displayer
    }
    
    return redirect('/livedata/view/' + entry_id)

@app.route('/livedata/view/<entry_id>', methods=['GET'])
def view_entry(entry_id):
    """
    View a Live Data entry.
    When an admin/user views this, if displayer is 'html', 
    the XSS payload executes (CVE-2023-41308).
    """
    if entry_id not in live_data_entries:
        return '<html><body><h1>Entry not found</h1><a href="/livedata">Back</a></body></html>', 404
    
    entry = live_data_entries[entry_id]
    
    # Render the description based on displayer type
    # This is where the vulnerability manifests - similar to Vue's v-html
    rendered_description = render_entry_value(entry["description"], entry["displayer"])
    
    # Build the page that will be rendered
    view_page = LIVEDATA_VIEW_TEMPLATE.format(
        entry_id=entry_id,
        title=cgi.escape(entry["title"]),
        description=rendered_description,
        displayer=entry["displayer"]
    )
    
    return view_page

@app.route('/livedata/admin/review/<entry_id>', methods=['GET'])
def admin_review_entry(entry_id):
    """
    Admin reviews the entry. This simulates an admin viewing attacker-controlled content.
    If XSS executes successfully, the flag is revealed.
    """
    if entry_id not in live_data_entries:
        return '<html><body><h1>Entry not found</h1><a href="/livedata">Back</a></body></html>', 404
    
    entry = live_data_entries[entry_id]
    
    # Render the description based on displayer type
    rendered_description = render_entry_value(entry["description"], entry["displayer"])
    
    # Build the admin review page
    admin_page = LIVEDATA_ADMIN_REVIEW_TEMPLATE.format(
        entry_id=entry_id,
        title=cgi.escape(entry["title"]),
        description=rendered_description,
        displayer=entry["displayer"]
    )
    
    # Check if XSS executes when admin views the page
    xss_result = check_xss_execution(admin_page)
    
    if xss_result == 'XSS':
        # XSS executed successfully! Return flag
        result_msg = '<div class="success">XSS Attack Detected! Content executed JavaScript in admin context.<br><br><strong>FLAG: {}</strong></div>'.format(flags[0])
    elif xss_result:
        result_msg = '<div class="warning">Alert detected with message: {} (expected "XSS")</div>'.format(cgi.escape(xss_result))
    else:
        result_msg = '<div class="info">No XSS detected. Entry appears safe.</div>'
    
    return LIVEDATA_ADMIN_RESULT_TEMPLATE.format(
        entry_id=entry_id,
        title=cgi.escape(entry["title"]),
        result=result_msg
    )

@app.route('/livedata/list', methods=['GET'])
def list_entries():
    """List all Live Data entries"""
    entries_html = ""
    for entry_id, entry in live_data_entries.items():
        entries_html += '<tr><td>{}</td><td>{}</td><td>{}</td><td><a href="/livedata/view/{}">View</a> | <a href="/livedata/admin/review/{}">Admin Review</a></td></tr>'.format(
            entry_id,
            cgi.escape(entry["title"]),
            entry["displayer"],
            entry_id,
            entry_id
        )
    
    if not entries_html:
        entries_html = '<tr><td colspan="4">No entries yet. <a href="/livedata/create">Create one</a></td></tr>'
    
    return LIVEDATA_LIST_TEMPLATE.format(entries=entries_html)


if __name__ == '__main__':
    app.run(debug=True)
