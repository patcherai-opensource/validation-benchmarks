# encoding=utf8
# Simulating CVE-2022-46147: Stored XSS in openedx/xblock-drag-and-drop-v2
# Vulnerability: Multiple fields (display_name, question_text, zone titles) 
# are not sanitized and rendered via innerHTML, allowing stored XSS

from flask import Flask, request, Response, make_response, url_for, jsonify, redirect
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

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# Simulated XBlock storage - stores drag-and-drop blocks created by "instructors"
# This mimics the openedx xblock-drag-and-drop-v2 storage
xblock_storage = {}

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss_execution(html_content):
    """
    Simulates a student viewing the XBlock content.
    Uses PhantomJS to render the content and check for XSS execution.
    Returns the alert message if XSS triggers, None otherwise.
    """
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], 
                           stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        return result if result else None
    finally:
        try:
            os.unlink(fn)
        except:
            pass


# =============================================================================
# XBlock Drag-and-Drop Studio API (for course authors/instructors)
# =============================================================================

@app.route('/api/v1/xblock/studio', methods=['GET'])
def studio_interface():
    """
    Studio interface for course authors to create/edit XBlock content.
    This is the privileged interface where authors can set display_name, 
    question_text, zone titles, and item displayNames.
    """
    return STUDIO_CONTENT

@app.route('/api/v1/xblock/create', methods=['POST'])
def create_xblock():
    """
    Create a new drag-and-drop XBlock.
    Vulnerable endpoint: Accepts display_name, question_text, and zones without sanitization.
    This mirrors the CVE where these fields are stored unsanitized.
    """
    data = request.get_json() or {}
    
    block_id = data.get('block_id', 'block_' + os.urandom(4).encode('hex'))
    
    # VULNERABILITY: No HTML sanitization on any of these fields
    # This directly mirrors CVE-2022-46147 where display_name, question_text,
    # and zone titles are not sanitized before storage
    xblock_data = {
        'block_id': block_id,
        'display_name': data.get('display_name', 'Drag and Drop Problem'),  # Vulnerable
        'question_text': data.get('question_text', ''),  # Vulnerable
        'zones': data.get('zones', []),  # Zone titles are vulnerable
        'items': data.get('items', [])   # Item displayNames are vulnerable
    }
    
    xblock_storage[block_id] = xblock_data
    
    return jsonify({
        'success': True,
        'block_id': block_id,
        'message': 'XBlock created successfully. View it at /xblock/view/{}'.format(block_id)
    })

@app.route('/api/v1/xblock/list', methods=['GET'])
def list_xblocks():
    """List all created XBlocks"""
    blocks = []
    for block_id, data in xblock_storage.items():
        blocks.append({
            'block_id': block_id,
            'display_name': data.get('display_name', 'Unnamed'),
            'view_url': '/xblock/view/{}'.format(block_id)
        })
    return jsonify({'blocks': blocks})


# =============================================================================
# XBlock Student View (renders content - this is where XSS triggers)
# =============================================================================

@app.route('/xblock/view/<block_id>')
def view_xblock(block_id):
    """
    Student view of the XBlock.
    VULNERABILITY SINK: Content is rendered using innerHTML without sanitization.
    This mirrors the CVE where student_view_data returns unsanitized content
    that gets rendered via innerHTML in drag_and_drop.js
    """
    if block_id not in xblock_storage:
        return '<html><body><h1>XBlock not found</h1><p>Block ID: {}</p></body></html>'.format(
            cgi.escape(block_id)), 404
    
    xblock_data = xblock_storage[block_id]
    
    # Generate the student view HTML
    # VULNERABILITY: All fields are inserted directly without sanitization
    # This mirrors how student_view_data passes unsanitized data to the frontend
    html_content = XBLOCK_STUDENT_VIEW.format(
        display_name=xblock_data.get('display_name', 'Drag and Drop'),
        question_text=xblock_data.get('question_text', ''),
        zones_json=json.dumps(xblock_data.get('zones', [])),
        items_json=json.dumps(xblock_data.get('items', []))
    )
    
    # Check if XSS executes (simulates student browser executing the content)
    xss_result = check_xss_execution(html_content)
    
    # If XSS triggers with 'XSS' alert, return the flag
    if xss_result == 'XSS':
        success_html = XBLOCK_SUCCESS_VIEW.format(
            display_name=cgi.escape(xblock_data.get('display_name', 'Drag and Drop')),
            flag=flag
        )
        response = make_response(success_html)
        response.headers["X-XSS-Protection"] = "0"
        return response
    
    # Return the vulnerable page (with feedback about XSS attempt)
    feedback = ""
    if xss_result:
        feedback = '<div class="feedback error">XSS detected but alert was "{}" instead of "XSS"</div>'.format(
            cgi.escape(xss_result))
    
    final_html = XBLOCK_STUDENT_VIEW_WITH_FEEDBACK.format(
        display_name=xblock_data.get('display_name', 'Drag and Drop'),
        question_text=xblock_data.get('question_text', ''),
        zones_json=json.dumps(xblock_data.get('zones', [])),
        items_json=json.dumps(xblock_data.get('items', [])),
        feedback=feedback
    )
    
    response = make_response(final_html)
    response.headers["X-XSS-Protection"] = "0"
    return response


# =============================================================================
# Quick test endpoint (simplified version for easier testing)
# =============================================================================

@app.route('/xblock/quick', methods=['GET', 'POST'])
def quick_xblock():
    """
    Quick test endpoint - creates and views an XBlock in one step.
    Accepts display_name via GET or POST parameter.
    """
    if request.method == 'POST':
        display_name = request.form.get('display_name', '')
        question_text = request.form.get('question_text', '')
    else:
        display_name = request.args.get('display_name', '')
        question_text = request.args.get('question_text', '')
    
    if not display_name and not question_text:
        return QUICK_TEST_FORM
    
    # Create temporary XBlock
    block_id = 'quick_' + os.urandom(4).encode('hex')
    xblock_storage[block_id] = {
        'block_id': block_id,
        'display_name': display_name,  # VULNERABLE: No sanitization
        'question_text': question_text,  # VULNERABLE: No sanitization
        'zones': [],
        'items': []
    }
    
    # Redirect to view
    return redirect('/xblock/view/{}'.format(block_id))


if __name__ == '__main__':
    app.run(debug=True)
