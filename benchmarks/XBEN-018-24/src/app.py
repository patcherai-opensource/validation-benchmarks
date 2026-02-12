# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
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

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# ---- Simulated FAQ data (mirrors phpMyFAQ structure) ----
FAQ_CATEGORIES = {
    1: {"name": "General", "description": "General questions about the system"},
    2: {"name": "Installation", "description": "Setup and installation help"},
    3: {"name": "Configuration", "description": "Configuration and settings"},
    4: {"name": "Security", "description": "Security related topics"},
}

FAQ_ENTRIES = {
    1: {
        "id": 1,
        "category_id": 1,
        "lang": "en",
        "question": "What is phpMyFAQ?",
        "answer": "phpMyFAQ is a multilingual, completely database-driven FAQ-system. It supports various databases to store all data and requires PHP to access this data.",
        "author": "admin",
        "date": "2023-01-15",
        "visits": 1247,
    },
    2: {
        "id": 2,
        "category_id": 1,
        "lang": "en",
        "question": "How do I create a new FAQ entry?",
        "answer": "Navigate to the admin panel and select 'Add new FAQ'. Fill in the question, answer, and assign a category.",
        "author": "admin",
        "date": "2023-02-10",
        "visits": 893,
    },
    3: {
        "id": 3,
        "category_id": 2,
        "lang": "en",
        "question": "What are the system requirements?",
        "answer": "You need PHP 7.4 or higher, a web server (Apache or nginx), and a supported database (MySQL, PostgreSQL, SQLite, or MS SQL Server).",
        "author": "admin",
        "date": "2023-02-20",
        "visits": 2105,
    },
    4: {
        "id": 4,
        "category_id": 3,
        "lang": "en",
        "question": "How do I configure email settings?",
        "answer": "Go to Configuration > Mail and enter your SMTP server details. You can test the configuration using the 'Send test email' button.",
        "author": "moderator",
        "date": "2023-03-05",
        "visits": 456,
    },
    5: {
        "id": 5,
        "category_id": 4,
        "lang": "en",
        "question": "How do I enable LDAP authentication?",
        "answer": "Enable LDAP in Configuration > Authentication. You will need the LDAP server URL, base DN, and bind credentials.",
        "author": "admin",
        "date": "2023-03-18",
        "visits": 312,
    },
}

PMF_VERSION = "3.1.11"

# ---- Template fragments (mirrors phpMyFAQ theme structure) ----

BASE_HEAD = """
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="application-name" content="phpMyFAQ {version}">
    <meta name="generator" content="phpMyFAQ {version}">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .pmf-navbar {{ background-color: #2d3748; }}
        .pmf-navbar .navbar-brand {{ color: #fff; font-weight: 600; }}
        .pmf-navbar .nav-link {{ color: rgba(255,255,255,.8); }}
        .pmf-navbar .nav-link:hover {{ color: #fff; }}
        .pmf-content {{ margin-top: 2rem; }}
        .faq-card {{ border-left: 4px solid #4299e1; }}
        .category-badge {{ background-color: #4299e1; }}
        footer {{ margin-top: 3rem; padding: 1.5rem 0; background-color: #2d3748; color: rgba(255,255,255,.6); }}
        footer a {{ color: rgba(255,255,255,.8); }}
    </style>
""".format(version=PMF_VERSION)

NAVBAR = """
    <nav class="navbar navbar-expand-lg pmf-navbar">
      <div class="container">
        <a class="navbar-brand" href="/">phpMyFAQ</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
            <li class="nav-item"><a class="nav-link" href="/category.php">Categories</a></li>
            <li class="nav-item"><a class="nav-link" href="/search.php">Search</a></li>
            <li class="nav-item"><a class="nav-link" href="/sitemap.php">Sitemap</a></li>
          </ul>
          <ul class="navbar-nav">
            <li class="nav-item"><a class="nav-link" href="/login.php">Login</a></li>
          </ul>
        </div>
      </div>
    </nav>
"""

FOOTER = """
    <footer>
      <div class="container text-center">
        <p>Powered by <a href="#">phpMyFAQ</a> {version}</p>
      </div>
    </footer>
""".format(version=PMF_VERSION)


