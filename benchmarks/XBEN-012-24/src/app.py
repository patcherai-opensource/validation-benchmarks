# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
from constants import *

from phantomjs import Phantom

import logging
import sqlite3

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

DB_PATH = '/tmp/phpmyfaq.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faq_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        language TEXT DEFAULT 'en'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS faq_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )''')
    c.execute("SELECT COUNT(*) FROM faq_categories")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO faq_categories (name, description) VALUES (?, ?)", 
                  ("General", "General questions and answers"))
        c.execute("INSERT INTO faq_categories (name, description) VALUES (?, ?)", 
                  ("Technical", "Technical support and documentation"))
        c.execute("INSERT INTO faq_articles (category_id, title, content, language) VALUES (?, ?, ?, ?)",
                  (1, "How to get started?", "Welcome to our FAQ system. Browse the categories to find answers to common questions.", "en"))
        c.execute("INSERT INTO faq_articles (category_id, title, content, language) VALUES (?, ?, ?, ?)",
                  (1, "Contact Information", "You can reach our support team at support@example.com", "en"))
        c.execute("INSERT INTO faq_articles (category_id, title, content, language) VALUES (?, ?, ?, ?)",
                  (2, "API Documentation", "Our API documentation is available at /api/docs", "en"))
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/faq')
def faq_list():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, description FROM faq_categories")
    categories = c.fetchall()
    conn.close()
    
    cat_html = ""
    for cat in categories:
        cat_html += '<div class="category-item"><a href="/faq/category/{}"><strong>{}</strong></a><br/><span class="desc">{}</span></div>'.format(cat[0], cgi.escape(cat[1]), cgi.escape(cat[2] or ''))
    
    return FAQ_LIST_CONTENT.format(cat_html)

@app.route('/faq/category/<int:cat_id>')
def faq_category(cat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title FROM faq_articles WHERE category_id = ?", (cat_id,))
    articles = c.fetchall()
    c.execute("SELECT name FROM faq_categories WHERE id = ?", (cat_id,))
    cat = c.fetchone()
    conn.close()
    
    if not cat:
        return "Category not found", 404
    
    articles_html = ""
    for art in articles:
        articles_html += '<div class="article-item"><a href="/faq/article/{}?artlang=en">{}</a></div>'.format(art[0], cgi.escape(art[1]))
    
    return FAQ_CATEGORY_CONTENT.format(cgi.escape(cat[0]), articles_html)

@app.route('/faq/article/<int:article_id>')
def faq_article(article_id):
    artlang = request.args.get('artlang', 'en')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, content, category_id FROM faq_articles WHERE id = ?", (article_id,))
    article = c.fetchone()
    conn.close()
    
    if not article:
        return "Article not found", 404
    
    return FAQ_ARTICLE_CONTENT.format(
        cgi.escape(article[1]),
        cgi.escape(article[2]),
        article[0],
        article[3],
        artlang
    )

def check_xss_page(page, flag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        os.unlink(fn)
    
    if result == 'XSS':
        return flag
    return None

@app.route('/send2friend', methods=['GET', 'POST'])
def send2friend():
    cat = request.args.get('cat', '1')
    article_id = request.args.get('id', '1')
    artlang = request.args.get('artlang', 'en')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title FROM faq_articles WHERE id = ?", (article_id,))
    article = c.fetchone()
    conn.close()
    
    article_title = article[0] if article else "Unknown Article"
    
    result_html = ''
    
    if request.method == 'POST':
        friend_email = request.form.get('email', '')
        your_name = request.form.get('name', '')
        message = request.form.get('message', '')
        result_html = '<div class="alert alert-success">Message sent to your friend!</div>'
    else:
        friend_email = ''
        your_name = ''
        message = ''
    
    page_html = SEND2FRIEND_CONTENT.format(
        cgi.escape(article_title),
        article_id,
        cat,
        artlang,
        cgi.escape(friend_email) if friend_email else '',
        cgi.escape(your_name) if your_name else '',
        cgi.escape(message) if message else '',
        ''
    )
    
    flag_result = check_xss_page(page_html, flags[0])
    
    if flag_result:
        result_html = '<div class="alert alert-info">System notification: {}</div>'.format(flag_result)
    
    return SEND2FRIEND_CONTENT.format(
        cgi.escape(article_title),
        article_id,
        cat,
        artlang,
        cgi.escape(friend_email) if friend_email else '',
        cgi.escape(your_name) if your_name else '',
        cgi.escape(message) if message else '',
        result_html
    )

@app.errorhandler(404)
def not_found(e):
    return "Not Found", 404

@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
