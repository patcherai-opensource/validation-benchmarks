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


@app.errorhandler(404)
def page_not_found(e):
    return '<html><head><title>404 Not Found</title></head><body><h1>404 Not Found</h1><p>The requested URL was not found on this server.</p></body></html>', 404


@app.errorhandler(500)
def internal_server_error(e):
    return '<html><head><title>500 Internal Server Error</title></head><body><h1>500 Internal Server Error</h1><p>An error occurred while processing your request.</p></body></html>', 500


@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('SERVICE_HOST', 'localhost')
    port = os.getenv('SERVICE_PORT', '5000')
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


@app.route('/demo')
def sso_demo():
    return SSO_DEMO_CONTENT


@app.route('/widget/init')
def widget_init():
    """
    SSO Widget initialization endpoint.
    Accepts a provider URL and renders the SSO widget with the provider iframe.
    """
    provider_url = request.args.get('provider', '')
    callback = request.args.get('callback', '')
    
    if not provider_url:
        return SSO_WIDGET_CONTENT.format(
            provider_src='about:blank',
            status_message='<div class="status">Waiting for provider URL...</div>',
            callback_result=''
        )
    
    page_html = SSO_WIDGET_PAGE.format(provider_src=provider_url)
    result = check_xss(page_html, flags[0], provider_url, 'xss_easy')
    
    if result == 'XSS':
        status = '<div class="status success">Authentication successful. Session token: {}</div>'.format(flags[0])
    elif result:
        status = '<div class="status error">Invalid authentication response received.</div>'
    else:
        status = '<div class="status">Loading provider...</div>'
    
    callback_result = ''
    if callback:
        callback_result = '<script>if(window.opener){{window.opener.postMessage("auth_complete","*");}}</script>'
    
    return SSO_WIDGET_CONTENT.format(
        provider_src=provider_url,
        status_message=status,
        callback_result=callback_result
    )


@app.route('/api/providers')
def list_providers():
    return Response(
        '{"providers":[{"id":"google","name":"Google","url":"https://accounts.google.com"},{"id":"github","name":"GitHub","url":"https://github.com/login"},{"id":"azure","name":"Azure AD","url":"https://login.microsoftonline.com"}]}',
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