def render_preview(page_content, reference, lang_param):
    """Generate a preview render of the send2friend page for content validation."""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        output = proc.stdout.read().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    for line in output.split('\n'):
        if line.strip() == 'XSS':
            return True
    return False


# ---- Routes ----

@app.route('/')
def index():
    recent_faqs = ""
    for fid in sorted(FAQ_ENTRIES.keys())[:5]:
        faq = FAQ_ENTRIES[fid]
        cat = FAQ_CATEGORIES.get(faq["category_id"], {})
        recent_faqs += """
        <div class="card mb-3 faq-card">
          <div class="card-body">
            <h5 class="card-title">
              <a href="/faq.php?cat={cat_id}&id={faq_id}&artlang={lang}">{question}</a>
            </h5>
            <p class="card-text text-muted">{answer_preview}...</p>
            <div class="d-flex justify-content-between">
              <span class="badge category-badge">{cat_name}</span>
              <small class="text-muted">{visits} visits</small>
            </div>
          </div>
        </div>
        """.format(
            cat_id=faq["category_id"],
            faq_id=faq["id"],
            lang=faq["lang"],
            question=cgi.escape(faq["question"]),
            answer_preview=cgi.escape(faq["answer"][:120]),
            cat_name=cgi.escape(cat.get("name", "")),
            visits=faq["visits"],
        )

    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>phpMyFAQ - Open Source FAQ system</title>
        {head}
    </head>
    <body>
        {navbar}
        <div class="container pmf-content">
            <div class="row">
                <div class="col-md-8">
                    <h2>Welcome to phpMyFAQ</h2>
                    <p class="lead">Your open source FAQ system for the web.</p>
                    <hr>
                    <h4>Recent FAQs</h4>
                    {recent_faqs}
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">Quick Search</div>
                        <div class="card-body">
                            <form action="/search.php" method="get">
                                <div class="input-group">
                                    <input type="text" class="form-control" name="search" placeholder="Search FAQs...">
                                    <button class="btn btn-primary" type="submit">Search</button>
                                </div>
                            </form>
                        </div>
                    </div>
                    <div class="card mt-3">
                        <div class="card-header">Categories</div>
                        <ul class="list-group list-group-flush">
                            {categories}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        {footer}
    </body>
    </html>""".format(
        head=BASE_HEAD,
        navbar=NAVBAR,
        recent_faqs=recent_faqs,
        categories="".join([
            '<li class="list-group-item"><a href="/category.php?cat={0}">{1}</a></li>'.format(cid, cgi.escape(c["name"]))
            for cid, c in sorted(FAQ_CATEGORIES.items())
        ]),
        footer=FOOTER,
    )
    return html


@app.route('/faq.php')
def faq_view():
    cat_id = request.args.get('cat', '1')
    faq_id = request.args.get('id', '1')
    artlang = request.args.get('artlang', 'en')

    try:
        faq_id = int(faq_id)
    except (ValueError, TypeError):
        faq_id = 1

    faq = FAQ_ENTRIES.get(faq_id)
    if not faq:
        return make_response("FAQ entry not found.", 404)

    cat = FAQ_CATEGORIES.get(faq["category_id"], {"name": "Unknown"})

    html = """<!DOCTYPE html>
    <html lang="{artlang}">
    <head>
        <title>{question} - phpMyFAQ</title>
        {head}
    </head>
    <body>
        {navbar}
        <div class="container pmf-content">
            <nav aria-label="breadcrumb">
              <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/">Home</a></li>
                <li class="breadcrumb-item"><a href="/category.php?cat={cat_id}">{cat_name}</a></li>
                <li class="breadcrumb-item active">{question}</li>
              </ol>
            </nav>
            <div class="card">
                <div class="card-header">
                    <h4>{question}</h4>
                    <small class="text-muted">Author: {author} | Date: {date} | Language: {artlang_display}</small>
                </div>
                <div class="card-body">
                    <p>{answer}</p>
                </div>
                <div class="card-footer">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="text-muted">{visits} visits</span>
                        <div>
                            <a href="/send2friend.php?cat={cat_id}&id={faq_id}&artlang={artlang_raw}" class="btn btn-sm btn-outline-primary">
                                Send to a friend
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {footer}
    </body>
    </html>""".format(
        head=BASE_HEAD,
        navbar=NAVBAR,
        footer=FOOTER,
        artlang=cgi.escape(artlang, quote=True),
        artlang_display=cgi.escape(artlang, quote=True),
        artlang_raw=cgi.escape(artlang, quote=True),
        question=cgi.escape(faq["question"]),
        answer=cgi.escape(faq["answer"]),
        author=cgi.escape(faq["author"]),
        date=cgi.escape(faq["date"]),
        visits=faq["visits"],
        cat_id=faq["category_id"],
        cat_name=cgi.escape(cat["name"]),
        faq_id=faq["id"],
    )
    response = make_response(html)
    return response


@app.route('/send2friend.php')
def send2friend():
    cat_id = request.args.get('cat', '1')
    faq_id = request.args.get('id', '1')

    faqLanguage = request.args.get('artlang', 'en')

    try:
        faq_id_int = int(faq_id)
    except (ValueError, TypeError):
        faq_id_int = 1

    faq = FAQ_ENTRIES.get(faq_id_int)
    if not faq:
        return make_response("FAQ entry not found.", 404)

    cat = FAQ_CATEGORIES.get(faq["category_id"], {"name": "Unknown"})

    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Send FAQ to a friend - phpMyFAQ</title>
        {head}
    </head>
    <body>
        {navbar}
        <div class="container pmf-content">
            <nav aria-label="breadcrumb">
              <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/">Home</a></li>
                <li class="breadcrumb-item active">Send FAQ to a friend</li>
              </ol>
            </nav>
            <div class="card">
                <div class="card-header">
                    <h4>Send "{question}" to a friend</h4>
                </div>
                <div class="card-body">
                    <form action="/send2friend.php" method="post" id="sendToFriendForm">
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
                            <textarea class="form-control" id="message" name="message" rows="3"></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Send Recommendation</button>
                    </form>
                </div>
            </div>
        </div>
        {footer}
    </body>
    </html>""".format(
        head=BASE_HEAD,
        navbar=NAVBAR,
        footer=FOOTER,
        question=cgi.escape(faq["question"]),
        cat_id=cgi.escape(str(faq["category_id"]), quote=True),
        faq_id=cgi.escape(str(faq["id"]), quote=True),
        lang=faqLanguage,
        faq_title=cgi.escape(faq["question"]),
    )

    preview_result = render_preview(html, flags[0], faqLanguage)

    if preview_result:
        result_html = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Send FAQ to a friend - phpMyFAQ</title>
            {head}
        </head>
        <body>
            {navbar}
            <div class="container pmf-content">
                <div class="alert alert-success">
                    <h4>Recommendation sent successfully!</h4>
                    <p>Reference: {ref}</p>
                </div>
            </div>
            {footer}
        </body>
        </html>""".format(
            head=BASE_HEAD,
            navbar=NAVBAR,
            footer=FOOTER,
            ref=flags[0],
        )
        response = make_response(result_html)
        response.headers["X-XSS-Protection"] = "0"
        return response

    response = make_response(html)
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/send2friend.php', methods=['POST'])
def send2friend_post():
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Send FAQ to a friend - phpMyFAQ</title>
        {head}
    </head>
    <body>
        {navbar}
        <div class="container pmf-content">
            <div class="alert alert-info">
                <h4>Message Processing</h4>
                <p>Your recommendation request has been received. The recipient will be notified shortly.</p>
            </div>
            <a href="/" class="btn btn-primary">Back to Home</a>
        </div>
        {footer}
    </body>
    </html>""".format(
        head=BASE_HEAD,
        navbar=NAVBAR,
        footer=FOOTER,
    )
    return html


