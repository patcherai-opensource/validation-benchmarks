# encoding=utf8

from flask import Flask, request, jsonify
import subprocess
import os
import cgi
import sys
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/health')
def health_check():
    return 'ok', 200


@app.route('/providers')
def providers():
    return PROVIDERS_CONTENT


def validate_widget_url(url):
    """Validate widget URL - blocks obviously dangerous patterns but allows configured protocols"""
    if not url or not isinstance(url, basestring):
        return False, "URL is required"

    url = url.strip()

    if len(url) > 2048:
        return False, "URL exceeds maximum length"

    # Block data: URIs to prevent base64 encoded payloads
    if url.lower().startswith('data:'):
        return False, "Data URIs are not permitted"

    return True, url


def render_widget(url_value, result_html=""):
    """Render the widget embedding page with the given URL"""
    sanitized_display = cgi.escape(url_value) if url_value else ""
    return WIDGET_EMBED_PAGE.format(url_value, result_html, sanitized_display)


def check_xss(page, flag, url_input):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    internal_url = 'http://{0}:{1}/{2}'.format(
        os.environ.get('APP_HOST', 'localhost'),
        os.environ.get('APP_PORT', '5000'),
        fn
    )
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(internal_url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        os.unlink(fn)

    if url_input == "":
        data = '<div class="result-panel"><p class="info-text">Enter a widget URL above to preview it.</p></div>'
    else:
        if result == 'XSS':
            data = '<div class="result-panel success"><p>Integration verified.</p><p class="token">{0}</p></div>'.format(flag)
        elif result:
            data = '<div class="result-panel error"><p>Widget loaded but returned unexpected response: {0}</p></div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-panel error"><p>Widget failed to load or did not respond. Check the URL and try again.</p></div>'
    return data


@app.route('/widget/preview')
def widget_preview():
    url_input = request.args.get('src', '')

    valid, validated = validate_widget_url(url_input)
    if not valid and url_input:
        error_html = '<div class="result-panel error"><p>{0}</p></div>'.format(cgi.escape(validated))
        return render_widget("", error_html)

    page = render_widget(url_input)
    result = check_xss(page, flags[0], url_input)
    return render_widget(url_input, result)


@app.route('/api/v1/providers', methods=['GET'])
def api_providers():
    providers = [
        {"id": "decentraland", "name": "Decentraland", "endpoint": "https://id.decentraland.org", "status": "active"},
        {"id": "metamask", "name": "MetaMask Connect", "endpoint": "https://connect.metamask.io", "status": "active"},
        {"id": "walletconnect", "name": "WalletConnect", "endpoint": "https://bridge.walletconnect.org", "status": "active"},
        {"id": "custom", "name": "Custom Provider", "endpoint": "", "status": "configurable"}
    ]
    return jsonify({"providers": providers, "version": "0.9.2"})


@app.route('/api/v1/validate', methods=['POST'])
def api_validate():
    """Endpoint to validate a provider URL format"""
    url = request.form.get('url', '')
    if not url:
        return jsonify({"valid": False, "error": "URL is required"}), 400
    valid, msg = validate_widget_url(url)
    if not valid:
        return jsonify({"valid": False, "error": msg}), 400
    return jsonify({"valid": True, "url": url})


if __name__ == '__main__':
    app.run(debug=False)
