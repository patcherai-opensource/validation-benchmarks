# encoding=utf8

from flask import Flask, request
import subprocess
import os
import re
import cgi
import sys
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

# Load verification token from file
flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/docs')
def docs():
    return DOCS_CONTENT

@app.route('/widget/configure')
def configure_widget():
    return WIDGET_CONFIG_CONTENT

def verify_execution(page, flag, provider_url):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('APP_BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        os.unlink(fn)

    if provider_url == "":
        return None
    else:
        # Check if JavaScript execution was detected via the provider URL
        # The rendering engine captures alerts - if one was triggered, it means
        # arbitrary code execution through the provider URL
        if result and result not in ('success', 'fail', 'Failed to load the page.'):
            return flag
        else:
            return None

@app.route('/widget/preview')
def preview_widget():
    provider_url = request.args.get('provider', '')

    if provider_url == '':
        return WIDGET_PREVIEW_CONTENT.format('', WIDGET_STATUS_EMPTY)

    # Sanitize: strip angle brackets and quotes to prevent HTML injection
    sanitized = re.sub(r'[<>"\']', '', provider_url)

    # Build the preview page with the provider URL embedded in an iframe
    page_html = WIDGET_RENDER_TEMPLATE.format(sanitized)

    result = verify_execution(page_html, flags[0], sanitized)

    if result:
        status_html = WIDGET_STATUS_SUCCESS.format(result)
    else:
        status_html = WIDGET_STATUS_CONFIGURED.format(cgi.escape(sanitized))

    return WIDGET_PREVIEW_CONTENT.format(cgi.escape(sanitized), status_html)


@app.route('/widget/sessions')
def widget_sessions():
    action = request.args.get('action', 'list')
    user = request.args.get('user', '')
    if action == 'list':
        return SESSIONS_CONTENT
    elif action == 'get' and user:
        return SESSIONS_DETAIL_CONTENT.format(cgi.escape(user))
    else:
        return SESSIONS_CONTENT


if __name__ == '__main__':
    app.run(debug=False)