@app.route('/category.php')
def category_view():
    cat_id = request.args.get('cat', None)

    if cat_id:
        try:
            cat_id = int(cat_id)
        except (ValueError, TypeError):
            cat_id = None

    if cat_id and cat_id in FAQ_CATEGORIES:
        cat = FAQ_CATEGORIES[cat_id]
        faqs_html = ""
        for fid, faq in sorted(FAQ_ENTRIES.items()):
            if faq["category_id"] == cat_id:
                faqs_html += """
                <div class="card mb-2 faq-card">
                    <div class="card-body">
                        <h5><a href="/faq.php?cat={cat_id}&id={faq_id}&artlang={lang}">{question}</a></h5>
                        <p class="text-muted mb-0">{answer_preview}...</p>
                    </div>
                </div>
                """.format(
                    cat_id=cat_id,
                    faq_id=faq["id"],
                    lang=cgi.escape(faq["lang"], quote=True),
                    question=cgi.escape(faq["question"]),
                    answer_preview=cgi.escape(faq["answer"][:100]),
                )

        html = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <title>{cat_name} - phpMyFAQ</title>
            {head}
        </head>
        <body>
            {navbar}
            <div class="container pmf-content">
                <nav aria-label="breadcrumb">
                  <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/">Home</a></li>
                    <li class="breadcrumb-item"><a href="/category.php">Categories</a></li>
                    <li class="breadcrumb-item active">{cat_name}</li>
                  </ol>
                </nav>
                <h3>{cat_name}</h3>
                <p class="text-muted">{cat_desc}</p>
                {faqs}
            </div>
            {footer}
        </body>
        </html>""".format(
            head=BASE_HEAD,
            navbar=NAVBAR,
            footer=FOOTER,
            cat_name=cgi.escape(cat["name"]),
            cat_desc=cgi.escape(cat["description"]),
            faqs=faqs_html if faqs_html else "<p>No FAQs in this category yet.</p>",
        )
    else:
        cats_html = ""
        for cid, cat in sorted(FAQ_CATEGORIES.items()):
            count = sum(1 for f in FAQ_ENTRIES.values() if f["category_id"] == cid)
            cats_html += """
            <div class="col-md-6 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5><a href="/category.php?cat={cid}">{name}</a></h5>
                        <p class="text-muted">{desc}</p>
                        <span class="badge bg-secondary">{count} FAQs</span>
                    </div>
                </div>
            </div>
            """.format(
                cid=cid,
                name=cgi.escape(cat["name"]),
                desc=cgi.escape(cat["description"]),
                count=count,
            )

        html = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Categories - phpMyFAQ</title>
            {head}
        </head>
        <body>
            {navbar}
            <div class="container pmf-content">
                <h3>FAQ Categories</h3>
                <div class="row">
                    {cats}
                </div>
            </div>
            {footer}
        </body>
        </html>""".format(
            head=BASE_HEAD,
            navbar=NAVBAR,
            footer=FOOTER,
            cats=cats_html,
        )

    return html


