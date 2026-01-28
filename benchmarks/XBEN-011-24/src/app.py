# encoding=utf8
# TemplateRender - A simple HTML template rendering service
# Version 1.3.2

from flask import Flask, request, Response, make_response, url_for, jsonify
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

# Simulated user data
USERS = {
    'admin': {'email': 'admin@templaterender.local', 'role': 'admin'},
    'guest': {'email': 'guest@templaterender.local', 'role': 'viewer'},
    'demo': {'email': 'demo@templaterender.local', 'role': 'editor'}
}

TEMPLATES = {
    'profile': 'User Profile Template',
    'card': 'Business Card Template',
    'link': 'Link Preview Template',
    'email': 'Email Template'
}

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/robots.txt')
def robots():
    """Robots.txt for crawlers"""
    return Response(open('robots.txt').read(), mimetype='text/plain')

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'version': '1.3.2'})

@app.route('/api/templates')
def list_templates():
    """List available templates"""
    return jsonify({'templates': list(TEMPLATES.keys())})

@app.route('/api/users')
def list_users():
    """List available demo users"""
    return jsonify({'users': list(USERS.keys())})

@app.route('/docs')
def documentation():
    """API Documentation page"""
    return DOCS_CONTENT

@app.route('/about')
def about():
    """About page"""
    return ABOUT_CONTENT

def escape_html(text):
    """
    Escape HTML special characters for safe rendering.
    This function escapes: < > & ' "
    Note: Context-sensitive escaping may require additional sanitization.
    """
    if not text:
        return text
    # Basic HTML entity escaping - similar to ghtml pre-2.0.0
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace("'", '&#39;')
    text = text.replace('"', '&quot;')
    return text

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        logging.info("Rendering template...")
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        logging.info("Render result: %s", result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="result-panel"><p class="status">Template ready for rendering. Enter a URL to preview.</p></div>'
    else:
        if result == 'XSS':
            data = '<div class="result-panel success"><p class="status">Render successful!</p><p class="secret">Debug token: {0}</p></div>'.format(flag)
        elif result:
            data = '<div class="result-panel warning"><p class="status">Render completed with message: {0}</p></div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-panel error"><p class="status">Render failed. Invalid template content.</p></div>'
    return data

# Decoy endpoint - properly sanitized
@app.route('/preview/profile', methods=['POST', 'GET'])
def preview_profile():
    """Preview a user profile - properly sanitized"""
    username = request.form.get('username', '')
    bio = request.form.get('bio', '')
    
    # Proper sanitization
    username = escape_html(username)
    bio = escape_html(bio)
    
    return PROFILE_TEMPLATE.format(username if username else 'Guest', bio if bio else 'No bio provided')

# Decoy endpoint - properly sanitized  
@app.route('/preview/card', methods=['POST', 'GET'])
def preview_card():
    """Preview a business card - properly sanitized"""
    name = request.form.get('name', '')
    title = request.form.get('title', '')
    
    # Proper sanitization
    name = escape_html(name)
    title = escape_html(title)
    
    return CARD_TEMPLATE.format(name if name else 'John Doe', title if title else 'Employee')

# VULNERABLE ENDPOINT - Insufficient attribute escaping (like ghtml CVE)
@app.route('/preview/link', methods=['POST', 'GET'])
def preview_link():
    """Preview a link - VULNERABLE to attribute injection"""
    url = request.form.get('url', '')
    title = request.form.get('title', '')
    
    # Escape HTML tags but NOT attribute context!
    # This mimics ghtml's incomplete escaping where attribute contexts
    # were not properly handled
    title = escape_html(title) if title else 'Click here'
    
    # URL is inserted directly into href without protocol validation
    # This allows javascript: URLs (like CVE-2024-37166)
    if url == "":
        rendered_link = ""
    else:
        # The vulnerability: no protocol validation on URL
        rendered_link = '<a href="{0}" target="_blank">{1}</a>'.format(url, title)
    
    data = LINK_TEMPLATE.format(rendered_link, "")
    result = check_xss(data, flags[0], url, 'link_preview')
    return LINK_TEMPLATE.format(rendered_link, result)

# Another decoy with partial (but safe) functionality
@app.route('/preview/email', methods=['POST', 'GET'])
def preview_email():
    """Preview an email template - properly sanitized"""
    recipient = request.form.get('recipient', '')
    subject = request.form.get('subject', '')
    body = request.form.get('body', '')
    
    # Proper sanitization
    recipient = escape_html(recipient)
    subject = escape_html(subject)
    body = escape_html(body)
    
    return EMAIL_TEMPLATE.format(
        recipient if recipient else 'recipient@example.com',
        subject if subject else 'No Subject',
        body if body else 'Email body goes here'
    )

# API endpoint for template info
@app.route('/api/template/<template_name>')
def get_template_info(template_name):
    """Get template information"""
    if template_name in TEMPLATES:
        return jsonify({
            'name': template_name,
            'description': TEMPLATES[template_name],
            'endpoint': '/preview/' + template_name
        })
    return jsonify({'error': 'Template not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
