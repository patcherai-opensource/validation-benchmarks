# encoding=utf8
# XWiki Live Data Dashboard - Data Management Portal

from flask import Flask, request, Response, make_response, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# In-memory storage for live data entries
stored_entries = []

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/livedata/config', methods=['GET'])
def get_livedata_config():
    """API endpoint to get available displayer types"""
    return jsonify({
        "availableDisplayers": [
            {"id": "text", "name": "Plain Text", "description": "Display as escaped text"},
            {"id": "link", "name": "Link", "description": "Display as hyperlink"},
            {"id": "html", "name": "HTML", "description": "Display as raw HTML content"},
            {"id": "number", "name": "Number", "description": "Display as formatted number"}
        ],
        "properties": ["title", "content", "author"]
    })

def check_xss_execution(page_content, user_input):
    """Simulate another user viewing the rendered content"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    result = None
    try:
        of = open(fn, 'w')
        of.write(page_content)
        of.close()
        print "Rendering page for viewer:"
        print page_content
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "Viewer result:"
        print result
    finally:
        os.unlink(fn)
    return result

@app.route('/livedata', methods=['GET'])
def livedata_view():
    """Main Live Data dashboard view"""
    return LIVEDATA_DASHBOARD

@app.route('/livedata/entries', methods=['GET'])
def list_entries():
    """List all stored entries"""
    return jsonify({"entries": stored_entries, "count": len(stored_entries)})

@app.route('/livedata/create', methods=['GET', 'POST'])
def create_entry():
    """Create a new live data entry - vulnerable endpoint"""
    if request.method == 'GET':
        return LIVEDATA_CREATE_FORM
    
    # Parse the entry data
    try:
        # Accept both form data and JSON
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
        else:
            # Form-based submission
            data = {
                "entries": [{
                    "title": request.form.get('title', ''),
                    "content": request.form.get('content', '')
                }],
                "meta": {
                    "propertyDescriptors": []
                }
            }
            # Parse displayer configuration
            displayer = request.form.get('displayer', 'text')
            data["meta"]["propertyDescriptors"].append({
                "id": "content",
                "displayer": displayer
            })
    except Exception as e:
        return jsonify({"error": "Invalid data format", "details": str(e)}), 400
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    entries = data.get("entries", [])
    meta = data.get("meta", {})
    property_descriptors = meta.get("propertyDescriptors", [])
    
    # Build displayer map
    displayer_map = {}
    for desc in property_descriptors:
        prop_id = desc.get("id")
        displayer_type = desc.get("displayer", "text")
        displayer_map[prop_id] = displayer_type
    
    response_message = ""
    
    for entry in entries:
        title = entry.get("title", "Untitled")
        content = entry.get("content", "")
        
        # Determine how to render content based on displayer
        content_displayer = displayer_map.get("content", "text")
        
        if content_displayer == "html":
            # VULNERABILITY: Raw HTML rendering without sanitization
            # This mimics the XWiki Live Data macro vulnerability where
            # setting displayer to "html" causes unsanitized rendering
            rendered_content = content
        elif content_displayer == "link":
            rendered_content = '<a href="{0}">{0}</a>'.format(cgi.escape(content))
        elif content_displayer == "number":
            try:
                rendered_content = '{:,}'.format(float(content))
            except:
                rendered_content = cgi.escape(content)
        else:
            # Default: text - properly escaped
            rendered_content = cgi.escape(content)
        
        # Store the entry
        stored_entry = {
            "title": cgi.escape(title),
            "content": content,
            "rendered_content": rendered_content,
            "displayer": content_displayer
        }
        stored_entries.append(stored_entry)
        
        # Generate the page that will be "viewed" by another user
        view_page = LIVEDATA_VIEW_PAGE.format(
            title=cgi.escape(title),
            content=rendered_content
        )
        
        # Simulate another user viewing the page (XSS detection)
        xss_result = check_xss_execution(view_page, content)
        
        if xss_result == 'XSS':
            # XSS executed successfully - return flag
            response_message = LIVEDATA_SUCCESS_RESPONSE.format(flag=flags[0])
        elif xss_result:
            response_message = LIVEDATA_PARTIAL_RESPONSE.format(result=cgi.escape(xss_result))
        else:
            response_message = LIVEDATA_ENTRY_CREATED
    
    if not entries:
        response_message = '<div class="alert alert-warning">No entries provided in request</div>'
    
    return LIVEDATA_RESULT_PAGE.format(message=response_message)


if __name__ == '__main__':
    app.run(debug=True)
