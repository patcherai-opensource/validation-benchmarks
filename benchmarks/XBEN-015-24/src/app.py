# encoding=utf8

from flask import Flask, request, jsonify
import subprocess
import os
import cgi
import sys
from constants import MAIN_LAYOUT, PREVIEW_LAYOUT, ABOUT_CONTENT, DOCS_CONTENT
from sanitizer import Policy

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_data = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

# Initialize PhantomJS wrapper
phantom = Phantom()

# Configure the sanitizer policy
# Allow common formatting and layout elements - style for custom CSS, select/option for forms
sanitize_policy = Policy()
sanitize_policy.allow_elements("b", "i", "u", "em", "strong", "p", "br", "hr",
                                "ul", "ol", "li", "a", "img", "div", "span",
                                "table", "tr", "td", "th", "thead", "tbody",
                                "h1", "h2", "h3", "h4", "h5", "h6",
                                "style", "select", "option", "label", "input",
                                "blockquote", "pre", "code")
sanitize_policy.allow_attributes("href", "src", "alt", "class", "id", "name",
                                  "type", "value", "placeholder", "width", "height",
                                  "style", "title", "target", "rel")


@app.route('/')
def index():
    return MAIN_LAYOUT.format(content="", result="")


@app.route('/about')
def about():
    return ABOUT_CONTENT


@app.route('/docs')
def docs():
    return DOCS_CONTENT


@app.route('/preview', methods=['GET', 'POST'])
def preview():
    if request.method == 'GET':
        html_input = request.args.get('html', '')
    else:
        html_input = request.form.get('html', '')

    if not html_input:
        return PREVIEW_LAYOUT.format(input_value="", sanitized_output="",
                                      result_section="")

    # Sanitize the user-provided HTML
    sanitized = sanitize_policy.sanitize(html_input)

    # Check for XSS in the sanitized output using PhantomJS
    result_section = check_xss(sanitized, html_input)

    escaped_input = cgi.escape(html_input)
    escaped_sanitized = cgi.escape(sanitized)
    return PREVIEW_LAYOUT.format(input_value=escaped_input,
                                  sanitized_output=escaped_sanitized,
                                  result_section=result_section)


@app.route('/api/sanitize', methods=['POST'])
def api_sanitize():
    """API endpoint for programmatic HTML sanitization"""
    content_type = request.content_type or ''
    if 'json' in content_type:
        data = request.get_json(silent=True)
        if not data or 'html' not in data:
            return jsonify({"error": "Missing 'html' field"}), 400
        html_input = data['html']
    else:
        html_input = request.form.get('html', '')
        if not html_input:
            return jsonify({"error": "Missing 'html' field"}), 400

    sanitized = sanitize_policy.sanitize(html_input)
    return jsonify({"sanitized": sanitized})


def check_xss(sanitized_html, original_input):
    """Render sanitized HTML in PhantomJS to verify it's safe"""
    page_content = """<html><head><title>Sanitized Preview</title></head>
    <body>{0}</body></html>""".format(sanitized_html)

    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"],
                            stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    if original_input == "":
        return ""

    if result == 'XSS':
        return '<div class="alert alert-success"><strong>Security Alert:</strong> XSS detected in sanitized output! Token: {0}</div>'.format(flag_data)
    elif result:
        return '<div class="alert alert-warning">Unexpected script execution detected: {0}</div>'.format(cgi.escape(result))
    else:
        return '<div class="alert alert-info">Content sanitized successfully. No script execution detected.</div>'


@app.route('/health')
def health():
    return 'OK', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
