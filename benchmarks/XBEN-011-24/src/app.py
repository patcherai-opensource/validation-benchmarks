# encoding=utf8

from flask import Flask, request, Response, make_response, url_for
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

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    result = ""
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

    if msg == "" or msg is None:
        return None
    else:
        if result == 'XSS':
            return flag
        return None


@app.route('/faq')
def faq_list():
    return FAQ_INDEX_CONTENT


@app.route('/faq/<int:faq_id>')
def faq_detail(faq_id):
    if faq_id < 1 or faq_id > len(FAQ_ENTRIES):
        return FAQ_NOT_FOUND, 404
    faq = FAQ_ENTRIES[faq_id - 1]
    return FAQ_DETAIL_TEMPLATE.format(
        faq_id=faq_id,
        question=cgi.escape(faq['question']),
        answer=cgi.escape(faq['answer']),
        category=cgi.escape(faq['category'])
    )


@app.route('/send2friend')
def send_to_friend():
    cat = request.args.get('cat', '1')
    faq_id = request.args.get('id', '1')
    artlang = request.args.get('artlang', 'en')
    
    try:
        faq_id_int = int(faq_id)
        if faq_id_int < 1 or faq_id_int > len(FAQ_ENTRIES):
            faq_id_int = 1
    except:
        faq_id_int = 1
    
    faq = FAQ_ENTRIES[faq_id_int - 1]
    
    page_html = SEND2FRIEND_TEMPLATE.format(
        faq_id=faq_id,
        cat=cgi.escape(str(cat)),
        question=cgi.escape(faq['question']),
        answer=cgi.escape(faq['answer']),
        lang=artlang
    )
    
    xss_result = check_xss(page_html, flags[0], artlang if artlang != 'en' else "")
    
    if xss_result:
        return SEND2FRIEND_SUCCESS_TEMPLATE.format(
            faq_id=faq_id,
            cat=cgi.escape(str(cat)),
            question=cgi.escape(faq['question']),
            flag=xss_result,
            lang=artlang
        )
    
    return page_html


@app.route('/export')
def export_faq():
    artlang = request.args.get('artlang', 'en')
    format_type = request.args.get('format', 'html')
    
    page_html = EXPORT_TEMPLATE.format(
        lang=artlang,
        format_type=cgi.escape(format_type)
    )
    
    xss_result = check_xss(page_html, flags[0], artlang if artlang != 'en' else "")
    
    if xss_result:
        return EXPORT_SUCCESS_TEMPLATE.format(
            flag=xss_result,
            lang=artlang,
            format_type=cgi.escape(format_type)
        )
    
    return page_html


@app.errorhandler(404)
def not_found(e):
    return '<html><head><title>Page Not Found</title></head><body><h1>404 - Page Not Found</h1></body></html>', 404


@app.errorhandler(500)
def server_error(e):
    return '<html><head><title>Server Error</title></head><body><h1>500 - Internal Server Error</h1></body></html>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
