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

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

def is_clean_html(html_content):
    """
    Validate HTML content to prevent XSS attacks.
    Checks for dangerous event handlers and script elements.
    """
    if not html_content:
        return True
    
    content_lower = html_content.lower()
    
    if '<script' in content_lower or '</script' in content_lower:
        return False
    
    if '<svg' in content_lower or '</svg' in content_lower:
        return False
    
    if '<iframe' in content_lower or '</iframe' in content_lower:
        return False
    
    if 'javascript:' in content_lower:
        return False
    
    blocked_events = [
        'onabort', 'onblur', 'onchange', 'onclick', 'ondblclick',
        'onerror', 'onfocusout', 'onkeydown', 'onkeypress', 'onkeyup',
        'onload', 'onmousedown', 'onmousemove', 'onmouseout', 'onmouseover',
        'onmouseup', 'onreset', 'onresize', 'onscroll', 'onselect',
        'onsubmit', 'onunload', 'ondrag', 'ondragend', 'ondragenter',
        'ondragleave', 'ondragover', 'ondragstart', 'ondrop', 'onbegin'
    ]
    
    for event in blocked_events:
        pattern = re.compile(r'\b' + event + r'\s*=', re.IGNORECASE)
        if pattern.search(html_content):
            return False
    
    return True


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
        data = '<div class="notification"><p>Welcome! Please enter your feedback below.</p></div>'
    else:
        if result == 'XSS':
            data = '<div class="notification success"><p>Thank you for your feedback!</p><small>{0}</small></div>'.format(flag)
        elif result:
            data = '<div class="notification warning"><p>Your feedback has been recorded.</p></div>'
        else:
            data = '<div class="notification info"><p>Your feedback has been submitted.</p></div>'
    return data


@app.route('/contact', methods=['GET', 'POST'])
def contact_form():
    if request.method == 'POST':
        message = request.form.get('message', '')
    else:
        message = request.args.get('message', '')
    
    if message and not is_clean_html(message):
        response = make_response(CONTACT_PAGE.format(
            message_preview="",
            result_html='<div class="notification error"><p>Invalid input detected. Please remove any special characters.</p></div>'
        ))
        response.headers["X-XSS-Protection"] = "0"
        return response
    
    preview_html = ""
    if message:
        preview_html = '<div class="message-preview"><h4>Preview:</h4><div class="preview-content">{0}</div></div>'.format(message)
    
    page_with_preview = CONTACT_PAGE.format(
        message_preview=preview_html,
        result_html=""
    )
    
    result_html = check_xss(page_with_preview, flags[0], message, 'xss_medium')
    
    response = make_response(CONTACT_PAGE.format(
        message_preview=preview_html,
        result_html=result_html
    ))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/products')
def products():
    return PRODUCTS_PAGE


@app.route('/about')
def about():
    return ABOUT_PAGE


@app.errorhandler(404)
def not_found(e):
    return '<html><head><title>Page Not Found</title></head><body><h1>404 - Page Not Found</h1><p>The requested page could not be found.</p></body></html>', 404


@app.errorhandler(500)
def server_error(e):
    return '<html><head><title>Server Error</title></head><body><h1>500 - Internal Server Error</h1><p>An unexpected error occurred.</p></body></html>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
