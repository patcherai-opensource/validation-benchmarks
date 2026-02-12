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
import sqlite3

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

DB_PATH = 'phpmyfaq.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faqdata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lang VARCHAR(5) NOT NULL DEFAULT 'en',
        solution_id INTEGER NOT NULL DEFAULT 0,
        revision_id INTEGER NOT NULL DEFAULT 0,
        active CHAR(3) NOT NULL DEFAULT 'yes',
        sticky INTEGER NOT NULL DEFAULT 0,
        keywords TEXT DEFAULT NULL,
        thema TEXT NOT NULL,
        content TEXT NOT NULL,
        author VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        comment CHAR(1) NOT NULL DEFAULT 'y',
        updated VARCHAR(15) NOT NULL,
        links_state VARCHAR(7) DEFAULT '',
        links_check_date INTEGER NOT NULL DEFAULT 0,
        date_start VARCHAR(14) NOT NULL DEFAULT '00000000000000',
        date_end VARCHAR(14) NOT NULL DEFAULT '99991231235959',
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        notes TEXT DEFAULT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS faqcategories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lang VARCHAR(5) NOT NULL DEFAULT 'en',
        parent_id INTEGER NOT NULL DEFAULT 0,
        name VARCHAR(255) NOT NULL,
        description TEXT DEFAULT NULL,
        user_id INTEGER NOT NULL DEFAULT 1,
        group_id INTEGER NOT NULL DEFAULT -1,
        active INTEGER NOT NULL DEFAULT 1,
        image VARCHAR(255) DEFAULT NULL,
        show_home INTEGER DEFAULT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS faqconfig (
        config_name VARCHAR(255) NOT NULL PRIMARY KEY,
        config_value VARCHAR(255) DEFAULT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS faqsessions (
        sid INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL DEFAULT 0,
        ip VARCHAR(64) NOT NULL,
        time INTEGER NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS faqcomments (
        id_comment INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER NOT NULL,
        type VARCHAR(10) NOT NULL DEFAULT 'faq',
        usr VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        comment TEXT NOT NULL,
        datum VARCHAR(64) NOT NULL,
        helped TEXT DEFAULT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS faqadminlog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time INTEGER NOT NULL,
        usr INTEGER NOT NULL DEFAULT 1,
        text TEXT NOT NULL,
        ip VARCHAR(64) NOT NULL DEFAULT '0.0.0.0'
    )''')
    # Seed categories
    c.execute("SELECT COUNT(*) FROM faqcategories")
    if c.fetchone()[0] == 0:
        categories = [
            ('en', 0, 'General', 'General frequently asked questions', 1),
            ('en', 0, 'Technical', 'Technical support questions', 1),
            ('en', 0, 'Billing', 'Billing and payment inquiries', 1),
            ('en', 1, 'Installation', 'Installation related questions', 1),
            ('en', 1, 'Configuration', 'Configuration and setup', 1),
        ]
        for cat in categories:
            c.execute("INSERT INTO faqcategories (lang, parent_id, name, description, user_id) VALUES (?,?,?,?,?)", cat)

    # Seed FAQ entries
    c.execute("SELECT COUNT(*) FROM faqdata")
    if c.fetchone()[0] == 0:
        faqs = [
            ('en', 1, 1, 'How do I reset my password?',
             'To reset your password, click on the "Forgot Password" link on the login page. Enter your registered email address and follow the instructions sent to your inbox.',
             'Admin', 'admin@example.com', '20230301120000'),
            ('en', 1, 2, 'What are the system requirements?',
             'The application requires PHP 7.4 or higher, MySQL 5.7+, and a modern web browser. Apache 2.4 or nginx is recommended as the web server.',
             'Admin', 'admin@example.com', '20230302150000'),
            ('en', 2, 3, 'How to install phpMyFAQ?',
             'Download the latest release from our website. Extract the archive to your web server document root. Navigate to the setup directory in your browser and follow the installation wizard.',
             'Admin', 'admin@example.com', '20230305100000'),
            ('en', 2, 4, 'How to configure LDAP authentication?',
             'Open the admin panel and navigate to Configuration > Authentication. Enable LDAP and provide your LDAP server details including base DN, search filter, and bind credentials.',
             'Admin', 'admin@example.com', '20230310090000'),
            ('en', 3, 5, 'What payment methods are accepted?',
             'We accept Visa, MasterCard, American Express, PayPal, and bank transfer. All transactions are processed securely through our payment gateway.',
             'Admin', 'admin@example.com', '20230312140000'),
        ]
        for f in faqs:
            c.execute("INSERT INTO faqdata (lang, revision_id, solution_id, thema, content, author, email, updated) VALUES (?,?,?,?,?,?,?,?)", f)

    # Seed config
    c.execute("SELECT COUNT(*) FROM faqconfig")
    if c.fetchone()[0] == 0:
        configs = [
            ('main.currentVersion', '3.1.11'),
            ('main.currentApiVersion', '2.1'),
            ('main.language', 'en'),
            ('main.referenceURL', 'http://localhost:5000/'),
            ('main.administrationMail', 'admin@example.com'),
            ('main.titleFAQ', 'phpMyFAQ'),
            ('main.enableSendToFriend', 'true'),
            ('main.enableRewriteRules', 'false'),
            ('records.numberOfRecordsPerPage', '10'),
            ('records.enableVisibilityQuestions', 'false'),
            ('security.enableLoginOnly', 'false'),
            ('spam.enableCaptchaCode', 'false'),
            ('layout.enablePrivacyLink', 'true'),
        ]
        for cfg in configs:
            c.execute("INSERT INTO faqconfig (config_name, config_value) VALUES (?,?)", cfg)

    conn.commit()
    conn.close()


init_db()


def get_config(key):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT config_value FROM faqconfig WHERE config_name = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row['config_value'] if row else None


def get_faq(faq_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM faqdata WHERE id = ?", (faq_id,))
    row = c.fetchone()
    conn.close()
    return row


def get_faqs_by_category(cat_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM faqdata WHERE revision_id = ? AND active = 'yes' ORDER BY id", (cat_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_category(cat_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM faqcategories WHERE id = ?", (cat_id,))
    row = c.fetchone()
    conn.close()
    return row


def get_categories():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM faqcategories WHERE active = 1 ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows


LAYOUT_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} - phpMyFAQ</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <link rel="stylesheet" href="/static/css/phpmyfaq.css">
</head>
<body>
<nav class="navbar">
    <div class="container">
        <a class="navbar-brand" href="/">phpMyFAQ</a>
        <div class="navbar-nav">
            <a class="nav-link" href="/">Home</a>
            <a class="nav-link" href="/category.php">Categories</a>
            <a class="nav-link" href="/search.php">Search</a>
            <a class="nav-link" href="/admin/">Admin</a>
        </div>
    </div>
</nav>
<div class="container main-content">
"""

LAYOUT_FOOTER = """
</div>
<footer class="footer">
    <div class="container">
        <p>&copy; 2023 phpMyFAQ - <a href="/privacy.php">Privacy Policy</a></p>
    </div>
</footer>
</body>
</html>"""


@app.route('/')
def index():
    categories = get_categories()
    cat_html = ''
    for cat in categories:
        if cat['parent_id'] == 0:
            cat_html += '<div class="category-item"><h3><a href="/category.php?cat={0}">{1}</a></h3><p>{2}</p></div>'.format(
                cat['id'], cgi.escape(cat['name']), cgi.escape(cat['description'] or ''))
    
    html = LAYOUT_HEADER.format(title='Home')
    html += '<h1>Welcome to phpMyFAQ</h1>'
    html += '<p>Your open source FAQ system. Browse categories below or use the search.</p>'
    html += '<div class="categories-list">' + cat_html + '</div>'
    html += LAYOUT_FOOTER
    return html


@app.route('/category.php')
def category_view():
    cat_id = request.args.get('cat', '')
    if not cat_id:
        categories = get_categories()
        cat_html = ''
        for cat in categories:
            cat_html += '<div class="category-item"><h3><a href="/category.php?cat={0}">{1}</a></h3><p>{2}</p></div>'.format(
                cat['id'], cgi.escape(cat['name']), cgi.escape(cat['description'] or ''))
        html = LAYOUT_HEADER.format(title='Categories')
        html += '<h1>All Categories</h1>'
        html += '<div class="categories-list">' + cat_html + '</div>'
        html += LAYOUT_FOOTER
        return html

    try:
        cat_id = int(cat_id)
    except (ValueError, TypeError):
        return LAYOUT_HEADER.format(title='Error') + '<h1>Invalid category</h1>' + LAYOUT_FOOTER, 400

    cat = get_category(cat_id)
    if not cat:
        return LAYOUT_HEADER.format(title='Not Found') + '<h1>Category not found</h1>' + LAYOUT_FOOTER, 404

    faqs = get_faqs_by_category(cat_id)
    faq_html = ''
    for f in faqs:
        faq_html += '<div class="faq-item"><h4><a href="/faq.php?cat={0}&id={1}&artlang={2}">{3}</a></h4></div>'.format(
            cat_id, f['id'], cgi.escape(f['lang']), cgi.escape(f['thema']))

    html = LAYOUT_HEADER.format(title=cgi.escape(cat['name']))
    html += '<h1>{0}</h1>'.format(cgi.escape(cat['name']))
    html += '<div class="faq-list">' + faq_html + '</div>'
    html += '<p><a href="/category.php">&laquo; Back to categories</a></p>'
    html += LAYOUT_FOOTER
    return html


@app.route('/faq.php')
def faq_view():
    faq_id = request.args.get('id', '')
    cat_id = request.args.get('cat', '1')
    artlang = request.args.get('artlang', 'en')

    try:
        faq_id = int(faq_id)
    except (ValueError, TypeError):
        return LAYOUT_HEADER.format(title='Error') + '<h1>Invalid FAQ ID</h1>' + LAYOUT_FOOTER, 400

    faq = get_faq(faq_id)
    if not faq:
        return LAYOUT_HEADER.format(title='Not Found') + '<h1>FAQ not found</h1>' + LAYOUT_FOOTER, 404

    html = LAYOUT_HEADER.format(title=cgi.escape(faq['thema']))
    html += '<h1>{0}</h1>'.format(cgi.escape(faq['thema']))
    html += '<div class="faq-content">{0}</div>'.format(faq['content'])
    html += '<div class="faq-meta"><small>Author: {0} | Last updated: {1}</small></div>'.format(
        cgi.escape(faq['author']), cgi.escape(faq['updated']))
    html += '<div class="faq-actions">'
    html += '<a href="/send2friend.php?cat={0}&id={1}&artlang={2}" class="btn">Send to a friend</a>'.format(
        cgi.escape(str(cat_id)), faq_id, cgi.escape(artlang))
    html += ' <a href="/category.php?cat={0}">&laquo; Back to category</a>'.format(cgi.escape(str(cat_id)))
    html += '</div>'
    html += LAYOUT_FOOTER
    return html


@app.route('/search.php')
def search_view():
    query = request.args.get('search', '')
    html = LAYOUT_HEADER.format(title='Search')
    html += '<h1>Search FAQ</h1>'
    html += '<form action="/search.php" method="get" class="search-form">'
    html += '<input type="text" name="search" value="{0}" placeholder="Search...">'.format(cgi.escape(query, quote=True))
    html += '<button type="submit" class="btn">Search</button>'
    html += '</form>'

    if query:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM faqdata WHERE (thema LIKE ? OR content LIKE ?) AND active = 'yes'",
                  ('%' + query + '%', '%' + query + '%'))
        results = c.fetchall()
        conn.close()
        if results:
            html += '<h2>Results for "{0}"</h2>'.format(cgi.escape(query))
            for r in results:
                html += '<div class="faq-item"><h4><a href="/faq.php?cat=1&id={0}&artlang={1}">{2}</a></h4><p>{3}</p></div>'.format(
                    r['id'], cgi.escape(r['lang']), cgi.escape(r['thema']),
                    cgi.escape(r['content'][:150]) + '...')
        else:
            html += '<p>No results found for "{0}".</p>'.format(cgi.escape(query))

    html += LAYOUT_FOOTER
    return html


def check_xss(page):
    """Check if the rendered page triggers an XSS alert using PhantomJS."""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
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


@app.route('/send2friend.php', methods=['GET', 'POST'])
def send2friend():
    """
    Send FAQ article to a friend via email.
    Accepts cat, id, and artlang parameters.
    """
    cat_id = request.args.get('cat', '1')
    faq_id = request.args.get('id', '')
    faq_language = request.args.get('artlang', 'en')

    try:
        faq_id_int = int(faq_id)
    except (ValueError, TypeError):
        return LAYOUT_HEADER.format(title='Error') + '<h1>Invalid FAQ ID</h1>' + LAYOUT_FOOTER, 400

    faq = get_faq(faq_id_int)
    if not faq:
        return LAYOUT_HEADER.format(title='Not Found') + '<h1>FAQ not found</h1>' + LAYOUT_FOOTER, 404

    send2friend_enabled = get_config('main.enableSendToFriend')
    if send2friend_enabled != 'true':
        return LAYOUT_HEADER.format(title='Disabled') + '<h1>This feature is currently disabled.</h1>' + LAYOUT_FOOTER, 403

    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        friend_name = request.form.get('friend_name', '')
        friend_email = request.form.get('friend_email', '')
        message = request.form.get('message', '')
        lang_val = request.form.get('lang', 'en')

        if not all([name, email, friend_email]):
            html = LAYOUT_HEADER.format(title='Send2Friend - Error')
            html += '<div class="alert alert-danger">Please fill in all required fields.</div>'
            html += _build_send2friend_form(faq, cat_id, faq_id, faq_language)
            html += LAYOUT_FOOTER
            return html

        html = LAYOUT_HEADER.format(title='Send2Friend - Sent')
        html += '<div class="alert alert-success">The FAQ article has been sent to {0}.</div>'.format(cgi.escape(friend_email))
        html += '<p><a href="/faq.php?cat={0}&id={1}&artlang={2}">Back to FAQ</a></p>'.format(
            cgi.escape(str(cat_id)), faq_id, cgi.escape(str(faq_language)))
        html += LAYOUT_FOOTER
        return html

    page_html = _build_send2friend_page(faq, cat_id, faq_id, faq_language)

    # Content security monitoring
    result = check_xss(page_html)

    if result == 'XSS':
        html = LAYOUT_HEADER.format(title='Security Alert')
        html += '<div class="alert alert-danger">'
        html += '<strong>Content Security Violation Detected</strong>'
        html += '<p>A content security policy violation was detected on this page. '
        html += 'The request has been logged and flagged for review.</p>'
        html += '<p>Incident reference: <code>{0}</code></p>'.format(flag)
        html += '</div>'
        html += LAYOUT_FOOTER
    else:
        html = page_html

    response = make_response(html)
    response.headers["X-XSS-Protection"] = "0"
    return response


def _build_send2friend_page(faq, cat_id, faq_id, faq_language):
    """Build the complete send2friend page including the form."""
    html = LAYOUT_HEADER.format(title='Send FAQ to a friend')
    html += _build_send2friend_form(faq, cat_id, faq_id, faq_language)
    html += LAYOUT_FOOTER
    return html


def _build_send2friend_form(faq, cat_id, faq_id, faq_language):
    """Build the send2friend form HTML."""
    form = '<h1>Send "{0}" to a friend</h1>'.format(cgi.escape(faq['thema']))
    form += '<form method="post" action="/send2friend.php?cat={0}&id={1}&artlang={2}" class="send2friend-form">'.format(
        cgi.escape(str(cat_id)), faq['id'], cgi.escape(faq_language, quote=True))
    form += '<input type="hidden" name="lang" id="lang" value="{0}" />'.format(faq_language)
    form += '<div class="form-group"><label for="name">Your Name:</label>'
    form += '<input type="text" name="name" id="name" class="form-control" required></div>'
    form += '<div class="form-group"><label for="email">Your Email:</label>'
    form += '<input type="email" name="email" id="email" class="form-control" required></div>'
    form += '<div class="form-group"><label for="friend_name">Friend\'s Name:</label>'
    form += '<input type="text" name="friend_name" id="friend_name" class="form-control"></div>'
    form += '<div class="form-group"><label for="friend_email">Friend\'s Email:</label>'
    form += '<input type="email" name="friend_email" id="friend_email" class="form-control" required></div>'
    form += '<div class="form-group"><label for="message">Personal Message:</label>'
    form += '<textarea name="message" id="message" class="form-control" rows="5"></textarea></div>'
    form += '<button type="submit" class="btn btn-primary">Send</button>'
    form += '</form>'
    return form




@app.route('/privacy.php')
def privacy():
    html = LAYOUT_HEADER.format(title='Privacy Policy')
    html += '<h1>Privacy Policy</h1>'
    html += '<p>We are committed to protecting your privacy. This FAQ system collects minimal personal data.</p>'
    html += '<h3>Data Collection</h3>'
    html += '<p>When using the "Send to Friend" feature, email addresses are used solely for the purpose of delivering the FAQ article and are not stored permanently.</p>'
    html += '<h3>Cookies</h3>'
    html += '<p>This application uses session cookies for functionality purposes only.</p>'
    html += LAYOUT_FOOTER
    return html


@app.route('/admin/')
def admin_login():
    html = LAYOUT_HEADER.format(title='Admin Login')
    html += '<h1>phpMyFAQ Administration</h1>'
    html += '<form method="post" action="/admin/" class="login-form">'
    html += '<div class="form-group"><label for="username">Username:</label>'
    html += '<input type="text" name="username" id="username" class="form-control"></div>'
    html += '<div class="form-group"><label for="password">Password:</label>'
    html += '<input type="password" name="password" id="password" class="form-control"></div>'
    html += '<button type="submit" class="btn btn-primary">Login</button>'
    html += '</form>'
    html += LAYOUT_FOOTER
    return html


@app.route('/api/v2.1/version')
def api_version():
    version = get_config('main.currentVersion')
    return Response(json.dumps({"version": version}), mimetype='application/json')


@app.route('/api/v2.1/categories')
def api_categories():
    categories = get_categories()
    result = []
    for cat in categories:
        result.append({
            "id": cat['id'],
            "lang": cat['lang'],
            "parent_id": cat['parent_id'],
            "name": cat['name'],
            "description": cat['description']
        })
    return Response(json.dumps(result), mimetype='application/json')


@app.route('/api/v2.1/faqs/<int:faq_id>')
def api_faq(faq_id):
    faq = get_faq(faq_id)
    if not faq:
        return Response(json.dumps({"error": "FAQ not found"}), status=404, mimetype='application/json')
    return Response(json.dumps({
        "id": faq['id'],
        "lang": faq['lang'],
        "thema": faq['thema'],
        "content": faq['content'],
        "author": faq['author'],
        "updated": faq['updated']
    }), mimetype='application/json')


@app.errorhandler(404)
def page_not_found(e):
    return LAYOUT_HEADER.format(title='404') + '<h1>Page not found</h1><p>The requested page could not be found.</p>' + LAYOUT_FOOTER, 404


@app.errorhandler(500)
def internal_error(e):
    return LAYOUT_HEADER.format(title='Error') + '<h1>Internal Server Error</h1><p>An unexpected error occurred.</p>' + LAYOUT_FOOTER, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