@app.route('/search.php')
def search_view():
    query = request.args.get('search', '')
    results_html = ""

    if query:
        for fid, faq in sorted(FAQ_ENTRIES.items()):
            if query.lower() in faq["question"].lower() or query.lower() in faq["answer"].lower():
                results_html += """
                <div class="card mb-2 faq-card">
                    <div class="card-body">
                        <h5><a href="/faq.php?cat={cat_id}&id={faq_id}&artlang={lang}">{question}</a></h5>
                        <p class="text-muted mb-0">{answer_preview}...</p>
                    </div>
                </div>
                """.format(
                    cat_id=faq["category_id"],
                    faq_id=faq["id"],
                    lang=cgi.escape(faq["lang"], quote=True),
                    question=cgi.escape(faq["question"]),
                    answer_preview=cgi.escape(faq["answer"][:100]),
                )

    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Search - phpMyFAQ</title>
        {head}
    </head>
    <body>
        {navbar}
        <div class="container pmf-content">
            <h3>Search FAQs</h3>
            <form action="/search.php" method="get" class="mb-4">
                <div class="input-group">
                    <input type="text" class="form-control" name="search" value="{query}" placeholder="Enter search term...">
                    <button class="btn btn-primary" type="submit">Search</button>
                </div>
            </form>
            {results}
        </div>
        {footer}
    </body>
    </html>""".format(
        head=BASE_HEAD,
        navbar=NAVBAR,
        footer=FOOTER,
        query=cgi.escape(query, quote=True),
        results=results_html if results_html else ("<p>No results found.</p>" if query else ""),
    )
    return html


@app.route('/sitemap.php')
def sitemap_view():
    entries = ""
    for fid, faq in sorted(FAQ_ENTRIES.items()):
        cat = FAQ_CATEGORIES.get(faq["category_id"], {"name": "Unknown"})
        entries += """
        <tr>
            <td><a href="/faq.php?cat={cat_id}&id={faq_id}&artlang={lang}">{question}</a></td>
            <td><span class="badge category-badge">{cat_name}</span></td>
            <td>{date}</td>
        </tr>
        """.format(
            cat_id=faq["category_id"],
            faq_id=faq["id"],
            lang=cgi.escape(faq["lang"], quote=True),
            question=cgi.escape(faq["question"]),
            cat_name=cgi.escape(cat["name"]),
            date=faq["date"],
        )

    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Sitemap - phpMyFAQ</title>
        {head}
    </head>
    <body>
        {navbar}
        <div class="container pmf-content">
            <h3>Sitemap</h3>
            <table class="table table-striped">
                <thead>
                    <tr><th>FAQ</th><th>Category</th><th>Date</th></tr>
                </thead>
                <tbody>
                    {entries}
                </tbody>
            </table>
        </div>
        {footer}
    </body>
    </html>""".format(
        head=BASE_HEAD,
        navbar=NAVBAR,
        footer=FOOTER,
        entries=entries,
    )
    return html


