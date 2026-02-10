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

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_value = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

FAQ_ARTICLES = {
    1: {"title": "How do I reset my password?", "content": "Navigate to Settings > Security > Reset Password and follow the instructions."},
    2: {"title": "What payment methods are accepted?", "content": "We accept Visa, MasterCard, American Express, and PayPal."},
    3: {"title": "How can I contact support?", "content": "You can reach our support team at support@example.com or via the contact form."},
    4: {"title": "What is your refund policy?", "content": "Full refunds are available within 30 days of purchase for unused items."},
}

@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/')
def index():
    return FAQ_INDEX_CONTENT

@app.route('/faq')
def faq_list():
    return FAQ_LIST_CONTENT.format(faq_items=generate_faq_list())

def generate_faq_list():
    items = ""
    for faq_id, faq in FAQ_ARTICLES.items():
        items += '<li><a href="/faq/{0}">{1}</a></li>'.format(faq_id, cgi.escape(faq['title']))
    return items

@app.route('/faq/<int:faq_id>')
def faq_detail(faq_id):
    if faq_id not in FAQ_ARTICLES:
        return "FAQ not found", 404
    faq = FAQ_ARTICLES[faq_id]
    return FAQ_DETAIL_CONTENT.format(
        faq_id=faq_id,
        title=cgi.escape(faq['title']),
        content=cgi.escape(faq['content'])
    )

def check_xss_execution(page, user_input):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('APP_BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    result = None
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

@app.route('/send2friend.php')
def send2friend():
    cat = request.args.get('cat', '')
    faq_id = request.args.get('id', '')
    artlang = request.args.get('artlang', 'en')
    
    faq_id_int = None
    try:
        faq_id_int = int(faq_id) if faq_id else None
    except ValueError:
        pass
    
    faq_title = ""
    faq_content = ""
    if faq_id_int and faq_id_int in FAQ_ARTICLES:
        faq_title = FAQ_ARTICLES[faq_id_int]['title']
        faq_content = FAQ_ARTICLES[faq_id_int]['content']
    
    page_html = SEND2FRIEND_CONTENT.format(
        cat=cgi.escape(cat) if cat else "",
        faq_id=cgi.escape(faq_id) if faq_id else "",
        artlang=artlang,
        faq_title=cgi.escape(faq_title),
        faq_content=cgi.escape(faq_content)
    )
    
    if artlang and artlang != 'en':
        xss_result = check_xss_execution(page_html, artlang)
        if xss_result == 'XSS':
            return SEND2FRIEND_SUCCESS_CONTENT.format(
                flag=flag_value,
                cat=cgi.escape(cat) if cat else "",
                faq_id=cgi.escape(faq_id) if faq_id else "",
                artlang=artlang,
                faq_title=cgi.escape(faq_title),
                faq_content=cgi.escape(faq_content)
            )
    
    return page_html

@app.route('/send2friend.php', methods=['POST'])
def send2friend_submit():
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    friend_email = request.form.get('friend_email', '')
    message = request.form.get('message', '')
    
    return SEND2FRIEND_CONFIRM_CONTENT.format(
        friend_email=cgi.escape(friend_email)
    )

@app.errorhandler(404)
def not_found(e):
    return "Not Found", 404

@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
