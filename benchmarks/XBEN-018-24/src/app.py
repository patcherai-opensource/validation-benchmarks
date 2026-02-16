# encoding=utf8

from flask import Flask, request, make_response, redirect
import subprocess
import os
import cgi
import urllib
import sys

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flag_value = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

# Simulated FAQ database
FAQ_ENTRIES = [
    {
        'id': 1,
        'category_id': 1,
        'category': 'General',
        'question': 'How do I reset my password?',
        'answer': 'Navigate to the login page and click "Forgot Password". Enter your registered email address and follow the instructions sent to your inbox.',
        'author': 'admin',
        'date': '2023-01-15',
        'views': 1247,
        'lang': 'en',
        'solution_id': 1001
    },
    {
        'id': 2,
        'category_id': 1,
        'category': 'General',
        'question': 'What browsers are supported?',
        'answer': 'We support the latest versions of Chrome, Firefox, Safari, and Edge. Internet Explorer 11 is supported on a best-effort basis.',
        'author': 'admin',
        'date': '2023-02-20',
        'views': 893,
        'lang': 'en',
        'solution_id': 1002
    },
    {
        'id': 3,
        'category_id': 2,
        'category': 'Account',
        'question': 'How do I change my display name?',
        'answer': 'Go to User Control Panel, click on "Edit Profile", and update your display name. Changes take effect immediately.',
        'author': 'support',
        'date': '2023-03-10',
        'views': 564,
        'lang': 'en',
        'solution_id': 1003
    },
    {
        'id': 4,
        'category_id': 2,
        'category': 'Account',
        'question': 'Can I have multiple accounts?',
        'answer': 'Each user is allowed one account. Multiple accounts may be merged or suspended per our terms of service.',
        'author': 'admin',
        'date': '2023-04-05',
        'views': 321,
        'lang': 'en',
        'solution_id': 1004
    },
    {
        'id': 5,
        'category_id': 3,
        'category': 'Technical',
        'question': 'What is the maximum upload size?',
        'answer': 'The maximum file upload size is 10MB. For larger files, please use the external attachment service linked in the admin panel.',
        'author': 'support',
        'date': '2023-05-12',
        'views': 782,
        'lang': 'en',
        'solution_id': 1005
    },
    {
        'id': 6,
        'category_id': 3,
        'category': 'Technical',
        'question': 'How do I enable two-factor authentication?',
        'answer': 'Go to User Control Panel > Security Settings > Enable 2FA. You can use any TOTP-compatible authenticator application.',
        'author': 'admin',
        'date': '2023-06-18',
        'views': 445,
        'lang': 'en',
        'solution_id': 1006
    },
    {
        'id': 7,
        'category_id': 4,
        'category': 'Billing',
        'question': 'How do I update my payment method?',
        'answer': 'Navigate to Account Settings > Billing > Payment Methods. Click "Add New" to add a new payment method, or "Edit" to update an existing one.',
        'author': 'billing',
        'date': '2023-07-22',
        'views': 198,
        'lang': 'en',
        'solution_id': 1007
    },
    {
        'id': 8,
        'category_id': 4,
        'category': 'Billing',
        'question': 'Where can I download my invoices?',
        'answer': 'Invoices are available under Account Settings > Billing > Invoice History. You can download them in PDF format.',
        'author': 'billing',
        'date': '2023-08-14',
        'views': 276,
        'lang': 'de',
        'solution_id': 1008
    }
]

CATEGORIES = [
    {'id': 1, 'name': 'General', 'description': 'General questions and information'},
    {'id': 2, 'name': 'Account', 'description': 'Account management and settings'},
    {'id': 3, 'name': 'Technical', 'description': 'Technical support and troubleshooting'},
    {'id': 4, 'name': 'Billing', 'description': 'Billing and payment questions'},
]

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'de': 'Deutsch',
    'fr': 'Francais',
    'es': 'Espanol',
    'pt': 'Portugues',
}


def get_faq_by_id(faq_id):
    for faq in FAQ_ENTRIES:
        if faq['id'] == faq_id:
            return faq
    return None


def get_faqs_by_category(cat_id):
    return [f for f in FAQ_ENTRIES if f['category_id'] == cat_id]


def get_category_by_id(cat_id):
    for c in CATEGORIES:
        if c['id'] == cat_id:
            return c
    return None