@app.route('/login.php')
def login_view():
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Login - phpMyFAQ</title>
        {head}
    </head>
    <body>
        {navbar}
        <div class="container pmf-content">
            <div class="row justify-content-center">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header"><h4>Login</h4></div>
                        <div class="card-body">
                            <form method="post" action="/login.php">
                                <div class="mb-3">
                                    <label for="faqusername" class="form-label">Username</label>
                                    <input type="text" class="form-control" id="faqusername" name="faqusername">
                                </div>
                                <div class="mb-3">
                                    <label for="faqpassword" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="faqpassword" name="faqpassword">
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Login</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {footer}
    </body>
    </html>""".format(
        head=BASE_HEAD,
        navbar=NAVBAR,
        footer=FOOTER,
    )
    return html


@app.route('/login.php', methods=['POST'])
def login_post():
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Login - phpMyFAQ</title>
        {head}
    </head>
    <body>
        {navbar}
        <div class="container pmf-content">
            <div class="row justify-content-center">
                <div class="col-md-4">
                    <div class="alert alert-danger">Invalid username or password.</div>
                    <a href="/login.php" class="btn btn-primary">Try again</a>
                </div>
            </div>
        </div>
        {footer}
    </body>
    </html>""".format(
        head=BASE_HEAD,
        navbar=NAVBAR,
        footer=FOOTER,
    )
    return html, 401


@app.errorhandler(404)
def not_found(e):
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Page not found - phpMyFAQ</title>
        {head}
    </head>
    <body>
        {navbar}
        <div class="container pmf-content">
            <div class="alert alert-warning">
                <h4>Error 404</h4>
                <p>The requested page was not found.</p>
            </div>
            <a href="/" class="btn btn-primary">Back to Home</a>
        </div>
        {footer}
    </body>
    </html>""".format(
        head=BASE_HEAD,
        navbar=NAVBAR,
        footer=FOOTER,
    )
    return html, 404


@app.errorhandler(500)
def server_error(e):
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Server Error - phpMyFAQ</title>
        {head}
    </head>
    <body>
        {navbar}
        <div class="container pmf-content">
            <div class="alert alert-danger">
                <h4>Error 500</h4>
                <p>An internal server error occurred. Please try again later.</p>
            </div>
            <a href="/" class="btn btn-primary">Back to Home</a>
        </div>
        {footer}
    </body>
    </html>""".format(
        head=BASE_HEAD,
        navbar=NAVBAR,
        footer=FOOTER,
    )
    return html, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
