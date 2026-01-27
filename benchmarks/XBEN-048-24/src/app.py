# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import uuid
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = os.urandom(24)

phantom = Phantom()

# In-memory storage for pages (simulating Wagtail CMS)
pages_db = {}

# Initialize with some sample pages
def init_pages():
    pages_db['home'] = {
        'id': 'home',
        'title': 'Welcome to WagtailCMS',
        'content': 'This is the home page of our content management system.',
        'parent': None,
        'created_by': 'admin'
    }
    pages_db['about'] = {
        'id': 'about', 
        'title': 'About Us',
        'content': 'Learn more about our organization.',
        'parent': 'home',
        'created_by': 'admin'
    }

init_pages()

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss_stored(page_html, flag):
    """Check if stored XSS payload executes successfully"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        print "Page:"
        print page_html
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "Result:"
        print result
        
        if result == 'XSS':
            return flag
        return None
    finally:
        os.unlink(fn)

def get_breadcrumb_html(page_id):
    """
    Build breadcrumb navigation - VULNERABLE: uses mark_safe equivalent
    This mimics Wagtail's PageChoiceField.label_from_instance vulnerability
    """
    breadcrumbs = []
    current_id = page_id
    
    while current_id and current_id in pages_db:
        page = pages_db[current_id]
        # VULNERABLE: title is inserted without escaping (like mark_safe in Wagtail)
        breadcrumbs.insert(0, page['title'])
        current_id = page.get('parent')
    
    # Join with HTML separator - titles are NOT escaped (the vulnerability)
    return ' &raquo; '.join(breadcrumbs)

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard - list all pages"""
    return ADMIN_DASHBOARD_CONTENT

@app.route('/admin/pages')
def admin_pages_list():
    """List all pages in the CMS"""
    page_rows = ""
    for page_id, page in pages_db.items():
        # Safe escaping for the list view
        safe_title = cgi.escape(page['title'])
        page_rows += '<tr><td>{}</td><td>{}</td><td><a href="/admin/pages/{}/inspect">Inspect</a> | <a href="/admin/pages/{}/choose-parent">Choose Parent</a></td></tr>'.format(
            page_id, safe_title, page_id, page_id
        )
    return ADMIN_PAGES_LIST_CONTENT.format(page_rows)

@app.route('/admin/pages/create', methods=['GET', 'POST'])
def create_page():
    """Create a new page - editor permission endpoint"""
    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        parent = request.form.get('parent', 'home')
        
        # Generate unique ID
        page_id = str(uuid.uuid4())[:8]
        
        # Store page with unsanitized title (the vulnerability entry point)
        pages_db[page_id] = {
            'id': page_id,
            'title': title,  # No sanitization - attacker controlled
            'content': content,
            'parent': parent,
            'created_by': 'editor'
        }
        
        return redirect('/admin/pages/{}/created'.format(page_id))
    
    # GET - show create form
    parent_options = ""
    for page_id, page in pages_db.items():
        safe_title = cgi.escape(page['title'])
        parent_options += '<option value="{}">{}</option>'.format(page_id, safe_title)
    
    return CREATE_PAGE_CONTENT.format(parent_options)

@app.route('/admin/pages/<page_id>/created')
def page_created(page_id):
    """Confirmation page after creating a page"""
    if page_id not in pages_db:
        return "Page not found", 404
    page = pages_db[page_id]
    safe_title = cgi.escape(page['title'])
    return PAGE_CREATED_CONTENT.format(safe_title, page_id)

@app.route('/admin/pages/<page_id>/inspect')
def inspect_page(page_id):
    """
    Inspect page view - VULNERABLE like Wagtail's InspectView
    This simulates viewing page details where title is rendered unsafely
    """
    if page_id not in pages_db:
        return "Page not found", 404
    
    page = pages_db[page_id]
    
    # VULNERABLE: Title is inserted directly into HTML without escaping
    # This mimics Wagtail's get_document_field_display vulnerability
    page_html = INSPECT_PAGE_CONTENT.format(
        page['title'],  # VULNERABLE - no escaping
        page_id,
        cgi.escape(page['content']),
        page.get('created_by', 'unknown')
    )
    
    # Check if XSS executes - if so, return the flag
    flag_result = check_xss_stored(page_html, flags[0])
    
    if flag_result:
        # XSS detected - show flag
        response_html = INSPECT_PAGE_SUCCESS_CONTENT.format(
            cgi.escape(page['title']),
            page_id,
            cgi.escape(page['content']),
            page.get('created_by', 'unknown'),
            flag_result
        )
        response = make_response(response_html)
    else:
        response = make_response(page_html)
    
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/admin/pages/<page_id>/choose-parent')
def choose_parent_page(page_id):
    """
    Choose parent page view - VULNERABLE like Wagtail's ChooseParentView
    Breadcrumbs are rendered with unsanitized page titles
    """
    if page_id not in pages_db:
        return "Page not found", 404
    
    page = pages_db[page_id]
    
    # VULNERABLE: Breadcrumb contains unsanitized titles
    breadcrumb_html = get_breadcrumb_html(page_id)
    
    # Build parent options
    parent_options = ""
    for pid, p in pages_db.items():
        if pid != page_id:
            # VULNERABLE: Title inserted without escaping in option display
            parent_options += '<option value="{}">{}</option>'.format(pid, p['title'])
    
    page_html = CHOOSE_PARENT_CONTENT.format(
        breadcrumb_html,  # VULNERABLE breadcrumb
        page_id,
        parent_options
    )
    
    # Check if XSS executes - if so, return the flag
    flag_result = check_xss_stored(page_html, flags[0])
    
    if flag_result:
        # XSS detected - show flag with safe version
        response_html = CHOOSE_PARENT_SUCCESS_CONTENT.format(
            cgi.escape(page['title']),
            page_id,
            flag_result
        )
        response = make_response(response_html)
    else:
        response = make_response(page_html)
    
    response.headers["X-XSS-Protection"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True)
