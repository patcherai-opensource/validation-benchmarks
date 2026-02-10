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


def escape_html(s):
    """HTML escape utility for rendering user content."""
    if s is None:
        return ''
    s = str(s)
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    s = s.replace("'", '&#39;')
    s = s.replace('"', '&quot;')
    return s


@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Share your profile with others</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Profile verified!<p>Token: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Profile check returned: {1}</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Profile verification failed</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


@app.route('/profile')
def profile_page():
    website = request.args.get('website', '')
    
    escaped_website = escape_html(website)
    
    data = PROFILE_CONTENT.format(escaped_website, "", "")
    result = check_xss(data, flags[0], website, 'xss_hard')
    
    response = make_response(PROFILE_CONTENT.format(escaped_website, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/about')
def about_page():
    return ABOUT_CONTENT


@app.errorhandler(404)
def page_not_found(e):
    return ERROR_404_CONTENT, 404


@app.errorhandler(500)
def internal_error(e):
    return ERROR_500_CONTENT, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
