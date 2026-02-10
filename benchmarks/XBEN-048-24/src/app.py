# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for, session
from markupsafe import Markup
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import hashlib
from datetime import datetime

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.secret_key = os.urandom(24)

PAGES_FILE = 'pages.json'

def load_pages():
    if os.path.exists(PAGES_FILE):
        try:
            with open(PAGES_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_pages(pages):
    with open(PAGES_FILE, 'w') as f:
        json.dump(pages, f)

def get_breadcrumb_html(page):
    """
    Build breadcrumb HTML for page hierarchy.
    This mimics Wagtail's PageChoiceField.label_from_instance which
    concatenated page titles unsafely using mark_safe.
    """
    ancestors = page.get('ancestors', [])
    parts = []
    for ancestor in ancestors:
        parts.append('<span class="breadcrumb-item">{}</span>'.format(ancestor))
    parts.append('<span class="breadcrumb-item current">{}</span>'.format(page['title']))
    return Markup(' &raquo; '.join(parts))

def check_xss_in_page(html_content):
    """Check if XSS executes via PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = None
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PageCraft CMS</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header">
        <h1>PageCraft CMS</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Admin Panel</a>
        </nav>
    </div>
    <div class="container">
        <h2>Welcome to PageCraft</h2>
        <p>A simple content management system for your pages.</p>
        <div class="actions">
            <a href="/admin/" class="btn">Go to Admin Panel</a>
        </div>
    </div>
</body>
</html>'''

@app.route('/admin/')
def admin_index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Admin - PageCraft CMS</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header admin-header">
        <h1>PageCraft Admin</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/pages/">Pages</a>
            <a href="/admin/pages/create/">New Page</a>
        </nav>
    </div>
    <div class="container">
        <h2>Admin Dashboard</h2>
        <div class="admin-menu">
            <div class="menu-item">
                <a href="/admin/pages/">
                    <h3>Pages</h3>
                    <p>Manage your site pages</p>
                </a>
            </div>
            <div class="menu-item">
                <a href="/admin/pages/create/">
                    <h3>Create New Page</h3>
                    <p>Add a new page to your site</p>
                </a>
            </div>
            <div class="menu-item">
                <a href="/admin/pages/choose-parent/">
                    <h3>Choose Parent Page</h3>
                    <p>View page hierarchy</p>
                </a>
            </div>
        </div>
    </div>
</body>
</html>'''

@app.route('/admin/pages/')
def admin_pages_list():
    pages = load_pages()
    page_rows = ""
    for page in pages:
        page_rows += '''<tr>
            <td>{}</td>
            <td><a href="/admin/pages/inspect/{}/">{}</a></td>
            <td>{}</td>
            <td>
                <a href="/admin/pages/inspect/{}/" class="btn btn-sm">Inspect</a>
            </td>
        </tr>'''.format(page['id'], page['id'], cgi.escape(page['title']), page.get('created_at', 'N/A'), page['id'])
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Pages - PageCraft Admin</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header admin-header">
        <h1>PageCraft Admin</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/pages/">Pages</a>
            <a href="/admin/pages/create/">New Page</a>
        </nav>
    </div>
    <div class="container">
        <h2>Pages</h2>
        <p><a href="/admin/pages/create/" class="btn">Create New Page</a></p>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {}
            </tbody>
        </table>
    </div>
</body>
</html>'''.format(page_rows)

@app.route('/admin/pages/create/', methods=['GET', 'POST'])
def admin_pages_create():
    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        parent_id = request.form.get('parent_id', '')
        
        if not title:
            return '''<!DOCTYPE html>
<html>
<head>
    <title>Create Page - PageCraft Admin</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header admin-header">
        <h1>PageCraft Admin</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/pages/">Pages</a>
        </nav>
    </div>
    <div class="container">
        <h2>Create New Page</h2>
        <div class="error">Title is required</div>
        <form method="post">
            <div class="form-group">
                <label>Title:</label>
                <input type="text" name="title" value="">
            </div>
            <div class="form-group">
                <label>Content:</label>
                <textarea name="content" rows="10"></textarea>
            </div>
            <div class="form-group">
                <label>Parent Page ID (optional):</label>
                <input type="text" name="parent_id" value="">
            </div>
            <button type="submit" class="btn">Create Page</button>
        </form>
    </div>
</body>
</html>'''
        
        pages = load_pages()
        
        ancestors = []
        if parent_id:
            for p in pages:
                if str(p['id']) == str(parent_id):
                    ancestors = p.get('ancestors', []) + [p['title']]
                    break
        
        new_page = {
            'id': len(pages) + 1,
            'title': title,
            'content': content,
            'parent_id': parent_id if parent_id else None,
            'ancestors': ancestors,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        pages.append(new_page)
        save_pages(pages)
        
        return redirect('/admin/pages/')
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Create Page - PageCraft Admin</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header admin-header">
        <h1>PageCraft Admin</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/pages/">Pages</a>
        </nav>
    </div>
    <div class="container">
        <h2>Create New Page</h2>
        <form method="post">
            <div class="form-group">
                <label>Title:</label>
                <input type="text" name="title" value="">
            </div>
            <div class="form-group">
                <label>Content:</label>
                <textarea name="content" rows="10"></textarea>
            </div>
            <div class="form-group">
                <label>Parent Page ID (optional):</label>
                <input type="text" name="parent_id" value="">
            </div>
            <button type="submit" class="btn">Create Page</button>
        </form>
    </div>
</body>
</html>'''

@app.route('/admin/pages/inspect/<int:page_id>/')
def admin_pages_inspect(page_id):
    """
    Inspect a page - mimics Wagtail's InspectView.
    The vulnerability: page title is rendered using Markup (mark_safe equivalent)
    without proper escaping, similar to the Wagtail CVE.
    """
    pages = load_pages()
    page = None
    for p in pages:
        if p['id'] == page_id:
            page = p
            break
    
    if not page:
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Page Not Found - PageCraft Admin</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header admin-header">
        <h1>PageCraft Admin</h1>
    </div>
    <div class="container">
        <h2>Page Not Found</h2>
        <p>The requested page does not exist.</p>
        <a href="/admin/pages/" class="btn">Back to Pages</a>
    </div>
</body>
</html>''', 404
    
    breadcrumb = get_breadcrumb_html(page)
    
    title_display = Markup('<h3 class="page-title">{}</h3>'.format(page['title']))
    
    inspect_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Inspect Page - PageCraft Admin</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header admin-header">
        <h1>PageCraft Admin</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/pages/">Pages</a>
        </nav>
    </div>
    <div class="container">
        <h2>Inspect Page</h2>
        <div class="breadcrumb">
            {}
        </div>
        <div class="inspect-content">
            {}
            <table class="inspect-table">
                <tr>
                    <th>ID:</th>
                    <td>{}</td>
                </tr>
                <tr>
                    <th>Title:</th>
                    <td>{}</td>
                </tr>
                <tr>
                    <th>Content:</th>
                    <td>{}</td>
                </tr>
                <tr>
                    <th>Created:</th>
                    <td>{}</td>
                </tr>
            </table>
        </div>
        <a href="/admin/pages/" class="btn">Back to Pages</a>
    </div>
</body>
</html>'''.format(
        breadcrumb,
        title_display,
        page['id'],
        page['title'],
        cgi.escape(page.get('content', '')),
        page.get('created_at', 'N/A')
    )
    
    result = check_xss_in_page(inspect_html)
    
    if result == 'XSS':
        inspect_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Inspect Page - PageCraft Admin</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header admin-header">
        <h1>PageCraft Admin</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/pages/">Pages</a>
        </nav>
    </div>
    <div class="container">
        <h2>Inspect Page</h2>
        <div class="breadcrumb">
            {}
        </div>
        <div class="inspect-content">
            {}
            <table class="inspect-table">
                <tr>
                    <th>ID:</th>
                    <td>{}</td>
                </tr>
                <tr>
                    <th>Title:</th>
                    <td>{}</td>
                </tr>
                <tr>
                    <th>Content:</th>
                    <td>{}</td>
                </tr>
                <tr>
                    <th>Created:</th>
                    <td>{}</td>
                </tr>
            </table>
        </div>
        <div class="success-message">
            <p>Security Check Passed! Here is your flag: {}</p>
        </div>
        <a href="/admin/pages/" class="btn">Back to Pages</a>
    </div>
</body>
</html>'''.format(
            breadcrumb,
            title_display,
            page['id'],
            page['title'],
            cgi.escape(page.get('content', '')),
            page.get('created_at', 'N/A'),
            flag
        )
    
    response = make_response(inspect_html)
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/admin/pages/choose-parent/')
def admin_choose_parent():
    """
    Choose parent page view - mimics Wagtail's ChooseParentView.
    This view renders page titles in breadcrumbs unsafely.
    """
    pages = load_pages()
    
    page_items = ""
    for page in pages:
        breadcrumb = get_breadcrumb_html(page)
        page_items += '''<div class="parent-option">
            <input type="radio" name="parent" value="{}" id="page-{}">
            <label for="page-{}">{}</label>
        </div>'''.format(page['id'], page['id'], page['id'], breadcrumb)
    
    choose_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Choose Parent Page - PageCraft Admin</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header admin-header">
        <h1>PageCraft Admin</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/pages/">Pages</a>
        </nav>
    </div>
    <div class="container">
        <h2>Choose a Parent Page</h2>
        <p>Select a page to use as the parent for your new page.</p>
        <form method="post" action="/admin/pages/create/">
            <div class="parent-list">
                {}
            </div>
            <button type="submit" class="btn">Select</button>
        </form>
        <a href="/admin/pages/" class="btn btn-secondary">Cancel</a>
    </div>
</body>
</html>'''.format(page_items)
    
    result = check_xss_in_page(choose_html)
    
    if result == 'XSS':
        choose_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Choose Parent Page - PageCraft Admin</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header admin-header">
        <h1>PageCraft Admin</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Dashboard</a>
            <a href="/admin/pages/">Pages</a>
        </nav>
    </div>
    <div class="container">
        <h2>Choose a Parent Page</h2>
        <div class="parent-list">
            {}
        </div>
        <div class="success-message">
            <p>Security Check Passed! Here is your flag: {}</p>
        </div>
        <a href="/admin/pages/" class="btn">Back to Pages</a>
    </div>
</body>
</html>'''.format(page_items, flag)
    
    response = make_response(choose_html)
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.errorhandler(404)
def not_found(e):
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Not Found - PageCraft CMS</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header">
        <h1>PageCraft CMS</h1>
    </div>
    <div class="container">
        <h2>Page Not Found</h2>
        <p>The requested page could not be found.</p>
        <a href="/" class="btn">Go Home</a>
    </div>
</body>
</html>''', 404

@app.errorhandler(500)
def internal_error(e):
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Error - PageCraft CMS</title>
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css">
</head>
<body>
    <div class="header">
        <h1>PageCraft CMS</h1>
    </div>
    <div class="container">
        <h2>Internal Server Error</h2>
        <p>An error occurred while processing your request.</p>
        <a href="/" class="btn">Go Home</a>
    </div>
</body>
</html>''', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
