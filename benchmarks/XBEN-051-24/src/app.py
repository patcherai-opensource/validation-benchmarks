# encoding=utf8
# OpenLearn Course Builder - Drag & Drop Block Editor
# Educational content management system

from flask import Flask, request, Response, make_response, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# In-memory storage for course blocks (simulates database)
stored_blocks = {}

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/studio')
def studio():
    """Course authoring interface - where instructors create content"""
    return STUDIO_CONTENT

@app.route('/api/blocks', methods=['GET'])
def list_blocks():
    """API endpoint to list all created blocks"""
    return jsonify({"blocks": list(stored_blocks.keys())})

def check_xss(page, flag, msg):
    """Check if XSS payload executes in headless browser"""
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

    if msg == "":
        data = '<div class="block-status"><span class="status-icon">&#128221;</span><br>Block preview ready. Add content to see it rendered.</div>'
    else:
        if result == 'XSS':
            data = '<div class="block-status success"><span class="status-icon">&#127942;</span><br>Security Alert Triggered!<p>Debug Token: {0}</div>'.format(flag)
        elif result:
            data = '<div class="block-status warning"><span class="status-icon">&#9888;</span><br>Alert detected with content: {0}<br>Expected: XSS</div>'.format(cgi.escape(result))
        else:
            data = '<div class="block-status error"><span class="status-icon">&#10060;</span><br>Content rendered without issues.</div>'
    return data


@app.route('/xblock/edit', methods=['GET', 'POST'])
def edit_xblock():
    """
    XBlock Editor - Edit drag-and-drop block properties
    Fields: display_name, question_text, zone_title
    Vulnerable to stored XSS - content is saved and rendered without proper sanitization
    """
    if request.method == 'POST':
        display_name = request.form.get('display_name', '')
        question_text = request.form.get('question_text', '')
        zone_title = request.form.get('zone_title', '')
        
        # Minimal input validation - intentionally incomplete (like the CVE)
        # Only blocks obvious script tags but misses other vectors
        blocked_patterns = ['<script', '</script', 'javascript:']
        
        combined_input = display_name + question_text + zone_title
        for pattern in blocked_patterns:
            if pattern.lower() in combined_input.lower():
                return XBLOCK_EDIT_CONTENT.format(
                    display_name="",
                    question_text="",
                    zone_title="",
                    result="",
                    error_msg='<div class="validation-error">&#9888; Blocked: Script tags are not allowed in content fields.</div>'
                )
        
        # Store the block data (simulating database save)
        block_id = os.urandom(8).encode('hex')
        stored_blocks[block_id] = {
            'display_name': display_name,
            'question_text': question_text,
            'zone_title': zone_title
        }
        
        # Render preview - vulnerable: content rendered via innerHTML without sanitization
        preview_html = XBLOCK_PREVIEW.format(
            display_name=display_name,
            question_text=question_text,
            zone_title=zone_title
        )
        
        # Check for XSS execution
        result = check_xss(preview_html, flags[0], combined_input)
        
        response = make_response(XBLOCK_EDIT_CONTENT.format(
            display_name=cgi.escape(display_name),
            question_text=cgi.escape(question_text),
            zone_title=cgi.escape(zone_title),
            result=result,
            error_msg=""
        ))
        response.headers["X-XSS-Protection"] = "0"
        return response
    
    # GET request - show empty form
    return XBLOCK_EDIT_CONTENT.format(
        display_name="",
        question_text="",
        zone_title="",
        result='<div class="block-status"><span class="status-icon">&#128221;</span><br>Create a new Drag & Drop block. Fill in the fields and click Preview.</div>',
        error_msg=""
    )


@app.route('/xblock/view/<block_id>')
def view_xblock(block_id):
    """View a stored XBlock - renders saved content (victim view)"""
    if block_id not in stored_blocks:
        return '<h1>Block not found</h1>', 404
    
    block = stored_blocks[block_id]
    # Vulnerable: renders stored content without sanitization
    preview_html = XBLOCK_PREVIEW.format(
        display_name=block['display_name'],
        question_text=block['question_text'],
        zone_title=block['zone_title']
    )
    
    response = make_response(preview_html)
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(debug=True)