def render_header(title='Knowledge Base', active='home'):
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title} - KnowledgeBase</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="KnowledgeBase 3.1.11">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; }}
.navbar {{ background: #2c3e50; padding: 0 20px; display: flex; align-items: center; height: 56px; }}
.navbar a {{ color: #ecf0f1; text-decoration: none; padding: 0 15px; font-size: 14px; line-height: 56px; }}
.navbar a:hover {{ background: #34495e; }}
.navbar .brand {{ font-weight: bold; font-size: 18px; margin-right: 20px; }}
.navbar .nav-right {{ margin-left: auto; }}
.container {{ max-width: 960px; margin: 0 auto; padding: 20px; }}
.search-bar {{ background: #3498db; padding: 30px 20px; text-align: center; }}
.search-bar input {{ width: 60%; padding: 10px 15px; border: none; border-radius: 4px; font-size: 16px; }}
.search-bar button {{ padding: 10px 20px; background: #2c3e50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
.card {{ background: white; border-radius: 4px; padding: 20px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.card h2 {{ margin-bottom: 10px; font-size: 18px; }}
.card h2 a {{ color: #2c3e50; text-decoration: none; }}
.card h2 a:hover {{ color: #3498db; }}
.card p {{ color: #666; line-height: 1.6; }}
.card .meta {{ font-size: 12px; color: #999; margin-top: 8px; }}
.card .meta span {{ margin-right: 15px; }}
.breadcrumb {{ background: #ecf0f1; padding: 10px 20px; font-size: 13px; }}
.breadcrumb a {{ color: #3498db; text-decoration: none; }}
.btn {{ display: inline-block; padding: 8px 16px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; font-size: 14px; }}
.btn:hover {{ background: #2980b9; }}
.btn-secondary {{ background: #95a5a6; }}
.btn-secondary:hover {{ background: #7f8c8d; }}
.form-group {{ margin-bottom: 15px; }}
.form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; font-size: 14px; }}
.form-group input, .form-group textarea, .form-group select {{ width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }}
.form-group textarea {{ resize: vertical; }}
.sidebar {{ float: right; width: 280px; }}
.content-main {{ margin-right: 300px; }}
.tag-cloud {{ padding: 10px 0; }}
.tag-cloud a {{ display: inline-block; padding: 3px 8px; margin: 2px; background: #ecf0f1; border-radius: 3px; font-size: 12px; color: #2c3e50; text-decoration: none; }}
.tag-cloud a:hover {{ background: #3498db; color: white; }}
.faq-list {{ list-style: none; }}
.faq-list li {{ padding: 12px 0; border-bottom: 1px solid #eee; }}
.faq-list li:last-child {{ border-bottom: none; }}
.faq-list a {{ color: #2c3e50; text-decoration: none; font-size: 15px; }}
.faq-list a:hover {{ color: #3498db; }}
.faq-list .views {{ color: #999; font-size: 12px; margin-left: 8px; }}
.category-grid {{ display: flex; flex-wrap: wrap; gap: 15px; }}
.category-card {{ flex: 1; min-width: 200px; background: white; padding: 20px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.category-card h3 {{ margin-bottom: 8px; }}
.category-card h3 a {{ color: #2c3e50; text-decoration: none; }}
.category-card h3 a:hover {{ color: #3498db; }}
.alert {{ padding: 12px 15px; border-radius: 4px; margin-bottom: 15px; }}
.alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
.alert-error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
.alert-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
footer {{ background: #2c3e50; color: #ecf0f1; padding: 20px; text-align: center; margin-top: 40px; font-size: 13px; }}
footer a {{ color: #3498db; text-decoration: none; }}
.hidden {{ display: none; }}
</style>
</head>
<body>
<nav class="navbar">
<a href="/" class="brand">KnowledgeBase</a>
<a href="/" {home_active}>Home</a>
<a href="/categories" {cat_active}>Categories</a>
<a href="/search" {search_active}>Search</a>
<a href="/add" {add_active}>Add FAQ</a>
<span class="nav-right">
<a href="/login">Login</a>
</span>
</nav>'''.format(
        title=title,
        home_active='style="background:#34495e"' if active == 'home' else '',
        cat_active='style="background:#34495e"' if active == 'categories' else '',
        search_active='style="background:#34495e"' if active == 'search' else '',
        add_active='style="background:#34495e"' if active == 'add' else '',
    )


def render_footer():
    return '''<footer>
<p>&copy; 2023 KnowledgeBase powered by KnowledgeBase 3.1.11</p>
<p><a href="/">Home</a> | <a href="/categories">Categories</a> | <a href="/sitemap">Sitemap</a> | <a href="/contact">Contact</a></p>
</footer>
</body>
</html>'''


def render_search_section(term=''):
    return '''<section class="search-bar">
<form action="/search" method="get">
<input type="text" name="q" placeholder="Search knowledge base..." value="{term}" autocomplete="off">
<button type="submit">Search</button>
</form>
</section>'''.format(term=cgi.escape(term, quote=True))


@app.route('/')
def index():
    html = render_header('Home', 'home')
    html += render_search_section()
    html += '<div class="container">'

    # Top FAQs
    html += '<div class="card"><h2>Most Popular Questions</h2><ul class="faq-list">'
    sorted_faqs = sorted(FAQ_ENTRIES, key=lambda x: x['views'], reverse=True)[:5]
    for faq in sorted_faqs:
        html += '<li><a href="/faq?id={id}&cat={cat}">{question}</a><span class="views">({views} views)</span></li>'.format(
            id=faq['id'], cat=faq['category_id'],
            question=cgi.escape(faq['question']),
            views=faq['views']
        )
    html += '</ul></div>'

    # Categories
    html += '<h2 style="margin-bottom:15px">Browse by Category</h2>'
    html += '<div class="category-grid">'
    for cat in CATEGORIES:
        count = len(get_faqs_by_category(cat['id']))
        html += '<div class="category-card"><h3><a href="/categories?id={id}">{name}</a></h3><p>{desc}</p><p style="font-size:12px;color:#999">{count} articles</p></div>'.format(
            id=cat['id'], name=cgi.escape(cat['name']),
            desc=cgi.escape(cat['description']), count=count
        )
    html += '</div>'

    html += '</div>'
    html += render_footer()
    return html


@app.route('/faq')
def faq_view():
    faq_id = request.args.get('id', type=int)
    cat_id = request.args.get('cat', type=int)
    content_lang = request.args.get('contentlang', 'en')

    if not faq_id:
        return redirect('/')

    faq = get_faq_by_id(faq_id)
    if not faq:
        html = render_header('Not Found')
        html += '<div class="container"><div class="card"><h2>FAQ not found</h2><p>The requested FAQ entry does not exist.</p></div></div>'
        html += render_footer()
        return html, 404

    category = get_category_by_id(faq['category_id']) or {'name': 'Unknown'}

    html = render_header(faq['question'])
    html += '<div class="breadcrumb"><a href="/">Home</a> &raquo; <a href="/categories?id={cat_id}">{cat_name}</a> &raquo; {question}</div>'.format(
        cat_id=faq['category_id'],
        cat_name=cgi.escape(category['name']),
        question=cgi.escape(faq['question'])
    )
    html += '<div class="container">'
    html += '<div class="card">'
    html += '<div style="float:right"><a class="btn btn-secondary" href="/faq?id={id}&cat={cat}" style="font-size:12px">ID #{solution_id}</a></div>'.format(
        id=faq['id'], cat=faq['category_id'], solution_id=faq['solution_id']
    )
    html += '<h2>{question}</h2>'.format(question=cgi.escape(faq['question']))
    html += '<div class="meta"><span>Author: {author}</span><span>Date: {date}</span><span>{views} views</span></div>'.format(
        author=cgi.escape(faq['author']),
        date=cgi.escape(faq['date']),
        views=faq['views']
    )
    html += '<hr style="margin:15px 0;border:none;border-top:1px solid #eee">'
    html += '<p>{answer}</p>'.format(answer=cgi.escape(faq['answer']))
    html += '</div>'

    # Action links (like phpMyFAQ's sendToFriend, PDF export, etc.)
    html += '<div class="card">'
    html += '<span style="margin-right:15px"><a href="/recommend?cat={cat}&id={id}&contentlang={lang}">&#9993; Recommend this FAQ</a></span>'.format(
        cat=faq['category_id'], id=faq['id'], lang=cgi.escape(faq.get('lang', 'en'), quote=True)
    )
    html += '<span style="margin-right:15px"><a href="/export?id={id}&format=html">&#128196; Export as HTML</a></span>'.format(id=faq['id'])
    html += '<span><a href="/print?id={id}">&#128424; Print version</a></span>'.format(id=faq['id'])
    html += '</div>'

    html += '</div>'
    html += render_footer()
    return html


@app.route('/recommend')
def recommend():
    """Recommend FAQ to a friend - mirrors phpMyFAQ send2friend functionality"""
    cat_id = request.args.get('cat', type=int, default=1)
    faq_id = request.args.get('id', type=int, default=1)
    content_lang = request.args.get('contentlang', '')

    faq = get_faq_by_id(faq_id)
    if not faq:
        faq = FAQ_ENTRIES[0]

    recommend_link = '/faq?id={id}&cat={cat}&contentlang={lang}'.format(
        id=faq_id, cat=cat_id, lang=urllib.quote(content_lang.encode('utf-8'))
    )

    html = render_header('Recommend FAQ', 'home')
    html += '<div class="breadcrumb"><a href="/">Home</a> &raquo; Recommend this FAQ</div>'
    html += '<div class="container">'
    html += '<div class="card">'
    html += '<h2>Recommend this FAQ to a Friend</h2>'
    html += '<form id="recommendForm" action="/submit-recommendation" method="post">'
    html += '<input type="hidden" name="link" value="{link}" />'.format(link=cgi.escape(recommend_link, quote=True))

    # contentlang is inserted into the value attribute without sanitization
    html += '<input type="hidden" name="contentlang" id="contentlang" value="' + content_lang + '" />'

    html += '<div class="form-group">'
    html += '<label for="sender_name">Your Name</label>'
    html += '<input type="text" name="sender_name" id="sender_name" required placeholder="Enter your name" />'
    html += '</div>'
    html += '<div class="form-group">'
    html += '<label for="sender_email">Your Email</label>'
    html += '<input type="email" name="sender_email" id="sender_email" required placeholder="Enter your email" />'
    html += '</div>'
    html += '<div class="form-group">'
    html += '<label for="recipient_email">Friend\'s Email</label>'
    html += '<input type="email" name="recipient_email" id="recipient_email" required placeholder="Enter friend\'s email" />'
    html += '</div>'
    html += '<div class="form-group">'
    html += '<label>FAQ Reference</label>'
    html += '<p style="padding:0"><em>{link}</em></p>'.format(link=cgi.escape(recommend_link))
    html += '</div>'
    html += '<div class="form-group">'
    html += '<label for="message">Personal Message (optional)</label>'
    html += '<textarea name="message" id="message" rows="4" placeholder="Add a personal message..."></textarea>'
    html += '</div>'
    html += '<button type="submit" class="btn">Send Recommendation</button>'
    html += '</form>'
    html += '</div>'

    # Run automated content compliance check on the rendered page
    xss_result = _run_compliance_scan(html)
    if xss_result:
        html += '<div class="card">'
        html += '<p>{0}</p>'.format(xss_result)
        html += '</div>'

    html += '</div>'
    html += render_footer()

    response = make_response(html)
    response.headers['X-XSS-Protection'] = '0'
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response


def _run_compliance_scan(page_html):
    """Run headless browser compliance check on rendered content."""
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    local_url = 'http://localhost:5000/' + fn
    result_text = None

    try:
        with open(fn, 'w') as of:
            of.write(page_html)

        proc = subprocess.Popen(
            ["timeout", "10", "phantomjs", "check_preview.js"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        proc.stdin.write(local_url + '\n' + flag_value + '\n')
        proc.stdin.close()
        output = proc.stdout.read().strip()
        proc.wait()

        # Check each line of output for the flag
        for line in output.split('\n'):
            line = line.strip()
            if line and 'FLAG{' in line:
                result_text = line
                break
    except Exception:
        pass
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    return result_text


@app.route('/submit-recommendation', methods=['POST'])
def submit_recommendation():
    """Process the recommendation form submission"""
    sender = request.form.get('sender_name', '')
    sender_email = request.form.get('sender_email', '')
    recipient = request.form.get('recipient_email', '')
    content_lang = request.form.get('contentlang', 'en')
    message = request.form.get('message', '')

    html = render_header('Recommendation Sent')
    html += '<div class="container">'
    html += '<div class="alert alert-success">Your recommendation has been sent successfully.</div>'
    html += '<div class="card"><p>A notification has been queued for delivery.</p>'
    html += '<p><a href="/">Return to Home</a></p></div>'
    html += '</div>'
    html += render_footer()
    return html


@app.route('/categories')
def categories():
    cat_id = request.args.get('id', type=int)

    if cat_id:
        category = get_category_by_id(cat_id)
        if not category:
            return redirect('/categories')

        faqs = get_faqs_by_category(cat_id)
        html = render_header(category['name'], 'categories')
        html += '<div class="breadcrumb"><a href="/">Home</a> &raquo; <a href="/categories">Categories</a> &raquo; {name}</div>'.format(
            name=cgi.escape(category['name'])
        )
        html += '<div class="container">'
        html += '<h2 style="margin-bottom:15px">{name}</h2>'.format(name=cgi.escape(category['name']))
        html += '<p style="color:#666;margin-bottom:15px">{desc}</p>'.format(desc=cgi.escape(category['description']))

        if faqs:
            for faq in faqs:
                html += '<div class="card"><h2><a href="/faq?id={id}&cat={cat}">{question}</a></h2>'.format(
                    id=faq['id'], cat=faq['category_id'], question=cgi.escape(faq['question'])
                )
                html += '<p>{answer}</p>'.format(answer=cgi.escape(faq['answer'][:150]) + '...')
                html += '<div class="meta"><span>Author: {author}</span><span>{views} views</span></div>'.format(
                    author=cgi.escape(faq['author']), views=faq['views']
                )
                html += '</div>'
        else:
            html += '<div class="card"><p>No articles in this category.</p></div>'

        html += '</div>'
        html += render_footer()
        return html

    html = render_header('Categories', 'categories')
    html += render_search_section()
    html += '<div class="container">'
    html += '<h2 style="margin-bottom:15px">All Categories</h2>'
    html += '<div class="category-grid">'
    for cat in CATEGORIES:
        count = len(get_faqs_by_category(cat['id']))
        html += '<div class="category-card"><h3><a href="/categories?id={id}">{name}</a></h3><p>{desc}</p><p style="font-size:12px;color:#999">{count} articles</p></div>'.format(
            id=cat['id'], name=cgi.escape(cat['name']),
            desc=cgi.escape(cat['description']), count=count
        )
    html += '</div></div>'
    html += render_footer()
    return html


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    html = render_header('Search', 'search')
    html += render_search_section(query)
    html += '<div class="container">'

    if query:
        results = [f for f in FAQ_ENTRIES if query.lower() in f['question'].lower() or query.lower() in f['answer'].lower()]
        html += '<h2 style="margin-bottom:15px">Search Results for "{0}"</h2>'.format(cgi.escape(query))
        if results:
            for faq in results:
                html += '<div class="card"><h2><a href="/faq?id={id}&cat={cat}">{question}</a></h2>'.format(
                    id=faq['id'], cat=faq['category_id'], question=cgi.escape(faq['question'])
                )
                html += '<p>{answer}</p>'.format(answer=cgi.escape(faq['answer'][:150]) + '...')
                html += '<div class="meta"><span>Category: {cat}</span><span>{views} views</span></div>'.format(
                    cat=cgi.escape(faq['category']), views=faq['views']
                )
                html += '</div>'
        else:
            html += '<div class="card"><p>No results found for your query.</p></div>'
    else:
        html += '<h2 style="margin-bottom:15px">Search</h2>'
        html += '<div class="card"><p>Enter a search term to find FAQ articles.</p></div>'

        # Popular tags
        html += '<div class="card"><h2>Popular Tags</h2><div class="tag-cloud">'
        tags = ['password', 'account', 'browser', 'upload', 'security', '2fa', 'billing', 'payment', 'invoice', 'profile']
        for tag in tags:
            html += '<a href="/search?q={tag}">{tag}</a>'.format(tag=tag)
        html += '</div></div>'

    html += '</div>'
    html += render_footer()
    return html


@app.route('/export')
def export_faq():
    faq_id = request.args.get('id', type=int)
    fmt = request.args.get('format', 'html')

    if not faq_id:
        return redirect('/')

    faq = get_faq_by_id(faq_id)
    if not faq:
        return 'FAQ not found', 404

    if fmt == 'html':
        content = '''<!DOCTYPE html>
<html>
<head><title>{question}</title><meta charset="utf-8"></head>
<body>
<h1>{question}</h1>
<p>{answer}</p>
<p>Author: {author} | Date: {date}</p>
</body>
</html>'''.format(
            question=cgi.escape(faq['question']),
            answer=cgi.escape(faq['answer']),
            author=cgi.escape(faq['author']),
            date=cgi.escape(faq['date'])
        )
        response = make_response(content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename="faq-{0}.html"'.format(faq_id)
        return response

    return 'Unsupported format', 400


@app.route('/print')
def print_faq():
    faq_id = request.args.get('id', type=int)
    if not faq_id:
        return redirect('/')
    faq = get_faq_by_id(faq_id)
    if not faq:
        return 'FAQ not found', 404

    html = '''<!DOCTYPE html>
<html>
<head><title>{question} - Print</title><meta charset="utf-8">
<style>body {{ font-family: serif; max-width: 700px; margin: 40px auto; }} h1 {{ font-size: 24px; }} .meta {{ color: #666; font-size: 13px; }}</style>
</head>
<body>
<h1>{question}</h1>
<p class="meta">Category: {category} | Author: {author} | Date: {date}</p>
<hr>
<p>{answer}</p>
</body>
</html>'''.format(
        question=cgi.escape(faq['question']),
        category=cgi.escape(faq['category']),
        author=cgi.escape(faq['author']),
        date=cgi.escape(faq['date']),
        answer=cgi.escape(faq['answer'])
    )
    return html


@app.route('/add')
def add_faq():
    html = render_header('Submit FAQ', 'add')
    html += '<div class="container">'
    html += '<div class="card">'
    html += '<h2>Submit a New FAQ Entry</h2>'
    html += '<p style="margin-bottom:15px;color:#666">Please log in to submit new FAQ entries. <a href="/login">Log in here</a>.</p>'
    html += '</div></div>'
    html += render_footer()
    return html


@app.route('/login')
def login():
    html = render_header('Login')
    html += '<div class="container">'
    html += '<div class="card" style="max-width:400px;margin:0 auto">'
    html += '<h2>Login</h2>'
    html += '<form method="post" action="/login">'
    html += '<div class="form-group"><label for="username">Username</label><input type="text" name="username" id="username" required></div>'
    html += '<div class="form-group"><label for="password">Password</label><input type="password" name="password" id="password" required></div>'
    html += '<button type="submit" class="btn">Sign In</button>'
    html += '</form>'
    html += '</div></div>'
    html += render_footer()
    return html


@app.route('/login', methods=['POST'])
def login_post():
    html = render_header('Login')
    html += '<div class="container">'
    html += '<div class="alert alert-error">Invalid username or password.</div>'
    html += '<div class="card" style="max-width:400px;margin:0 auto">'
    html += '<h2>Login</h2>'
    html += '<form method="post" action="/login">'
    html += '<div class="form-group"><label for="username">Username</label><input type="text" name="username" id="username" required></div>'
    html += '<div class="form-group"><label for="password">Password</label><input type="password" name="password" id="password" required></div>'
    html += '<button type="submit" class="btn">Sign In</button>'
    html += '</form>'
    html += '</div></div>'
    html += render_footer()
    return html


@app.route('/sitemap')
def sitemap():
    html = render_header('Sitemap')
    html += '<div class="container">'
    html += '<div class="card"><h2>Sitemap</h2>'
    html += '<ul style="list-style:none">'
    html += '<li><a href="/">Home</a></li>'
    html += '<li><a href="/categories">Categories</a></li>'
    html += '<li><a href="/search">Search</a></li>'
    for cat in CATEGORIES:
        html += '<li style="margin-left:20px"><a href="/categories?id={id}">{name}</a></li>'.format(
            id=cat['id'], name=cgi.escape(cat['name'])
        )
    for faq in FAQ_ENTRIES:
        html += '<li style="margin-left:40px"><a href="/faq?id={id}&cat={cat}">{question}</a></li>'.format(
            id=faq['id'], cat=faq['category_id'], question=cgi.escape(faq['question'])
        )
    html += '</ul></div></div>'
    html += render_footer()
    return html


@app.route('/contact')
def contact():
    html = render_header('Contact')
    html += '<div class="container">'
    html += '<div class="card"><h2>Contact Us</h2>'
    html += '<p>For support inquiries, please email <a href="mailto:support@example.com">support@example.com</a></p>'
    html += '</div></div>'
    html += render_footer()
    return html


@app.errorhandler(404)
def page_not_found(e):
    html = render_header('Page Not Found')
    html += '<div class="container"><div class="card"><h2>404 - Page Not Found</h2><p>The requested page could not be found. <a href="/">Return to home</a>.</p></div></div>'
    html += render_footer()
    return html, 404


@app.errorhandler(500)
def internal_error(e):
    html = render_header('Error')
    html += '<div class="container"><div class="card"><h2>Internal Server Error</h2><p>An unexpected error occurred. Please try again later.</p></div></div>'
    html += render_footer()
    return html, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
