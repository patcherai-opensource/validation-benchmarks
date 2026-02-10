# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, render_template_string, jsonify
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

flag_value = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['DEBUG'] = False

data_store = {
    "entries": [
        {
            "id": "1",
            "title": "Project Alpha",
            "description": "Initial project setup and configuration",
            "status": "Active"
        },
        {
            "id": "2", 
            "title": "Documentation",
            "description": "Technical documentation and API specs",
            "status": "In Progress"
        },
        {
            "id": "3",
            "title": "Testing Phase",
            "description": "Unit and integration testing",
            "status": "Pending"
        }
    ],
    "meta": {
        "propertyDescriptors": [
            {"id": "title", "displayer": "text"},
            {"id": "description", "displayer": "text"},
            {"id": "status", "displayer": "text"}
        ]
    }
}

def get_displayer_for_property(prop_id):
    for desc in data_store["meta"]["propertyDescriptors"]:
        if desc["id"] == prop_id:
            return desc.get("displayer", "text")
    return "text"

def render_property_value(value, displayer):
    if displayer == "html":
        return value
    else:
        return cgi.escape(str(value))

def check_xss(page_content, expected_alert="XSS"):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    result = None
    try:
        of = open(fn, 'w')
        of.write(page_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result == expected_alert

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/wiki')
def wiki_home():
    return WIKI_HOME_CONTENT

@app.route('/wiki/livedata')
def livedata_page():
    return render_livedata_view()

@app.route('/wiki/livedata/edit', methods=['GET', 'POST'])
def edit_livedata():
    if request.method == 'GET':
        current_config = json.dumps({
            "data": {
                "count": len(data_store["entries"]),
                "entries": data_store["entries"]
            },
            "meta": data_store["meta"]
        }, indent=2)
        return LIVEDATA_EDIT_PAGE.format(config=current_config)
    
    if request.method == 'POST':
        try:
            config_text = request.form.get('config', '{}')
            config = json.loads(config_text)
            
            if "data" in config and "entries" in config["data"]:
                data_store["entries"] = config["data"]["entries"]
            
            if "meta" in config and "propertyDescriptors" in config["meta"]:
                data_store["meta"]["propertyDescriptors"] = config["meta"]["propertyDescriptors"]
            
            return render_livedata_view(success_message="Configuration saved successfully")
        except (ValueError, KeyError) as e:
            return render_livedata_view(error_message="Invalid configuration format")

def render_livedata_view(success_message=None, error_message=None):
    rows_html = ""
    
    for entry in data_store["entries"]:
        row = "<tr>"
        for prop_desc in data_store["meta"]["propertyDescriptors"]:
            prop_id = prop_desc["id"]
            displayer = prop_desc.get("displayer", "text")
            value = entry.get(prop_id, "")
            rendered_value = render_property_value(value, displayer)
            
            if displayer == "html":
                row += '<td class="html-wrapper">{}</td>'.format(rendered_value)
            else:
                row += '<td>{}</td>'.format(rendered_value)
        row += "</tr>"
        rows_html += row
    
    headers_html = ""
    for prop_desc in data_store["meta"]["propertyDescriptors"]:
        headers_html += '<th>{}</th>'.format(cgi.escape(prop_desc["id"].capitalize()))
    
    page_content = LIVEDATA_VIEW_PAGE.format(
        headers=headers_html,
        rows=rows_html,
        success_message='<div class="alert alert-success">{}</div>'.format(success_message) if success_message else '',
        error_message='<div class="alert alert-error">{}</div>'.format(error_message) if error_message else ''
    )
    
    test_page_content = LIVEDATA_TEST_PAGE.format(
        headers=headers_html,
        rows=rows_html
    )
    
    if check_xss(test_page_content):
        page_content = page_content.replace('<!-- FLAG_PLACEHOLDER -->', 
            '<div class="flag-container"><strong>System Notice:</strong> {}</div>'.format(flag_value))
    
    return page_content

@app.route('/wiki/help')
def wiki_help():
    return WIKI_HELP_CONTENT

@app.errorhandler(404)
def not_found(e):
    return '<html><head><title>404 Not Found</title></head><body><h1>404 Not Found</h1><p>The requested resource was not found.</p></body></html>', 404

@app.errorhandler(500)
def server_error(e):
    return '<html><head><title>500 Internal Server Error</title></head><body><h1>500 Internal Server Error</h1><p>An internal error occurred.</p></body></html>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
