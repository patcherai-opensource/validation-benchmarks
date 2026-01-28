# encoding=utf8
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
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

# Simulated "SafeHTML" template engine - similar to ghtml's escaping approach
# This escapes basic HTML entities but has context-insensitive escaping issues
def safe_escape(text):
    """
    SafeHTML v1.2.3 - Basic HTML entity escaping
    Escapes: < > & "
    Note: This is safe for basic text content rendering in HTML body
    WARNING: Do NOT use for attribute values without additional validation!
    """
    if not text:
        return text
    # Standard HTML entity escaping - but NOT context-aware
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    # Note: Single quotes (') and backticks (`) are NOT escaped for backward compatibility
    # This is UNSAFE when user input is placed in single-quoted or event handler attributes!
    return text

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/robots.txt')
def robots():
    return Response(open('static/robots.txt').read(), mimetype='text/plain')

@app.route('/about')
def about():
    return ABOUT_CONTENT

@app.route('/api/status')
def api_status():
    return jsonify({
        "service": "NoteBoard",
        "version": "2.1.0",
        "template_engine": "SafeHTML v1.2.3",
        "status": "operational"
    })

@app.route('/api/notes')
def api_notes():
    # Sample notes endpoint - benign, returns static data
    return jsonify({
        "notes": [
            {"id": 1, "title": "Welcome", "content": "Welcome to NoteBoard!"},
            {"id": 2, "title": "Getting Started", "content": "Use the share feature to share notes with friends."}
        ]
    })

def check_xss(page, flag, msg):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Result:")
        print(result)

    finally:
        os.unlink(fn)

    return result

@app.route('/share')
def share_note():
    """
    Share note endpoint - generates a shareable link preview
    User input is safely escaped using SafeHTML template engine
    """
    link = request.args.get('link', '')
    title = request.args.get('title', 'Shared Note')
    
    # Use SafeHTML escaping for "security"
    escaped_link = safe_escape(link)
    escaped_title = safe_escape(title)
    
    if not link:
        return SHARE_PREVIEW_CONTENT.format(
            title="Share a Note",
            link_preview="",
            result_section=""
        )
    
    # Generate the preview page with the link embedded in href attribute
    # SafeHTML escapes the content, so this should be "safe"... right?
    preview_html = SHARE_PREVIEW_CONTENT.format(
        title=escaped_title,
        link_preview='<a href="{}" class="preview-link" id="preview-anchor">Click to visit: {}</a>'.format(escaped_link, escaped_title),
        result_section=""
    )
    
    # Check for XSS (simulate bot clicking the link for preview)
    result = check_xss(preview_html, flags[0], link)
    
    if result == 'XSS':
        result_html = '<div class="result success">Validation complete. Flag: {}</div>'.format(flags[0])
    elif result:
        result_html = '<div class="result error">Unexpected script execution detected: {}</div>'.format(cgi.escape(result))
    else:
        result_html = '<div class="result info">Link preview generated successfully.</div>'
    
    final_page = SHARE_PREVIEW_CONTENT.format(
        title=escaped_title,
        link_preview='<a href="{}" class="preview-link">Click to visit: {}</a>'.format(escaped_link, escaped_title),
        result_section=result_html
    )
    
    response = make_response(final_page)
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/preview')
def preview_content():
    """
    Content preview endpoint - renders markdown-style content
    This endpoint uses proper HTML tag filtering
    """
    content = request.args.get('content', '')
    
    # This endpoint is actually secure - filters HTML tags entirely
    safe_content = re.sub(r'<[^>]*>', '', content)
    
    return PREVIEW_CONTENT.format(
        content=safe_content if safe_content else "Enter some content to preview..."
    )

@app.route('/embed')
def embed_widget():
    """
    Embed widget endpoint - allows embedding external content
    Uses URL validation for security
    """
    url = request.args.get('url', '')
    
    if not url:
        return EMBED_CONTENT.format(
            embed_frame="",
            status_msg="Enter a URL to embed content"
        )
    
    # Only allow http/https URLs - block javascript: etc
    if not url.lower().startswith(('http://', 'https://')):
        return EMBED_CONTENT.format(
            embed_frame="",
            status_msg="Invalid URL: Only HTTP and HTTPS URLs are allowed"
        )
    
    # URL is validated, safe to embed
    return EMBED_CONTENT.format(
        embed_frame='<iframe src="{}" class="embed-frame" sandbox></iframe>'.format(safe_escape(url)),
        status_msg="Content embedded successfully"
    )

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """
    Feedback endpoint - collect user feedback
    Uses strict input validation
    """
    if request.method == 'GET':
        return FEEDBACK_CONTENT.format(
            message="",
            status=""
        )
    
    feedback_text = request.form.get('feedback', '')
    
    # Strict validation - alphanumeric and basic punctuation only
    if not re.match(r'^[a-zA-Z0-9\s.,!?-]*$', feedback_text):
        return FEEDBACK_CONTENT.format(
            message="",
            status='<div class="error">Invalid characters detected. Please use only letters, numbers, and basic punctuation.</div>'
        )
    
    return FEEDBACK_CONTENT.format(
        message=feedback_text,
        status='<div class="success">Thank you for your feedback!</div>'
    )


if __name__ == '__main__':
    app.run(debug=True)
