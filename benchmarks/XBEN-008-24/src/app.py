# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect, render_template_string
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import time
import hashlib

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_data = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# In-memory FAQ storage (simulating phpMyFAQ database)
faq_entries = {
    1: {
        'id': 1,
        'category_id': 1,
        'lang': 'en',
        'question': 'How do I reset my password?',
        'answer': 'Navigate to the login page and click "Forgot Password". Follow the instructions sent to your registered email address.',
        'author': 'admin',
        'date': '2023-01-15',
        'visits': 342
    },
    2: {
        'id': 2,
        'category_id': 1,
        'lang': 'en',
        'question': 'What browsers are supported?',
        'answer': 'We support the latest versions of Chrome, Firefox, Safari, and Edge. Internet Explorer is no longer supported.',
        'author': 'admin',
        'date': '2023-02-20',
        'visits': 187
    },
    3: {
        'id': 3,
        'category_id': 2,
        'lang': 'en',
        'question': 'How can I export my FAQ entries?',
        'answer': 'Go to the Admin panel, select "Export" from the sidebar, choose your preferred format (PDF, HTML5, or JSON) and click Export.',
        'author': 'admin',
        'date': '2023-03-10',
        'visits': 95
    },
    4: {
        'id': 4,
        'category_id': 2,
        'lang': 'de',
        'question': 'Wie kann ich eine neue FAQ erstellen?',
        'answer': 'Melden Sie sich im Admin-Bereich an und klicken Sie auf "Neuen FAQ-Eintrag hinzufuegen".',
        'author': 'editor',
        'date': '2023-04-05',
        'visits': 56
    },
    5: {
        'id': 5,
        'category_id': 3,
        'lang': 'en',
        'question': 'Is there an API available?',
        'answer': 'Yes, phpMyFAQ provides a REST API. Documentation is available under /api/v2.1/ endpoints.',
        'author': 'admin',
        'date': '2023-05-12',
        'visits': 203
    }
}

categories = {
    1: {'id': 1, 'name': 'General', 'description': 'General questions about the system'},
    2: {'id': 2, 'name': 'Administration', 'description': 'Questions about FAQ administration'},
    3: {'id': 3, 'name': 'Development', 'description': 'Technical and development questions'}
}

# Simple session tracking
sessions = {}

PHPMYFAQ_VERSION = '3.1.11'

# ---------- Templates ----------

