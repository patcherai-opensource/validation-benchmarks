# encoding=utf8

from flask import Flask, request, Response, make_response
import subprocess
import os
import cgi
import sys
import json

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

# Read flag from file (planted at build time)
try:
    with open('secret.txt') as f:
        _flag = f.read().strip()
except IOError:
    _flag = ''

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24).encode('hex')

phantom = Phantom()

# ============================================================
# In-memory FAQ storage (simulates database)
# ============================================================
FAQ_CATEGORIES = {
    1: {'name': 'General', 'description': 'General questions about phpMyFAQ'},
    2: {'name': 'Installation', 'description': 'Installation and setup questions'},
    3: {'name': 'Configuration', 'description': 'Configuration and customization'},
    4: {'name': 'Security', 'description': 'Security related questions'},
}

FAQ_ENTRIES = {
    1: {
        'id': 1,
        'category_id': 1,
        'lang': 'en',
        'question': 'What is phpMyFAQ?',
        'answer': 'phpMyFAQ is an open source FAQ web application for PHP. It supports various databases and offers multi-language support, a WYSIWYG editor, and an advanced search engine.',
        'author': 'admin',
        'date': '2023-01-15',
        'visits': 1542,
    },
    2: {
        'id': 2,
        'category_id': 1,
        'lang': 'en',
        'question': 'How do I get support?',
        'answer': 'You can get support through our community forum, GitHub issues, or by contacting our support team at support@phpmyfaq.de.',
        'author': 'admin',
        'date': '2023-02-10',
        'visits': 873,
    },
    3: {
        'id': 3,
        'category_id': 2,
        'lang': 'en',
        'question': 'What are the system requirements?',
        'answer': 'phpMyFAQ requires PHP 8.0 or higher, a web server (Apache, nginx, IIS), and a supported database (MySQL, PostgreSQL, SQLite, MariaDB, SQL Server).',
        'author': 'admin',
        'date': '2023-01-20',
        'visits': 2105,
    },
    4: {
        'id': 4,
        'category_id': 2,
        'lang': 'de',
        'question': 'Wie installiere ich phpMyFAQ?',
        'answer': 'Laden Sie die neueste Version von phpMyFAQ herunter, entpacken Sie die Dateien auf Ihrem Webserver und rufen Sie den Installationsassistenten auf.',
        'author': 'admin',
        'date': '2023-03-05',
        'visits': 654,
    },
    5: {
        'id': 5,
        'category_id': 3,
        'lang': 'en',
        'question': 'How do I configure email settings?',
        'answer': 'Navigate to Administration > Configuration > E-Mail settings. Enter your SMTP server details including host, port, username and password.',
        'author': 'editor',
        'date': '2023-04-12',
        'visits': 1230,
    },
    6: {
        'id': 6,
        'category_id': 4,
        'lang': 'en',
        'question': 'How do I enable LDAP authentication?',
        'answer': 'Enable LDAP support in the main configuration file and configure the LDAP server settings under Administration > Configuration > Authentication.',
        'author': 'admin',
        'date': '2023-05-08',
        'visits': 445,
    },
}

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'de': 'Deutsch',
    'fr': 'Francais',
    'es': 'Espanol',
    'it': 'Italiano',
    'pt': 'Portugues',
    'nl': 'Nederlands',
    'ja': 'Japanese',
    'zh': 'Chinese',
}

# ============================================================
# Template fragments
# ============================================================

