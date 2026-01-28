# encoding=utf8
# CMS Admin Panel - Page Management System

from flask import Flask, request, Response, make_response, url_for, redirect, jsonify
from markupsafe import Markup
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

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# In-memory storage for pages (simulating database)
pages_storage = {}

# Pre-populate with some example pages
def init_pages():
    pages_storage['home'] = {
        'id': 'home',
        'title': 'Welcome to Our CMS',
        'slug': 'home',
        'status': 'published',
        'parent': None,
        'author': 'admin'
    }
    pages_storage['about'] = {
        'id': 'about', 
        'title': 'About Us',
        'slug': 'about',
        'status': 'published',
        'parent': 'home',
        'author': 'admin'
    }
    pages_storage['contact'] = {
        'id': 'contact',
        'title': 'Contact Information',
        'slug': 'contact', 
        'status': 'draft',
        'parent': 'home',
        'author': 'editor1'
    }

init_pages()

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/admin')
def admin_dashboard():
    return ADMIN_DASHBOARD

@app.route('/admin/pages')
def admin_pages_list():
    # Safely escape page titles for the list view
    pages_html = ""
    for page_id, page in pages_storage.items():
        escaped_title = cgi.escape(page['title'])
        pages_html += '<tr><td>{}</td><td>{}</td><td>{}</td><td><a href="/admin/pages/inspect/{}">Inspect</a> | <a href="/admin/pages/choose-parent/{}">Move</a></td></tr>'.format(
            escaped_title, page['status'], page['author'], page_id, page_id
        )
    return ADMIN_PAGES_LIST.format(pages_html)

@app.route('/admin/pages/add', methods=['GET', 'POST'])
def admin_add_page():
    if request.method == 'POST':
        title = request.form.get('title', '')
        slug = request.form.get('slug', '')
        parent = request.form.get('parent', '')
        
        if not title or not slug:
            return ADMIN_ADD_PAGE.format('<div class="error">Title and slug are required</div>', get_parent_options())
        
        page_id = str(uuid.uuid4())[:8]
        pages_storage[page_id] = {
            'id': page_id,
            'title': title,
            'slug': slug,
            'status': 'draft',
            'parent': parent if parent else None,
            'author': 'editor'
        }
        return redirect('/admin/pages')
    
    return ADMIN_ADD_PAGE.format('', get_parent_options())

def get_parent_options():
    options = '<option value="">-- No Parent --</option>'
    for page_id, page in pages_storage.items():
        options += '<option value="{}">{}</option>'.format(page_id, cgi.escape(page['title']))
    return options

def get_breadcrumbs(page_id):
    """Build breadcrumb path for a page - VULNERABLE: uses mark_safe equivalent"""
    breadcrumbs = []
    current_id = page_id
    
    while current_id and current_id in pages_storage:
        page = pages_storage[current_id]
        breadcrumbs.insert(0, page['title'])  # Using raw title without escaping
        current_id = page['parent']
    
    # Vulnerable: joining unescaped titles and marking as safe (similar to Wagtail CVE)
    # This mimics: mark_safe(' &rsaquo; '.join(breadcrumbs))
    return Markup(' &rsaquo; '.join(breadcrumbs))

@app.route('/admin/pages/choose-parent/<page_id>')
def choose_parent_view(page_id):
    """Choose parent page view - VULNERABLE to stored XSS via breadcrumbs"""
    if page_id not in pages_storage:
        return '<h1>Page not found</h1>', 404
    
    page = pages_storage[page_id]
    
    # Build parent options with breadcrumbs (VULNERABLE)
    parent_options = ''
    for pid, p in pages_storage.items():
        if pid != page_id:
            breadcrumb = get_breadcrumbs(pid)  # Vulnerable: unescaped breadcrumbs
            parent_options += '<div class="parent-option"><input type="radio" name="new_parent" value="{}"> <span class="breadcrumb">{}</span></div>'.format(pid, breadcrumb)
    
    # This page renders in the admin's browser context
    html_content = CHOOSE_PARENT_VIEW.format(
        cgi.escape(page['title']),
        parent_options
    )
    
    # Check for XSS execution via PhantomJS (simulates admin viewing the page)
    result = check_admin_xss(html_content, flags[0])
    
    response = make_response(html_content.replace('</body>', result + '</body>'))
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/admin/pages/inspect/<page_id>')
def inspect_view(page_id):
    """Inspect page view - VULNERABLE to stored XSS via title display"""
    if page_id not in pages_storage:
        return '<h1>Page not found</h1>', 404
    
    page = pages_storage[page_id]
    
    # Vulnerable: using mark_safe on page title (similar to Wagtail CVE)
    # This mimics: mark_safe('<h2>{}</h2>'.format(page['title']))
    title_html = Markup('<h2 class="page-title">{}</h2>'.format(page['title']))
    
    html_content = INSPECT_VIEW.format(
        title_html,
        cgi.escape(page['slug']),
        page['status'],
        page['author'],
        cgi.escape(str(page['parent'])) if page['parent'] else 'None'
    )
    
    # Check for XSS execution via PhantomJS (simulates admin viewing the page)
    result = check_admin_xss(html_content, flags[0])
    
    response = make_response(html_content.replace('</body>', result + '</body>'))
    response.headers["X-XSS-Protection"] = "0"
    return response

def check_admin_xss(page, flag):
    """Check if XSS payload executed when admin views the page"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print "Admin Page:"
        print page
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "XSS Result:"
        print result

    finally:
        os.unlink(fn)

    if result == 'XSS':
        return '<div class="alert alert-success"><strong>Security Alert!</strong> Unauthorized script execution detected. Flag: {}</div>'.format(flag)
    elif result:
        return '<div class="alert alert-warning">Script attempted: {} (expected: XSS)</div>'.format(cgi.escape(result))
    return ''

# Additional noise endpoints to make reconnaissance harder
@app.route('/admin/settings')
def admin_settings():
    return ADMIN_SETTINGS

@app.route('/admin/users')
def admin_users():
    return ADMIN_USERS

@app.route('/admin/documents')
def admin_documents():
    return ADMIN_DOCUMENTS

@app.route('/api/pages')
def api_pages():
    """API endpoint - properly escaped"""
    safe_pages = []
    for pid, p in pages_storage.items():
        safe_pages.append({
            'id': pid,
            'title': p['title'],  # JSON encoding handles escaping
            'slug': p['slug'],
            'status': p['status']
        })
    return jsonify({'pages': safe_pages})

@app.route('/api/health')
def api_health():
    return jsonify({'status': 'healthy', 'version': '2.15.1'})

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

if __name__ == '__main__':
    app.run(debug=True)