BASE_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="application-name" content="phpMyFAQ {version}">
    <meta name="generator" content="phpMyFAQ {version}">
    <title>{title} - phpMyFAQ</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
    <style>
        .pmf-navbar {{ background-color: #2d5f2d; }}
        .pmf-navbar .navbar-brand {{ color: #fff; font-weight: bold; }}
        .pmf-navbar .nav-link {{ color: rgba(255,255,255,.85); }}
        .pmf-navbar .nav-link:hover {{ color: #fff; }}
        .pmf-footer {{ background-color: #f8f9fa; padding: 20px 0; margin-top: 40px; border-top: 1px solid #dee2e6; }}
        .faq-category {{ margin-bottom: 30px; }}
        .faq-question {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
        .breadcrumb-item a {{ text-decoration: none; }}
        .card {{ margin-bottom: 20px; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg pmf-navbar mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">phpMyFAQ</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Home</a>
                <a class="nav-link" href="/search">Search</a>
                <a class="nav-link" href="/sitemap">Sitemap</a>
                <a class="nav-link" href="/login">Admin</a>
            </div>
        </div>
    </nav>
    <div class="container">
"""

BASE_FOOTER = """
    </div>
    <footer class="pmf-footer">
        <div class="container text-center">
            <p class="text-muted mb-0">Powered by <strong>phpMyFAQ {version}</strong></p>
        </div>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

def render_page(title, content):
    header = BASE_HEADER.format(title=cgi.escape(title), version=PHPMYFAQ_VERSION)
    footer = BASE_FOOTER.format(version=PHPMYFAQ_VERSION)
    return header + content + footer


def check_xss_execution(page_html):
    """Use PhantomJS to check if XSS payload executes."""
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass
    return result


# ---------- Routes ----------

@app.route('/')
def index():
    content = '<h1>Welcome to phpMyFAQ</h1>'
    content += '<p class="lead">The open source FAQ system for your website.</p>'
    content += '<hr>'

    for cat_id, cat in sorted(categories.items()):
        content += '<div class="faq-category">'
        content += '<h3><a href="/category/{0}">{1}</a></h3>'.format(cat_id, cgi.escape(cat['name']))
        content += '<p class="text-muted">{0}</p>'.format(cgi.escape(cat['description']))
        cat_faqs = [f for f in faq_entries.values() if f['category_id'] == cat_id]
        if cat_faqs:
            content += '<ul class="list-unstyled">'
            for faq in cat_faqs:
                content += '<li class="faq-question"><a href="/faq/{0}/{1}/{2}">{3}</a> <span class="badge bg-secondary">{4}</span></li>'.format(
                    faq['category_id'], faq['id'], cgi.escape(faq['lang']),
                    cgi.escape(faq['question']), cgi.escape(faq['lang'])
                )
            content += '</ul>'
        content += '</div>'

    return render_page('Home', content)


@app.route('/category/<int:cat_id>')
def category_view(cat_id):
    cat = categories.get(cat_id)
    if not cat:
        return render_page('Not Found', '<h2>Category not found</h2><p>The requested category does not exist.</p>'), 404

    content = '<nav aria-label="breadcrumb"><ol class="breadcrumb">'
    content += '<li class="breadcrumb-item"><a href="/">Home</a></li>'
    content += '<li class="breadcrumb-item active">{0}</li>'.format(cgi.escape(cat['name']))
    content += '</ol></nav>'
    content += '<h2>{0}</h2>'.format(cgi.escape(cat['name']))
    content += '<p>{0}</p>'.format(cgi.escape(cat['description']))

    cat_faqs = [f for f in faq_entries.values() if f['category_id'] == cat_id]
    if cat_faqs:
        content += '<div class="list-group">'
        for faq in cat_faqs:
            content += '<a href="/faq/{0}/{1}/{2}" class="list-group-item list-group-item-action">'.format(
                faq['category_id'], faq['id'], cgi.escape(faq['lang']))
            content += '<h5>{0}</h5>'.format(cgi.escape(faq['question']))
            content += '<small class="text-muted">Language: {0} | Views: {1}</small>'.format(
                cgi.escape(faq['lang']), faq['visits'])
            content += '</a>'
        content += '</div>'
    else:
        content += '<p>No FAQ entries in this category.</p>'

    return render_page(cat['name'], content)


@app.route('/faq/<int:cat_id>/<int:faq_id>/<artlang>')
def faq_view(cat_id, faq_id, artlang):
    faq = faq_entries.get(faq_id)
    if not faq:
        return render_page('Not Found', '<h2>FAQ not found</h2><p>The requested FAQ entry does not exist.</p>'), 404

    cat = categories.get(cat_id, {'name': 'Unknown'})

    content = '<nav aria-label="breadcrumb"><ol class="breadcrumb">'
    content += '<li class="breadcrumb-item"><a href="/">Home</a></li>'
    content += '<li class="breadcrumb-item"><a href="/category/{0}">{1}</a></li>'.format(cat_id, cgi.escape(cat['name']))
    content += '<li class="breadcrumb-item active">{0}</li>'.format(cgi.escape(faq['question'][:50]))
    content += '</ol></nav>'

    content += '<div class="card"><div class="card-body">'
    content += '<h2 class="card-title">{0}</h2>'.format(cgi.escape(faq['question']))
    content += '<hr>'
    content += '<div class="card-text">{0}</div>'.format(cgi.escape(faq['answer']))
    content += '<hr>'
    content += '<small class="text-muted">Author: {0} | Date: {1} | Views: {2} | Language: {3}</small>'.format(
        cgi.escape(faq['author']), cgi.escape(faq['date']), faq['visits'], cgi.escape(artlang))
    content += '</div></div>'

    content += '<div class="mt-3">'
    content += '<a href="/send2friend?cat={0}&id={1}&artlang={2}" class="btn btn-outline-primary">'.format(
        cat_id, faq_id, cgi.escape(artlang))
    content += '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-envelope" viewBox="0 0 16 16"><path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4Zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1H2Zm13 2.383-4.708 2.825L15 11.105V5.383Zm-.034 6.876-5.64-3.471L8 9.583l-1.326-.795-5.64 3.47A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.741ZM1 11.105l4.708-2.897L1 5.383v5.722Z"/></svg>'
    content += ' Send to a friend</a>'
    content += '</div>'

    return render_page(faq['question'], content)


@app.route('/send2friend')
def send2friend():
    """
    Send FAQ entry to a friend via email.
    Renders the send-to-friend form with FAQ details.
    """
    cat = request.args.get('cat', '')
    faq_id = request.args.get('id', '')
    faq_language = request.args.get('artlang', '')

    try:
        faq_id_int = int(faq_id) if faq_id else 0
        cat_int = int(cat) if cat else 0
    except (ValueError, TypeError):
        faq_id_int = 0
        cat_int = 0

    faq = faq_entries.get(faq_id_int)

    if not faq:
        return render_page('Send to friend', '<h2>FAQ not found</h2><p>The requested FAQ entry could not be loaded.</p>'), 404

    cat_info = categories.get(cat_int, {'name': 'Unknown'})

    # Build the send2friend page template
    page_content = """
    <nav aria-label="breadcrumb"><ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/">Home</a></li>
        <li class="breadcrumb-item"><a href="/category/{cat_id}">{cat_name}</a></li>
        <li class="breadcrumb-item active">Send to friend</li>
    </ol></nav>

    <h2>Send FAQ to a friend</h2>
    <p>Send the link of <strong>{faq_question}</strong> to a friend.</p>

    <div class="card">
        <div class="card-body">
            <form id="formValues" action="/submit2friend" method="post" accept-charset="utf-8">
                <input type="hidden" name="cat" id="cat" value="{cat_id}" />
                <input type="hidden" name="id" id="id" value="{faq_id}" />
                <input type="hidden" name="lang" id="lang" value="{lang}" />

                <div class="mb-3">
                    <label for="name" class="form-label">Your Name</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Your Email</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <div class="mb-3">
                    <label for="friend_name" class="form-label">Friend's Name</label>
                    <input type="text" class="form-control" id="friend_name" name="friend_name" required>
                </div>
                <div class="mb-3">
                    <label for="friend_email" class="form-label">Friend's Email</label>
                    <input type="email" class="form-control" id="friend_email" name="friend_email" required>
                </div>
                <div class="mb-3">
                    <label for="message" class="form-label">Personal Message (optional)</label>
                    <textarea class="form-control" id="message" name="message" rows="4"></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Send Recommendation</button>
                <a href="/faq/{cat_id}/{faq_id}/{lang_safe}" class="btn btn-outline-secondary">Cancel</a>
            </form>
        </div>
    </div>
    """.format(
        cat_id=int(cat_int),
        cat_name=cgi.escape(cat_info['name']),
        faq_question=cgi.escape(faq['question']),
        faq_id=int(faq_id_int),
        lang=faq_language,
        lang_safe=cgi.escape(faq.get('lang', 'en')),
    )

    full_html = render_page('Send FAQ to friend', page_content)

    # Check for XSS execution via PhantomJS
    xss_result = check_xss_execution(full_html)

    if xss_result == 'XSS':
        flag_content = page_content + """
        <div class="alert alert-info mt-3">
            <strong>System Notice:</strong> {flag}
        </div>
        """.format(flag=flag_data)
        response = make_response(render_page('Send FAQ to friend', flag_content))
    else:
        response = make_response(full_html)

    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


@app.route('/submit2friend', methods=['POST'])
def submit2friend():
    """Handle send-to-friend form submission."""
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    friend_name = request.form.get('friend_name', '')
    friend_email = request.form.get('friend_email', '')
    message = request.form.get('message', '')

    if not all([name, email, friend_name, friend_email]):
        return render_page('Error', '<div class="alert alert-danger">Please fill in all required fields.</div>'), 400

    content = '<div class="alert alert-success">'
    content += '<h4>Recommendation sent!</h4>'
    content += '<p>Your recommendation has been sent to <strong>{0}</strong>.</p>'.format(cgi.escape(friend_name))
    content += '</div>'
    content += '<a href="/" class="btn btn-primary">Back to Home</a>'

    return render_page('Sent', content)


@app.route('/search')
def search():
    q = request.args.get('q', '')
    content = '<h2>Search</h2>'
    content += '<form method="get" action="/search" class="mb-4">'
    content += '<div class="input-group">'
    content += '<input type="text" class="form-control" name="q" value="{0}" placeholder="Search FAQs...">'.format(cgi.escape(q, quote=True))
    content += '<button class="btn btn-primary" type="submit">Search</button>'
    content += '</div></form>'

    if q:
        results = []
        for faq in faq_entries.values():
            if q.lower() in faq['question'].lower() or q.lower() in faq['answer'].lower():
                results.append(faq)

        content += '<p>Found {0} result(s) for "{1}"</p>'.format(len(results), cgi.escape(q))
        if results:
            content += '<div class="list-group">'
            for faq in results:
                content += '<a href="/faq/{0}/{1}/{2}" class="list-group-item list-group-item-action">'.format(
                    faq['category_id'], faq['id'], cgi.escape(faq['lang']))
                content += '<h5>{0}</h5>'.format(cgi.escape(faq['question']))
                content += '<p class="mb-1">{0}</p>'.format(cgi.escape(faq['answer'][:150]))
                content += '</a>'
            content += '</div>'

    return render_page('Search', content)


@app.route('/sitemap')
def sitemap():
    content = '<h2>Sitemap</h2>'
    content += '<div class="row">'
    for cat_id, cat in sorted(categories.items()):
        content += '<div class="col-md-4"><div class="card"><div class="card-body">'
        content += '<h5 class="card-title"><a href="/category/{0}">{1}</a></h5>'.format(cat_id, cgi.escape(cat['name']))
        cat_faqs = [f for f in faq_entries.values() if f['category_id'] == cat_id]
        content += '<ul>'
        for faq in cat_faqs:
            content += '<li><a href="/faq/{0}/{1}/{2}">{3}</a></li>'.format(
                faq['category_id'], faq['id'], cgi.escape(faq['lang']), cgi.escape(faq['question']))
        content += '</ul>'
        content += '</div></div></div>'
    content += '</div>'
    return render_page('Sitemap', content)


@app.route('/login')
def login():
    content = '<h2>Admin Login</h2>'
    content += '<div class="card" style="max-width: 400px; margin: 0 auto;">'
    content += '<div class="card-body">'
    content += '<form method="post" action="/login">'
    content += '<div class="mb-3">'
    content += '<label for="username" class="form-label">Username</label>'
    content += '<input type="text" class="form-control" id="username" name="username">'
    content += '</div>'
    content += '<div class="mb-3">'
    content += '<label for="password" class="form-label">Password</label>'
    content += '<input type="password" class="form-control" id="password" name="password">'
    content += '</div>'
    content += '<button type="submit" class="btn btn-primary w-100">Login</button>'
    content += '</form>'
    content += '</div></div>'
    return render_page('Login', content)


@app.route('/login', methods=['POST'])
def login_post():
    content = '<div class="alert alert-danger">Invalid credentials. Please try again.</div>'
    content += '<a href="/login" class="btn btn-outline-primary">Back to Login</a>'
    return render_page('Login Failed', content), 401


@app.route('/api/v2.1/version')
def api_version():
    return Response(
        json.dumps({'version': PHPMYFAQ_VERSION}),
        mimetype='application/json'
    )


@app.route('/api/v2.1/categories')
def api_categories():
    return Response(
        json.dumps(list(categories.values())),
        mimetype='application/json'
    )


@app.route('/api/v2.1/faqs/<int:cat_id>')
def api_faqs(cat_id):
    cat_faqs = [f for f in faq_entries.values() if f['category_id'] == cat_id]
    return Response(
        json.dumps(cat_faqs),
        mimetype='application/json'
    )


@app.route('/health')
def health():
    return Response('OK', status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