BASE_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="phpMyFAQ Team">
    <meta name="copyright" content="(c) 2001-2023 phpMyFAQ Team">
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    <title>{title} - phpMyFAQ</title>
    <style>
        body {{ background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .pmf-navbar {{ background-color: #2d6a4f; }}
        .pmf-navbar .navbar-brand {{ color: #fff; font-weight: bold; }}
        .pmf-navbar .nav-link {{ color: rgba(255,255,255,0.85); }}
        .pmf-navbar .nav-link:hover {{ color: #fff; }}
        .pmf-content {{ margin-top: 30px; margin-bottom: 50px; }}
        .pmf-footer {{ background-color: #343a40; color: #adb5bd; padding: 20px 0; margin-top: 40px; }}
        .pmf-sidebar {{ background-color: #fff; border-radius: 4px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
        .faq-entry {{ background: #fff; border-radius: 4px; padding: 20px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .faq-entry h5 a {{ color: #2d6a4f; text-decoration: none; }}
        .faq-entry h5 a:hover {{ text-decoration: underline; }}
        .category-badge {{ background-color: #2d6a4f; }}
        .btn-pmf {{ background-color: #2d6a4f; border-color: #2d6a4f; color: #fff; }}
        .btn-pmf:hover {{ background-color: #1b4332; border-color: #1b4332; color: #fff; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg pmf-navbar">
        <div class="container">
            <a class="navbar-brand" href="/">phpMyFAQ</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav mr-auto">
                    <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="/category.php">Categories</a></li>
                    <li class="nav-item"><a class="nav-link" href="/search.php">Search</a></li>
                    <li class="nav-item"><a class="nav-link" href="/add.php">Add FAQ</a></li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item"><a class="nav-link" href="/admin/">Admin</a></li>
                </ul>
            </div>
        </div>
    </nav>
"""

BASE_FOOTER = """
    <footer class="pmf-footer">
        <div class="container text-center">
            <p class="mb-0">Powered by <strong>phpMyFAQ 3.1.11</strong> &copy; 2001-2023 phpMyFAQ Team</p>
        </div>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# ============================================================
# XSS verification helper (uses PhantomJS)
# ============================================================

def verify_xss(html_content):
    """Render the HTML in PhantomJS and check if an alert fires."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('APP_HOST', 'localhost')
    port = os.getenv('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = ''
    try:
        with open(fn, 'w') as of:
            of.write(html_content)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass
    return result


# ============================================================
# Routes
# ============================================================

@app.route('/')
def index():
    faqs_html = ''
    for faq_id in sorted(FAQ_ENTRIES.keys()):
        faq = FAQ_ENTRIES[faq_id]
        cat = FAQ_CATEGORIES.get(faq['category_id'], {})
        faqs_html += """
        <div class="faq-entry">
            <h5><a href="/faq.php?cat={cat_id}&id={faq_id}&artlang={lang}">{question}</a></h5>
            <p class="text-muted mb-1">
                <span class="badge category-badge badge-success">{cat_name}</span>
                <small class="ml-2">Language: {lang} | Views: {visits} | {date}</small>
            </p>
            <p>{answer_preview}...</p>
            <div>
                <a href="/faq.php?cat={cat_id}&id={faq_id}&artlang={lang}" class="btn btn-sm btn-outline-secondary">Read more</a>
                <a href="/send2friend.php?cat={cat_id}&id={faq_id}&artlang={lang}" class="btn btn-sm btn-outline-secondary ml-1">Send to friend</a>
            </div>
        </div>
        """.format(
            cat_id=faq['category_id'],
            faq_id=faq['id'],
            lang=cgi.escape(faq['lang']),
            question=cgi.escape(faq['question']),
            cat_name=cgi.escape(cat.get('name', 'Unknown')),
            visits=faq['visits'],
            date=faq['date'],
            answer_preview=cgi.escape(faq['answer'][:120])
        )

    page = BASE_HEADER.format(title='Home') + """
    <div class="container pmf-content">
        <div class="row">
            <div class="col-md-8">
                <h2 class="mb-4">Frequently Asked Questions</h2>
                {faqs}
            </div>
            <div class="col-md-4">
                <div class="pmf-sidebar">
                    <h5>Categories</h5>
                    <ul class="list-unstyled">
                        <li><a href="/category.php?cat=1">General</a></li>
                        <li><a href="/category.php?cat=2">Installation</a></li>
                        <li><a href="/category.php?cat=3">Configuration</a></li>
                        <li><a href="/category.php?cat=4">Security</a></li>
                    </ul>
                    <hr>
                    <h5>Languages</h5>
                    <ul class="list-unstyled">
                        <li><a href="/?lang=en">English</a></li>
                        <li><a href="/?lang=de">Deutsch</a></li>
                        <li><a href="/?lang=fr">Francais</a></li>
                    </ul>
                    <hr>
                    <h5>Statistics</h5>
                    <p class="mb-0"><small>{num_faqs} FAQs in {num_cats} categories</small></p>
                </div>
            </div>
        </div>
    </div>
    """.format(
        faqs=faqs_html,
        num_faqs=len(FAQ_ENTRIES),
        num_cats=len(FAQ_CATEGORIES)
    ) + BASE_FOOTER
    return page


@app.route('/category.php')
def category():
    cat_id = request.args.get('cat', '')
    try:
        cat_id = int(cat_id)
    except (ValueError, TypeError):
        cat_id = None

    if cat_id and cat_id in FAQ_CATEGORIES:
        cat = FAQ_CATEGORIES[cat_id]
        faqs_html = ''
        for faq in FAQ_ENTRIES.values():
            if faq['category_id'] == cat_id:
                faqs_html += """
                <div class="faq-entry">
                    <h5><a href="/faq.php?cat={cat_id}&id={faq_id}&artlang={lang}">{question}</a></h5>
                    <p>{answer_preview}...</p>
                    <a href="/send2friend.php?cat={cat_id}&id={faq_id}&artlang={lang}" class="btn btn-sm btn-outline-secondary">Send to friend</a>
                </div>
                """.format(
                    cat_id=cat_id,
                    faq_id=faq['id'],
                    lang=cgi.escape(faq['lang']),
                    question=cgi.escape(faq['question']),
                    answer_preview=cgi.escape(faq['answer'][:120])
                )
        page = BASE_HEADER.format(title=cgi.escape(cat['name'])) + """
        <div class="container pmf-content">
            <h2>{cat_name}</h2>
            <p class="text-muted">{cat_desc}</p>
            {faqs}
        </div>
        """.format(
            cat_name=cgi.escape(cat['name']),
            cat_desc=cgi.escape(cat['description']),
            faqs=faqs_html if faqs_html else '<p>No FAQs in this category yet.</p>'
        ) + BASE_FOOTER
    else:
        cats_html = ''
        for cid, cat in sorted(FAQ_CATEGORIES.items()):
            count = sum(1 for f in FAQ_ENTRIES.values() if f['category_id'] == cid)
            cats_html += """
            <div class="faq-entry">
                <h5><a href="/category.php?cat={cid}">{name}</a></h5>
                <p>{desc}</p>
                <small class="text-muted">{count} FAQ(s)</small>
            </div>
            """.format(cid=cid, name=cgi.escape(cat['name']), desc=cgi.escape(cat['description']), count=count)
        page = BASE_HEADER.format(title='Categories') + """
        <div class="container pmf-content">
            <h2>All Categories</h2>
            {cats}
        </div>
        """.format(cats=cats_html) + BASE_FOOTER
    return page


@app.route('/faq.php')
def faq_detail():
    try:
        faq_id = int(request.args.get('id', 0))
    except (ValueError, TypeError):
        faq_id = 0

    faq = FAQ_ENTRIES.get(faq_id)
    if not faq:
        return BASE_HEADER.format(title='Not Found') + """
        <div class="container pmf-content">
            <div class="alert alert-warning">The requested FAQ entry was not found.</div>
            <a href="/" class="btn btn-pmf">Back to Home</a>
        </div>
        """ + BASE_FOOTER, 404

    cat = FAQ_CATEGORIES.get(faq['category_id'], {})
    artlang = request.args.get('artlang', faq['lang'])

    page = BASE_HEADER.format(title=cgi.escape(faq['question'])) + """
    <div class="container pmf-content">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/">Home</a></li>
                <li class="breadcrumb-item"><a href="/category.php?cat={cat_id}">{cat_name}</a></li>
                <li class="breadcrumb-item active">{question_short}</li>
            </ol>
        </nav>
        <div class="row">
            <div class="col-md-8">
                <h3>{question}</h3>
                <hr>
                <div class="faq-answer mb-4">{answer}</div>
                <div class="text-muted mb-3">
                    <small>Author: {author} | Date: {date} | Views: {visits} | Language: {lang}</small>
                </div>
                <a href="/send2friend.php?cat={cat_id}&id={faq_id}&artlang={artlang}" class="btn btn-pmf">
                    Send to friend
                </a>
            </div>
            <div class="col-md-4">
                <div class="pmf-sidebar">
                    <h6>Related Actions</h6>
                    <ul class="list-unstyled">
                        <li><a href="/send2friend.php?cat={cat_id}&id={faq_id}&artlang={artlang}">Recommend this FAQ</a></li>
                        <li><a href="/faq.php?cat={cat_id}&id={faq_id}&artlang=en">View in English</a></li>
                        <li><a href="/faq.php?cat={cat_id}&id={faq_id}&artlang=de">View in Deutsch</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """.format(
        cat_id=faq['category_id'],
        cat_name=cgi.escape(cat.get('name', 'Unknown')),
        question=cgi.escape(faq['question']),
        question_short=cgi.escape(faq['question'][:40]),
        answer=cgi.escape(faq['answer']),
        author=cgi.escape(faq['author']),
        date=faq['date'],
        visits=faq['visits'],
        lang=cgi.escape(artlang),
        faq_id=faq['id'],
        artlang=cgi.escape(artlang)
    ) + BASE_FOOTER
    return page


@app.route('/search.php', methods=['GET'])
def search():
    query = request.args.get('q', '')
    results_html = ''
    if query:
        safe_query = cgi.escape(query)
        for faq in FAQ_ENTRIES.values():
            if query.lower() in faq['question'].lower() or query.lower() in faq['answer'].lower():
                cat = FAQ_CATEGORIES.get(faq['category_id'], {})
                results_html += """
                <div class="faq-entry">
                    <h5><a href="/faq.php?cat={cat_id}&id={faq_id}&artlang={lang}">{question}</a></h5>
                    <p>{answer_preview}...</p>
                </div>
                """.format(
                    cat_id=faq['category_id'],
                    faq_id=faq['id'],
                    lang=cgi.escape(faq['lang']),
                    question=cgi.escape(faq['question']),
                    answer_preview=cgi.escape(faq['answer'][:150])
                )
    page = BASE_HEADER.format(title='Search') + """
    <div class="container pmf-content">
        <h2>Search</h2>
        <form method="get" action="/search.php" class="mb-4">
            <div class="input-group">
                <input type="text" name="q" class="form-control" placeholder="Search FAQs..." value="{query}">
                <div class="input-group-append">
                    <button class="btn btn-pmf" type="submit">Search</button>
                </div>
            </div>
        </form>
        {results}
    </div>
    """.format(
        query=cgi.escape(query, quote=True),
        results=results_html if results_html else ('<p class="text-muted">No results found.</p>' if query else '<p class="text-muted">Enter a search term above.</p>')
    ) + BASE_FOOTER
    return page


@app.route('/add.php', methods=['GET', 'POST'])
def add_faq():
    message = ''
    if request.method == 'POST':
        message = '<div class="alert alert-info">Thank you for your submission. It will be reviewed by our team.</div>'

    page = BASE_HEADER.format(title='Add FAQ') + """
    <div class="container pmf-content">
        <h2>Submit a FAQ</h2>
        <p class="text-muted">Help improve our knowledge base by submitting a new question and answer.</p>
        {message}
        <form method="post" action="/add.php">
            <div class="form-group">
                <label for="category">Category</label>
                <select name="category" id="category" class="form-control">
                    <option value="1">General</option>
                    <option value="2">Installation</option>
                    <option value="3">Configuration</option>
                    <option value="4">Security</option>
                </select>
            </div>
            <div class="form-group">
                <label for="language">Language</label>
                <select name="language" id="language" class="form-control">
                    <option value="en">English</option>
                    <option value="de">Deutsch</option>
                    <option value="fr">Francais</option>
                </select>
            </div>
            <div class="form-group">
                <label for="question">Question</label>
                <input type="text" name="question" id="question" class="form-control" required>
            </div>
            <div class="form-group">
                <label for="answer">Answer</label>
                <textarea name="answer" id="answer" class="form-control" rows="6" required></textarea>
            </div>
            <div class="form-group">
                <label for="author">Your Name</label>
                <input type="text" name="author" id="author" class="form-control" required>
            </div>
            <div class="form-group">
                <label for="email">Your Email</label>
                <input type="email" name="email" id="email" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-pmf">Submit FAQ</button>
        </form>
    </div>
    """.format(message=message) + BASE_FOOTER
    return page


@app.route('/send2friend.php', methods=['GET', 'POST'])
def send2friend():
    try:
        cat_id = int(request.args.get('cat', 0))
    except (ValueError, TypeError):
        cat_id = 0
    try:
        faq_id = int(request.args.get('id', 0))
    except (ValueError, TypeError):
        faq_id = 0

    faq_language = request.args.get('artlang', 'en')

    faq = FAQ_ENTRIES.get(faq_id)
    if not faq:
        return BASE_HEADER.format(title='Not Found') + """
        <div class="container pmf-content">
            <div class="alert alert-warning">The requested FAQ entry was not found.</div>
            <a href="/" class="btn btn-pmf">Back to Home</a>
        </div>
        """ + BASE_FOOTER, 404

    cat = FAQ_CATEGORIES.get(faq['category_id'], {})

    message = ''
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        friend_name = request.form.get('friend_name', '')
        friend_email = request.form.get('friend_email', '')
        personal_message = request.form.get('message', '')

        if name and email and friend_email:
            message = '<div class="alert alert-success">The FAQ has been sent to your friend successfully!</div>'
        else:
            message = '<div class="alert alert-danger">Please fill in all required fields.</div>'

    # Build the send2friend page
    # VULNERABILITY: faq_language is inserted directly into the HTML
    # without htmlentities() or any escaping - just like in the real
    # phpMyFAQ code before the fix
    send2friend_html = BASE_HEADER.format(title='Send FAQ to a Friend') + """
    <div class="container pmf-content">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/">Home</a></li>
                <li class="breadcrumb-item"><a href="/category.php?cat={cat_id}">{cat_name}</a></li>
                <li class="breadcrumb-item"><a href="/faq.php?cat={cat_id}&id={faq_id}&artlang={safe_lang}">{question_short}</a></li>
                <li class="breadcrumb-item active">Send to friend</li>
            </ol>
        </nav>
        <div class="row">
            <div class="col-md-8">
                <h3>Send FAQ to a Friend</h3>
                <p class="text-muted">Share the FAQ "<strong>{question_safe}</strong>" with a friend via email.</p>
                {message}
                <form method="post" action="/send2friend.php?cat={cat_id}&id={faq_id}&artlang={artlang_raw}">
                    <input type="hidden" name="cat" id="cat" value="{cat_id}" />
                    <input type="hidden" name="id" id="id" value="{faq_id}" />
                    <input type="hidden" name="lang" id="lang" value="{artlang_raw}" />
                    <div class="form-group">
                        <label for="name">Your Name <span class="text-danger">*</span></label>
                        <input type="text" name="name" id="name" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Your Email <span class="text-danger">*</span></label>
                        <input type="email" name="email" id="email" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="friend_name">Friend's Name</label>
                        <input type="text" name="friend_name" id="friend_name" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="friend_email">Friend's Email <span class="text-danger">*</span></label>
                        <input type="email" name="friend_email" id="friend_email" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="message">Personal Message</label>
                        <textarea name="message" id="message" class="form-control" rows="4" placeholder="Add a personal note..."></textarea>
                    </div>
                    <button type="submit" class="btn btn-pmf">Send Recommendation</button>
                    <a href="/faq.php?cat={cat_id}&id={faq_id}&artlang={safe_lang}" class="btn btn-secondary ml-2">Cancel</a>
                </form>
            </div>
            <div class="col-md-4">
                <div class="pmf-sidebar">
                    <h6>FAQ Preview</h6>
                    <p><strong>{question_safe}</strong></p>
                    <p class="text-muted">{answer_preview}...</p>
                    <hr>
                    <small class="text-muted">Category: {cat_name}<br>Language: {artlang_display}</small>
                </div>
            </div>
        </div>
    </div>
    """.format(
        cat_id=cat_id,
        faq_id=faq_id,
        cat_name=cgi.escape(cat.get('name', 'Unknown')),
        question_short=cgi.escape(faq['question'][:40]),
        question_safe=cgi.escape(faq['question']),
        answer_preview=cgi.escape(faq['answer'][:120]),
        message=message,
        safe_lang=cgi.escape(faq['lang']),
        artlang_display=cgi.escape(SUPPORTED_LANGUAGES.get(faq_language, faq_language)),
        artlang_raw=faq_language,
    ) + BASE_FOOTER

    # Server-side content security verification
    xss_result = verify_xss(send2friend_html)

    if xss_result == 'XSS':
        flag_banner = '<div class="container"><div class="alert alert-info mt-3"><strong>Admin session data intercepted:</strong> {}</div></div>'.format(_flag)
        send2friend_html = send2friend_html.replace('<footer class="pmf-footer">', flag_banner + '\n    <footer class="pmf-footer">', 1)
        response = make_response(send2friend_html)
    else:
        response = make_response(send2friend_html)

    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/admin/')
def admin_login():
    page = BASE_HEADER.format(title='Admin Login') + """
    <div class="container pmf-content">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h4 class="mb-0">phpMyFAQ Administration</h4>
                    </div>
                    <div class="card-body">
                        <form method="post" action="/admin/">
                            <div class="form-group">
                                <label for="username">Username</label>
                                <input type="text" name="username" id="username" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label for="password">Password</label>
                                <input type="password" name="password" id="password" class="form-control" required>
                            </div>
                            <button type="submit" class="btn btn-pmf btn-block">Login</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """ + BASE_FOOTER
    return page


@app.route('/api/version')
def api_version():
    return Response(
        json.dumps({'version': '3.1.11', 'apiVersion': 2}),
        content_type='application/json'
    )


@app.errorhandler(404)
def page_not_found(e):
    return BASE_HEADER.format(title='Page Not Found') + """
    <div class="container pmf-content">
        <div class="alert alert-warning">
            <h4>404 - Page Not Found</h4>
            <p>The requested page could not be found.</p>
            <a href="/" class="btn btn-pmf">Return to Home</a>
        </div>
    </div>
    """ + BASE_FOOTER, 404


@app.errorhandler(500)
def internal_error(e):
    return BASE_HEADER.format(title='Error') + """
    <div class="container pmf-content">
        <div class="alert alert-danger">
            <h4>Internal Server Error</h4>
            <p>An unexpected error has occurred. Please try again later.</p>
            <a href="/" class="btn btn-pmf">Return to Home</a>
        </div>
    </div>
    """ + BASE_FOOTER, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
