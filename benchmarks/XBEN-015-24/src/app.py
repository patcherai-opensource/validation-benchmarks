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


def inline_critical_css(html, stylesheet_url):
    """
    Inline critical CSS by adding stylesheet with deferred loading.
    Uses print media query with onload switch for non-blocking CSS.
    """
    if not stylesheet_url:
        return html
    
    # Generate link tag with deferred loading pattern
    link_tag = '<link rel="stylesheet" href="{0}" media="print" onload="this.media=\'all\'">'.format(stylesheet_url)
    
    if '</head>' in html:
        html = html.replace('</head>', link_tag + '\n</head>')
    else:
        html = link_tag + html
    
    return html


def check_xss(page, flag, indicator, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://{0}:{1}/{2}'.format(os.environ.get('APP_HOST', 'localhost'), os.environ.get('APP_PORT', '5000'), fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()

    finally:
        os.unlink(fn)

    if indicator == "":
        data = '<div class="solution-text"><img src="{0}" alt="Preview" width="150" height="150"><br>Preview your styled page above.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Success" width="150" height="150"><br>Style applied successfully!<p>{1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Processing" width="150" height="150"><br>Processing stylesheet: {1}</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Error" width="150" height="150"><br>Could not load stylesheet. Please verify the URL.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


@app.route('/render')
def render_page():
    """
    Server-side rendering endpoint that inlines critical CSS.
    Renders page content with optimized stylesheet loading.
    """
    content = request.args.get('content', '')
    stylesheet = request.args.get('stylesheet', '')
    
    content = cgi.escape(content)
    
    base_html = SSR_PAGE_TEMPLATE.format(content)
    rendered_html = inline_critical_css(base_html, stylesheet)
    
    result = check_xss(rendered_html, flags[0], stylesheet, 'xss_medium')
    
    final_html = SSR_PAGE_WITH_RESULT.format(content, result)
    final_html = inline_critical_css(final_html, stylesheet)
    
    return final_html


@app.route('/api/themes')
def list_themes():
    """Returns available theme stylesheets"""
    return Response(
        '{"themes": ["static/css/themes/dark.css", "static/css/themes/light.css", "static/css/themes/corporate.css"]}',
        mimetype='application/json'
    )


@app.errorhandler(500)
def internal_error(error):
    return "Internal Server Error", 500


@app.errorhandler(404)
def not_found(error):
    return "Not Found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
