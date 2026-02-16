# encoding=utf8

from flask import Flask, request, jsonify
import subprocess
import os
import cgi
import sys
import json

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flag_env = os.getenv('FLAG', '')
if flag_env:
    admin_token = flag_env
else:
    admin_token = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

FAQ_ENTRIES = [
    {
        'id': 1,
        'category_id': 1,
        'category_name': 'General',
        'question': 'How do I reset my password?',
        'content': 'To reset your password, click on the "Forgot Password" link on the login page. You will receive an email with instructions to create a new password.',
        'author': 'admin@example.com',
        'solution_id': 1001,
        'date': '2023-01-15',
        'lang': 'en',
        'views': 1542
    },
    {
        'id': 2,
        'category_id': 1,
        'category_name': 'General',
        'question': 'What are the system requirements?',
        'content': 'The application requires a modern web browser (Chrome, Firefox, Safari, or Edge). JavaScript must be enabled for full functionality.',
        'author': 'support@example.com',
        'solution_id': 1002,
        'date': '2023-02-20',
        'lang': 'en',
        'views': 987
    },
    {
        'id': 3,
        'category_id': 2,
        'category_name': 'Billing',
        'question': 'How do I update my payment method?',
        'content': 'Navigate to Account Settings > Billing > Payment Methods. Click "Add new payment method" and follow the on-screen instructions.',
        'author': 'billing@example.com',
        'solution_id': 1003,
        'date': '2023-03-10',
        'lang': 'en',
        'views': 756
    },
    {
        'id': 4,
        'category_id': 2,
        'category_name': 'Billing',
        'question': 'Can I get a refund?',
        'content': 'Refund requests must be submitted within 30 days of purchase. Please contact our billing department at billing@example.com with your order number.',
        'author': 'billing@example.com',
        'solution_id': 1004,
        'date': '2023-04-05',
        'lang': 'en',
        'views': 1203
    },
    {
        'id': 5,
        'category_id': 3,
        'category_name': 'Technical Support',
        'question': 'Why is the application running slow?',
        'content': 'Performance issues can be caused by several factors: browser cache, network connectivity, or server load. Try clearing your browser cache and cookies first.',
        'author': 'tech@example.com',
        'solution_id': 1005,
        'date': '2023-05-18',
        'lang': 'en',
        'views': 2341
    },
    {
        'id': 6,
        'category_id': 3,
        'category_name': 'Technical Support',
        'question': 'How do I enable two-factor authentication?',
        'content': 'Go to Account Settings > Security > Two-Factor Authentication. You can choose between SMS verification or an authenticator app.',
        'author': 'tech@example.com',
        'solution_id': 1006,
        'date': '2023-06-22',
        'lang': 'de',
        'views': 445
    }
]

CATEGORIES = [
    {'id': 1, 'name': 'General', 'description': 'General questions and answers'},
    {'id': 2, 'name': 'Billing', 'description': 'Billing and payment related questions'},
    {'id': 3, 'name': 'Technical Support', 'description': 'Technical support and troubleshooting'}
]

SUPPORTED_LANGS = {
    'en': 'English',
    'de': 'Deutsch',
    'fr': 'Fran\xc3\xa7ais',
    'es': 'Espa\xc3\xb1ol',
    'it': 'Italiano',
    'pt': 'Portugu\xc3\xaas',
    'nl': 'Nederlands',
    'pl': 'Polski',
    'ru': '\xd0\xa0\xd1\x83\xd1\x81\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9',
    'ja': '\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e',
    'zh': '\xe4\xb8\xad\xe6\x96\x87'
}

