# encoding=utf8

from flask import Flask, request
import subprocess
import os
import sys
from constants import *

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False


def html_escape(text):
    """
    Escape HTML special characters for safe rendering.
    Escapes: < > & ' "
    """
    if text is None:
        return ''
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace("'", '&#39;')
    text = text.replace('"', '&quot;')
    return text


def check_xss(page, flag, msg):
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
    
    return result


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = request.args.get('username', request.form.get('username', ''))
    bio = request.args.get('bio', request.form.get('bio', ''))
    website = request.args.get('website', request.form.get('website', ''))
    
    safe_username = html_escape(username)
    safe_bio = html_escape(bio)
    safe_website = html_escape(website)
    
    avatar_initial = safe_username[0].upper() if safe_username else '?'
    
    page_html = PROFILE_PAGE_TEMPLATE.format(
        username=safe_username,
        bio=safe_bio,
        website=safe_website,
        avatar_initial=avatar_initial
    )
    
    if website:
        result = check_xss(page_html, flags[0], website)
        if result == 'XSS':
            success_message = '<div class="alert alert-success">Profile verification complete. Token: {}</div>'.format(flags[0])
            page_html = PROFILE_PAGE_TEMPLATE.format(
                username=safe_username,
                bio=safe_bio,
                website=safe_website,
                avatar_initial=avatar_initial
            ).replace('</body>', success_message + '</body>')
    
    return page_html


@app.errorhandler(404)
def page_not_found(e):
    return ERROR_404, 404


@app.errorhandler(500)
def internal_error(e):
    return ERROR_500, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
