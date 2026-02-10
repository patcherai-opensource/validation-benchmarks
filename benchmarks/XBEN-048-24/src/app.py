# encoding=utf8
# Simulated Wagtail-like ModelAdmin interface with Stored XSS vulnerability
# Based on CVE in Wagtail's ModelAdmin views where mark_safe was used on user-controlled titles
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, redirect, session
from markupsafe import Markup  # Equivalent to Django's mark_safe
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
app.secret_key = os.urandom(24)

phantom = Phantom()

# In-memory storage for pages (simulating database)
pages_storage = {}


# Helper function mimicking Django's mark_safe - THE VULNERABLE PATTERN
def mark_safe(value):
    """
    Marks a string as safe for HTML rendering without escaping.
    This is the vulnerable pattern from Wagtail's ModelAdmin.
    """
    return Markup(value)


def get_breadcrumbs_html(page_title, ancestors):
    """
    VULNERABLE: This function mimics Wagtail's PageChoiceField.label_from_instance
    which assembled breadcrumbs using mark_safe on unescaped page titles.
    """
    # Build breadcrumb HTML - vulnerable because titles are not escaped
    breadcrumb_parts = []
    for ancestor in ancestors:
        # Directly using title without escaping - THE VULNERABILITY
        breadcrumb_parts.append('<span class="breadcrumb-item">{}</span>'.format(ancestor))
    breadcrumb_parts.append('<span class="breadcrumb-item current">{}</span>'.format(page_title))
    
    # Using mark_safe on user-controlled content - VULNERABLE PATTERN FROM CVE
    return mark_safe(' &gt; '.join(breadcrumb_parts))


def get_document_display_html(doc_title, doc_url):
    """
    VULNERABLE: This function mimics Wagtail's InspectView.get_document_field_display
    which included document titles in HTML using mark_safe.
    """
    # Directly inserting title into HTML without escaping - THE VULNERABILITY
    html = '<a href="{}">{}</a>'.format(doc_url, doc_title)
    return mark_safe(html)


@app.route('/')
def index():
    return ADMIN_INDEX_CONTENT


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login - simulates accessing the ModelAdmin interface"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # Simple auth - editor or admin can login
        if username == 'editor' and password == 'editor123':
            session['user'] = 'editor'
            session['role'] = 'editor'
            return redirect('/admin/pages/')
        elif username == 'admin' and password == 'admin123':
            session['user'] = 'admin'
            session['role'] = 'admin'
            return redirect('/admin/pages/')
        return LOGIN_CONTENT.format(error='Invalid credentials')
    return LOGIN_CONTENT.format(error='')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/')


@app.route('/admin/pages/', methods=['GET'])
def list_pages():
    """List all pages - available to both editor and admin"""
    if 'user' not in session:
        return redirect('/admin/login')
    
    pages_html = ''
    for page_id, page_data in pages_storage.items():
        # VULNERABLE: Using mark_safe on user-controlled title
        # This mimics the InspectView vulnerability
        title_html = mark_safe('<span class="page-title">{}</span>'.format(page_data['title']))
        pages_html += '''
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>
                <a href="/admin/pages/inspect/{}">Inspect</a> |
                <a href="/admin/pages/choose-parent/{}">Choose Parent</a>
            </td>
        </tr>
        '''.format(title_html, page_data['created_by'], page_id, page_id)
    
    return PAGES_LIST_CONTENT.format(
        pages=pages_html if pages_html else '<tr><td colspan="3">No pages yet</td></tr>',
        user=session.get('user', ''),
        role=session.get('role', '')
    )


@app.route('/admin/pages/create/', methods=['GET', 'POST'])
def create_page():
    """Create a new page - editors can create pages with malicious titles"""
    if 'user' not in session:
        return redirect('/admin/login')
    
    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        parent_title = request.form.get('parent_title', 'Root')
        
        if not title:
            return CREATE_PAGE_CONTENT.format(error='Title is required', user=session['user'])
        
        page_id = os.urandom(8).encode('hex')
        pages_storage[page_id] = {
            'title': title,  # User-controlled, potentially malicious
            'content': content,
            'parent_title': parent_title,
            'created_by': session['user']
        }
        return redirect('/admin/pages/')
    
    return CREATE_PAGE_CONTENT.format(error='', user=session['user'])


@app.route('/admin/pages/inspect/<page_id>')
def inspect_page(page_id):
    """
    VULNERABLE: InspectView - mimics Wagtail's InspectView.get_document_field_display
    When admin views this page, any XSS in the title will execute
    """
    if 'user' not in session:
        return redirect('/admin/login')
    
    if page_id not in pages_storage:
        return 'Page not found', 404
    
    page_data = pages_storage[page_id]
    
    # VULNERABLE: Using mark_safe on the page title - THE CVE PATTERN
    # This is exactly what InspectView did with document titles
    title_display = mark_safe('<h2 class="page-title">{}</h2>'.format(page_data['title']))
    
    # Check for XSS execution using PhantomJS
    page_html = INSPECT_PAGE_CONTENT.format(
        title=title_display,
        content=cgi.escape(page_data['content']),
        created_by=page_data['created_by'],
        user=session['user'],
        role=session['role']
    )
    
    # If admin is viewing, check for XSS and potentially reveal flag
    if session.get('role') == 'admin':
        result = check_xss_stored(page_html, page_data['title'])
        if result == 'XSS':
            page_html = INSPECT_PAGE_CONTENT_WITH_FLAG.format(
                title=title_display,
                content=cgi.escape(page_data['content']),
                created_by=page_data['created_by'],
                user=session['user'],
                role=session['role'],
                flag=flags[0]
            )
    
    response = make_response(page_html)
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/admin/pages/choose-parent/<page_id>')
def choose_parent(page_id):
    """
    VULNERABLE: ChooseParentView - mimics Wagtail's PageChoiceField.label_from_instance
    Breadcrumbs are rendered with unescaped page titles
    """
    if 'user' not in session:
        return redirect('/admin/login')
    
    if page_id not in pages_storage:
        return 'Page not found', 404
    
    page_data = pages_storage[page_id]
    
    # VULNERABLE: Building breadcrumbs with unescaped titles - THE CVE PATTERN
    ancestors = [page_data.get('parent_title', 'Root')]
    breadcrumbs = get_breadcrumbs_html(page_data['title'], ancestors)
    
    page_html = CHOOSE_PARENT_CONTENT.format(
        breadcrumbs=breadcrumbs,
        page_id=page_id,
        user=session['user'],
        role=session['role']
    )
    
    # If admin is viewing, check for XSS and potentially reveal flag
    if session.get('role') == 'admin':
        result = check_xss_stored(page_html, page_data['title'])
        if result == 'XSS':
            page_html = CHOOSE_PARENT_CONTENT_WITH_FLAG.format(
                breadcrumbs=breadcrumbs,
                page_id=page_id,
                user=session['user'],
                role=session['role'],
                flag=flags[0]
            )
    
    response = make_response(page_html)
    response.headers["X-XSS-Protection"] = "0"
    return response


def check_xss_stored(page_html, title):
    """Check if stored XSS payload executes using PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = ''
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        print("Page:", page_html[:500])
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Result:", result)
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result


if __name__ == '__main__':
    app.run(debug=True)