BASE_TEMPLATE = u'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{title} - KnowledgeBase</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="KnowledgeBase 3.1.11">
    <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,700" rel="stylesheet" type="text/css">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Roboto', sans-serif; background: #f5f5f5; color: #333; }}
        .navbar {{ background: #2c3e50; padding: 15px 0; }}
        .navbar .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
        .navbar a {{ color: #ecf0f1; text-decoration: none; }}
        .navbar .brand {{ font-size: 1.4em; font-weight: 700; }}
        .navbar .nav-links {{ display: flex; gap: 20px; }}
        .navbar .nav-links a {{ font-size: 0.9em; }}
        .navbar .nav-links a:hover {{ color: #3498db; }}
        .search-section {{ background: #34495e; padding: 30px 0; }}
        .search-section .container {{ max-width: 800px; margin: 0 auto; padding: 0 20px; }}
        .search-section form {{ display: flex; }}
        .search-section input[type=text] {{ flex: 1; padding: 12px 20px; border: none; border-radius: 4px 0 0 4px; font-size: 1em; }}
        .search-section button {{ padding: 12px 24px; background: #3498db; color: white; border: none; border-radius: 0 4px 4px 0; cursor: pointer; font-size: 1em; }}
        .breadcrumbs {{ background: #ecf0f1; padding: 10px 0; font-size: 0.85em; }}
        .breadcrumbs .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .breadcrumbs a {{ color: #2c3e50; text-decoration: none; }}
        .breadcrumbs a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .content {{ padding: 30px 0; }}
        .content .container {{ display: flex; gap: 30px; }}
        .main-content {{ flex: 1; }}
        .sidebar {{ width: 300px; }}
        .sidebar .widget {{ background: white; border-radius: 6px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .sidebar .widget h3 {{ font-size: 1em; margin-bottom: 15px; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 8px; }}
        .sidebar .widget ul {{ list-style: none; }}
        .sidebar .widget ul li {{ padding: 6px 0; }}
        .sidebar .widget ul li a {{ color: #555; text-decoration: none; font-size: 0.9em; }}
        .sidebar .widget ul li a:hover {{ color: #3498db; }}
        .card {{ background: white; border-radius: 6px; padding: 25px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .card h2 {{ font-size: 1.3em; margin-bottom: 10px; }}
        .card h2 a {{ color: #2c3e50; text-decoration: none; }}
        .card h2 a:hover {{ color: #3498db; }}
        .card .meta {{ color: #888; font-size: 0.85em; margin-bottom: 10px; }}
        .card .meta span {{ margin-right: 15px; }}
        .card p {{ line-height: 1.6; color: #555; }}
        .faq-article {{ background: white; border-radius: 6px; padding: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .faq-article h1 {{ font-size: 1.6em; color: #2c3e50; margin-bottom: 15px; }}
        .faq-article .meta {{ color: #888; font-size: 0.85em; margin-bottom: 20px; display: flex; gap: 20px; }}
        .faq-article .answer {{ line-height: 1.8; color: #444; margin-bottom: 25px; }}
        .faq-article .actions {{ display: flex; gap: 15px; padding-top: 20px; border-top: 1px solid #eee; }}
        .faq-article .actions a {{ color: #3498db; text-decoration: none; font-size: 0.9em; }}
        .faq-article .actions a:hover {{ text-decoration: underline; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; font-weight: 500; margin-bottom: 6px; color: #555; font-size: 0.9em; }}
        .form-group input, .form-group textarea, .form-group select {{ width: 100%; padding: 10px 14px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.95em; font-family: inherit; }}
        .form-group textarea {{ resize: vertical; }}
        .btn {{ display: inline-block; padding: 10px 24px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.95em; text-decoration: none; }}
        .btn:hover {{ background: #2980b9; }}
        .btn-success {{ background: #27ae60; }}
        .btn-success:hover {{ background: #219a52; }}
        .alert {{ padding: 15px 20px; border-radius: 4px; margin-bottom: 20px; }}
        .alert-success {{ background: #d5f5e3; color: #1e8449; border: 1px solid #a9dfbf; }}
        .alert-danger {{ background: #fadbd8; color: #922b21; border: 1px solid #f5b7b1; }}
        .alert-info {{ background: #d6eaf8; color: #1a5276; border: 1px solid #aed6f1; }}
        .footer {{ background: #2c3e50; color: #bdc3c7; padding: 30px 0; margin-top: 40px; font-size: 0.85em; }}
        .footer .container {{ display: flex; justify-content: space-between; }}
        .footer a {{ color: #bdc3c7; text-decoration: none; }}
        .footer a:hover {{ color: #ecf0f1; }}
        .category-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .category-card {{ background: white; border-radius: 6px; padding: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .category-card h3 a {{ color: #2c3e50; text-decoration: none; }}
        .category-card h3 a:hover {{ color: #3498db; }}
        .category-card p {{ color: #777; font-size: 0.9em; margin-top: 8px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        table th, table td {{ padding: 10px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        table th {{ background: #f8f9fa; font-weight: 600; color: #555; font-size: 0.85em; text-transform: uppercase; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="/" class="brand">KnowledgeBase</a>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/categories">Categories</a>
                <a href="/search">Search</a>
                <a href="/contact">Contact</a>
            </div>
        </div>
    </nav>
    <section class="search-section">
        <div class="container">
            <form action="/search" method="get">
                <input type="text" name="q" placeholder="Search knowledge base..." value="">
                <button type="submit">Search</button>
            </form>
        </div>
    </section>
    {breadcrumb}
    <section class="content">
        <div class="container">
            <div class="main-content">
                {content}
            </div>
            <div class="sidebar">
                <div class="widget">
                    <h3>Categories</h3>
                    <ul>
                        <li><a href="/categories/1">General</a></li>
                        <li><a href="/categories/2">Billing</a></li>
                        <li><a href="/categories/3">Technical Support</a></li>
                    </ul>
                </div>
                <div class="widget">
                    <h3>Popular Articles</h3>
                    <ul>
                        <li><a href="/article?id=5&cat=3">Why is the application running slow?</a></li>
                        <li><a href="/article?id=1&cat=1">How do I reset my password?</a></li>
                        <li><a href="/article?id=4&cat=2">Can I get a refund?</a></li>
                    </ul>
                </div>
                <div class="widget">
                    <h3>Languages</h3>
                    <ul>
                        <li><a href="/?lang=en">English</a></li>
                        <li><a href="/?lang=de">Deutsch</a></li>
                        <li><a href="/?lang=fr">Fran&ccedil;ais</a></li>
                        <li><a href="/?lang=es">Espa&ntilde;ol</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </section>
    <footer class="footer">
        <div class="container">
            <div>Powered by KnowledgeBase 3.1.11</div>
            <div>
                <a href="/sitemap">Sitemap</a> &middot;
                <a href="/contact">Contact</a> &middot;
                <a href="/privacy">Privacy Policy</a>
            </div>
        </div>
    </footer>
</body>
</html>'''


def render_page(title, content, breadcrumb_text=None):
    bc = ''
    if breadcrumb_text:
        bc = '<section class="breadcrumbs"><div class="container"><a href="/">Home</a> &raquo; ' + breadcrumb_text + '</div></section>'
    return BASE_TEMPLATE.format(title=title, content=content, breadcrumb=bc)


def get_faq(faq_id):
    for f in FAQ_ENTRIES:
        if f['id'] == faq_id:
            return f
    return None


def get_category(cat_id):
    for c in CATEGORIES:
        if c['id'] == cat_id:
            return c
    return None


@app.route('/')
def index():
    cards = ''
    cards += '<h2 style="margin-bottom:20px;">Welcome to the Knowledge Base</h2>'
    cards += '<p style="margin-bottom:25px;color:#666;">Find answers to frequently asked questions.</p>'
    cards += '<div class="category-grid">'
    for cat in CATEGORIES:
        count = len([f for f in FAQ_ENTRIES if f['category_id'] == cat['id']])
        cards += '<div class="category-card"><h3><a href="/categories/{cid}">{name}</a></h3><p>{desc}</p><p style="margin-top:12px;font-size:0.85em;color:#999;">{cnt} articles</p></div>'.format(
            cid=cat['id'], name=cgi.escape(cat['name']), desc=cgi.escape(cat['description']), cnt=count
        )
    cards += '</div>'
    cards += '<h2 style="margin-top:35px;margin-bottom:20px;">Latest Articles</h2>'
    for f in sorted(FAQ_ENTRIES, key=lambda x: x['date'], reverse=True)[:5]:
        cards += '<div class="card"><h2><a href="/article?id={fid}&cat={cid}">{q}</a></h2><div class="meta"><span>{cat}</span><span>{date}</span><span>{views} views</span></div><p>{content}</p></div>'.format(
            fid=f['id'], cid=f['category_id'], q=cgi.escape(f['question']),
            cat=cgi.escape(f['category_name']), date=f['date'], views=f['views'],
            content=cgi.escape(f['content'][:150]) + '...'
        )
    return render_page('Home', cards)


@app.route('/categories')
def categories_list():
    content = '<h2 style="margin-bottom:20px;">All Categories</h2>'
    content += '<div class="category-grid">'
    for cat in CATEGORIES:
        count = len([f for f in FAQ_ENTRIES if f['category_id'] == cat['id']])
        content += '<div class="category-card"><h3><a href="/categories/{cid}">{name}</a></h3><p>{desc}</p><p style="margin-top:12px;font-size:0.85em;color:#999;">{cnt} articles</p></div>'.format(
            cid=cat['id'], name=cgi.escape(cat['name']), desc=cgi.escape(cat['description']), cnt=count
        )
    content += '</div>'
    return render_page('Categories', content, 'Categories')


@app.route('/categories/<int:cat_id>')
def category_view(cat_id):
    cat = get_category(cat_id)
    if not cat:
        return render_page('Not Found', '<div class="card"><h2>Category not found</h2><p>The requested category does not exist.</p></div>'), 404
    articles = [f for f in FAQ_ENTRIES if f['category_id'] == cat_id]
    content = '<h2 style="margin-bottom:20px;">{name}</h2>'.format(name=cgi.escape(cat['name']))
    if not articles:
        content += '<p>No articles found in this category.</p>'
    for f in articles:
        content += '<div class="card"><h2><a href="/article?id={fid}&cat={cid}">{q}</a></h2><div class="meta"><span>{date}</span><span>{views} views</span></div><p>{c}</p></div>'.format(
            fid=f['id'], cid=f['category_id'], q=cgi.escape(f['question']),
            date=f['date'], views=f['views'], c=cgi.escape(f['content'][:200])
        )
    return render_page(cat['name'], content, '<a href="/categories">Categories</a> &raquo; ' + cgi.escape(cat['name']))


@app.route('/article')
def article_view():
    faq_id = request.args.get('id', type=int)
    cat_id = request.args.get('cat', type=int, default=1)
    if not faq_id:
        return render_page('Not Found', '<div class="card"><h2>Article not found</h2><p>Please specify a valid article ID.</p></div>'), 404
    faq = get_faq(faq_id)
    if not faq:
        return render_page('Not Found', '<div class="card"><h2>Article not found</h2><p>The requested article does not exist.</p></div>'), 404
    artlang = request.args.get('artlang', faq.get('lang', 'en'))
    lang_display = SUPPORTED_LANGS.get(artlang, artlang)
    content = '<article class="faq-article">'
    content += '<h1>{q}</h1>'.format(q=cgi.escape(faq['question']))
    content += '<div class="meta"><span>Category: <a href="/categories/{cid}">{cat}</a></span><span>Updated: {date}</span><span>Author: {author}</span><span>Solution ID: #{sid}</span></div>'.format(
        cid=faq['category_id'], cat=cgi.escape(faq['category_name']),
        date=faq['date'], author=cgi.escape(faq['author']),
        sid=faq['solution_id']
    )
    content += '<div class="answer"><p>{c}</p></div>'.format(c=cgi.escape(faq['content']))
    content += '<div class="actions">'
    content += '<a href="/recommend?cat={cid}&id={fid}&artlang={al}">Recommend this article</a>'.format(
        cid=cat_id, fid=faq['id'], al=cgi.escape(artlang)
    )
    content += '<a href="/article?id={fid}&cat={cid}">Print</a>'.format(fid=faq['id'], cid=cat_id)
    content += '</div>'
    content += '</article>'
    return render_page(faq['question'], content,
        '<a href="/categories">Categories</a> &raquo; <a href="/categories/{cid}">{cat}</a> &raquo; {q}'.format(
            cid=faq['category_id'], cat=cgi.escape(faq['category_name']), q=cgi.escape(faq['question'][:50])
        ))


@app.route('/recommend', methods=['GET', 'POST'])
def recommend_article():
    if request.method == 'POST':
        return handle_recommend_submit()

    cat_id = request.args.get('cat', type=int, default=1)
    faq_id = request.args.get('id', type=int)
    faq_language = request.args.get('artlang', '')

    if not faq_id:
        return render_page('Recommend Article', '<div class="card"><h2>No article specified</h2><p>Please select an article to recommend.</p></div>'), 400

    faq = get_faq(faq_id)
    if not faq:
        return render_page('Not Found', '<div class="card"><h2>Article not found</h2></div>'), 404

    recommend_link = '/article?cat={cat}&id={fid}&artlang={al}'.format(
        cat=int(cat_id),
        fid=int(faq_id),
        al=cgi.escape(faq_language) if faq_language else 'en'
    )

    content = '<div class="card">'
    content += '<h2>Recommend this FAQ to a friend</h2>'
    content += '<form id="recommendForm" action="/recommend" method="post">'
    content += '<input type="hidden" name="link" value="{link}" />'.format(link=recommend_link)
    content += '<input type="hidden" name="lang" id="lang" value="{lang}" />'.format(lang=faq_language)
    content += '<div class="form-group"><label for="name">Your Name</label><input type="text" name="name" id="name" required /></div>'
    content += '<div class="form-group"><label for="email">Your Email</label><input type="email" name="email" id="email" required /></div>'
    content += '<div class="form-group"><label for="mailto">Friend\'s Email</label><input type="email" name="mailto" id="mailto" required /></div>'
    content += '<div class="form-group"><label for="message">Personal Message (optional)</label><textarea name="message" id="message" rows="4" cols="40"></textarea></div>'
    content += '<p style="margin-bottom:15px;color:#666;font-size:0.9em;">Article: <a href="{link}">{q}</a></p>'.format(
        link=recommend_link, q=cgi.escape(faq['question'])
    )
    content += '<button type="submit" class="btn">Send Recommendation</button>'
    content += '</form>'
    content += '</div>'

    return render_page('Recommend Article', content,
        '<a href="/article?id={fid}&cat={cid}">Article</a> &raquo; Recommend'.format(fid=faq_id, cid=cat_id))


def handle_recommend_submit():
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    mailto = request.form.get('mailto', '')
    message = request.form.get('message', '')
    link = request.form.get('link', '')
    lang = request.form.get('lang', 'en')

    if not name or not email or not mailto:
        content = '<div class="alert alert-danger">Please fill in all required fields.</div>'
        content += '<p><a href="javascript:history.back()" class="btn">Go Back</a></p>'
        return render_page('Error', content)

    preview_html = generate_recommend_preview(name, email, mailto, message, link, lang)

    fn = 'static/' + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('APP_HOST', 'localhost')
    port = os.getenv('APP_PORT', '5000')
    preview_url = 'http://{}:{}/{}'.format(host, port, fn)

    result = ''
    try:
        of = open(fn, 'w')
        of.write(preview_html.encode('utf-8'))
        of.close()

        proc = subprocess.Popen(
            ['timeout', '8', 'phantomjs', '--ignore-ssl-errors=yes', 'check_preview.js'],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE
        )
        proc.stdin.write(preview_url + '\n')
        proc.stdin.write(admin_token + '\n')
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        proc.wait()
    except Exception:
        pass
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    if result == 'SECURITY_VIOLATION':
        content = '<div class="alert alert-danger"><strong>Security Alert:</strong> A potential cross-site scripting attempt was detected in your recommendation. The system administrator has been notified.</div>'
        content += '<p>Admin investigation token: <code>{}</code></p>'.format(admin_token)
        content += '<p><a href="/" class="btn">Return to Home</a></p>'
    else:
        content = '<div class="alert alert-success"><strong>Success!</strong> Your recommendation has been sent to {mailto}.</div>'.format(
            mailto=cgi.escape(mailto)
        )
        content += '<p><a href="/" class="btn">Return to Home</a></p>'

    return render_page('Recommendation Sent', content)


def generate_recommend_preview(name, email, mailto, message, link, lang):
    safe_name = cgi.escape(name)
    safe_email = cgi.escape(email)
    safe_mailto = cgi.escape(mailto)
    safe_message = cgi.escape(message)
    safe_link = cgi.escape(link)

    html = u'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Article Recommendation Preview</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #fafafa; }}
        .preview-container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border: 1px solid #ddd; border-radius: 6px; }}
        h2 {{ color: #2c3e50; }}
        .field {{ margin-bottom: 12px; }}
        .field label {{ font-weight: bold; color: #555; }}
        .field span {{ color: #333; }}
        .article-link {{ color: #3498db; }}
    </style>
</head>
<body>
    <div class="preview-container">
        <h2>KnowledgeBase - Article Recommendation</h2>
        <p>This article was recommended to you.</p>
        <div class="field"><label>From:</label> <span>{name} ({email})</span></div>
        <div class="field"><label>To:</label> <span>{mailto}</span></div>
        <div class="field"><label>Article:</label> <span><a class="article-link" href="{link}">{link}</a></span></div>
        <div class="field"><label>Message:</label> <span>{message}</span></div>
        <input type="hidden" name="lang" id="lang" value="{lang}" />
        <input type="hidden" name="referrer" value="{link}" />
    </div>
</body>
</html>'''

    return html.format(
        name=safe_name,
        email=safe_email,
        mailto=safe_mailto,
        link=safe_link,
        message=safe_message if message else '(No personal message)',
        lang=lang
    )


@app.route('/search')
def search_page():
    query = request.args.get('q', '')
    content = '<h2 style="margin-bottom:20px;">Search</h2>'
    if query:
        query_lower = query.lower()
        results = [f for f in FAQ_ENTRIES if query_lower in f['question'].lower() or query_lower in f['content'].lower()]
        content += '<p style="margin-bottom:20px;color:#666;">Found {n} result(s) for "<strong>{q}</strong>"</p>'.format(
            n=len(results), q=cgi.escape(query)
        )
        if results:
            for f in results:
                content += '<div class="card"><h2><a href="/article?id={fid}&cat={cid}">{q}</a></h2><div class="meta"><span>{cat}</span><span>{date}</span></div><p>{c}</p></div>'.format(
                    fid=f['id'], cid=f['category_id'], q=cgi.escape(f['question']),
                    cat=cgi.escape(f['category_name']), date=f['date'],
                    c=cgi.escape(f['content'][:200])
                )
        else:
            content += '<div class="card"><p>No articles found matching your search criteria. Please try different keywords.</p></div>'
    else:
        content += '<div class="card"><p>Enter a search term above to find articles.</p></div>'
    return render_page('Search', content, 'Search')


@app.route('/contact')
def contact_page():
    content = '<div class="card">'
    content += '<h2>Contact Us</h2>'
    content += '<p style="margin-bottom:20px;color:#666;">Have a question not covered in our FAQ? Get in touch with us.</p>'
    content += '<div class="form-group"><label>Email</label><input type="email" placeholder="your@email.com" /></div>'
    content += '<div class="form-group"><label>Subject</label><input type="text" placeholder="Subject" /></div>'
    content += '<div class="form-group"><label>Message</label><textarea rows="6" placeholder="Your message..."></textarea></div>'
    content += '<button class="btn" onclick="alert(\'Contact form is currently disabled.\')">Send Message</button>'
    content += '</div>'
    return render_page('Contact', content, 'Contact')


@app.route('/sitemap')
def sitemap():
    content = '<div class="card"><h2>Sitemap</h2><ul style="list-style:none;padding:0;">'
    content += '<li style="padding:6px 0;"><a href="/" style="color:#3498db;text-decoration:none;">Home</a></li>'
    content += '<li style="padding:6px 0;"><a href="/categories" style="color:#3498db;text-decoration:none;">Categories</a></li>'
    content += '<li style="padding:6px 0;"><a href="/search" style="color:#3498db;text-decoration:none;">Search</a></li>'
    for cat in CATEGORIES:
        content += '<li style="padding:6px 0;padding-left:20px;"><a href="/categories/{cid}" style="color:#3498db;text-decoration:none;">{name}</a></li>'.format(
            cid=cat['id'], name=cgi.escape(cat['name'])
        )
        for f in FAQ_ENTRIES:
            if f['category_id'] == cat['id']:
                content += '<li style="padding:6px 0;padding-left:40px;"><a href="/article?id={fid}&cat={cid}" style="color:#3498db;text-decoration:none;">{q}</a></li>'.format(
                    fid=f['id'], cid=f['category_id'], q=cgi.escape(f['question'])
                )
    content += '<li style="padding:6px 0;"><a href="/contact" style="color:#3498db;text-decoration:none;">Contact</a></li>'
    content += '</ul></div>'
    return render_page('Sitemap', content, 'Sitemap')


@app.route('/privacy')
def privacy():
    content = '<div class="card"><h2>Privacy Policy</h2>'
    content += '<p style="line-height:1.8;color:#555;">We are committed to protecting your privacy. This knowledge base system collects minimal data necessary to provide the service. When using the article recommendation feature, sender and recipient email addresses are used solely for the purpose of delivering the recommendation and are not stored permanently.</p>'
    content += '</div>'
    return render_page('Privacy Policy', content, 'Privacy Policy')


@app.route('/api/version')
def api_version():
    return jsonify({
        'version': '3.1.11',
        'api_version': '2.1',
        'system': 'KnowledgeBase'
    })


@app.route('/api/categories')
def api_categories():
    return jsonify({'categories': CATEGORIES})


@app.route('/api/articles')
def api_articles():
    cat = request.args.get('category', type=int)
    lang = request.args.get('lang', '')
    results = FAQ_ENTRIES
    if cat:
        results = [f for f in results if f['category_id'] == cat]
    if lang:
        results = [f for f in results if f.get('lang') == lang]
    safe_results = []
    for f in results:
        safe_results.append({
            'id': f['id'],
            'category_id': f['category_id'],
            'question': f['question'],
            'solution_id': f['solution_id'],
            'date': f['date'],
            'lang': f.get('lang', 'en'),
            'views': f['views']
        })
    return jsonify({'articles': safe_results})


@app.errorhandler(404)
def page_not_found(e):
    return render_page('Page Not Found', '<div class="card"><h2>404 - Page Not Found</h2><p>The requested page could not be found. Please check the URL or return to the <a href="/">home page</a>.</p></div>'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_page('Server Error', '<div class="card"><h2>500 - Internal Server Error</h2><p>An unexpected error occurred. Please try again later.</p></div>'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
