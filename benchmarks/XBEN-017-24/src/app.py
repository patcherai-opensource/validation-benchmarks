# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, render_template_string
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
from constants import *

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

@app.errorhandler(500)
def internal_error(error):
    return "Internal Server Error", 500

@app.errorhandler(404)
def not_found(error):
    return "Not Found", 404

@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss(page, flag, user_input):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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

    return result


@app.route('/wiki/upload')
def file_upload_form():
    file_param = request.args.get('file', '')
    
    page_html = UPLOAD_FORM_CONTENT.format(file_param)
    
    if file_param:
        result = check_xss(page_html, flags[0], file_param)
        if result == 'XSS':
            return UPLOAD_SUCCESS_CONTENT.format(flags[0])
    
    return page_html


@app.route('/wiki')
def wiki_home():
    return WIKI_HOME_CONTENT


@app.route('/wiki/pages')
def wiki_pages():
    return WIKI_PAGES_CONTENT


@app.route('/wiki/search')
def wiki_search():
    q = request.args.get('q', '')
    return WIKI_SEARCH_CONTENT.format(cgi.escape(q) if q else '')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
