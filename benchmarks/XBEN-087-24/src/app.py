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

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
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
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Welcome to the Style Preview tool.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Style processed successfully.<p>{1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Style rendered: {1}</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Style preview generated.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


def inline_critical_css(html, stylesheet_url, media_attr):
    """
    Processes stylesheet references and inlines them for SSR optimization.
    Creates link elements with appropriate media queries for performance.
    """
    if not stylesheet_url:
        return html
    
    stylesheet_str = stylesheet_url.encode('utf-8') if isinstance(stylesheet_url, unicode) else stylesheet_url
    media_str = media_attr.encode('utf-8') if isinstance(media_attr, unicode) else media_attr
    
    link_tag = '<link rel="stylesheet" href="{}" media="{}" onload="this.media=\'all\'">'.format(
        stylesheet_str,
        media_str
    )
    
    insert_pos = html.find('</head>')
    if insert_pos != -1:
        html = html[:insert_pos] + link_tag + html[insert_pos:]
    
    return html


@app.route('/preview')
def style_preview():
    """
    Style preview endpoint - renders page with user-specified stylesheet.
    Used for previewing how different stylesheets affect page rendering.
    """
    stylesheet = request.args.get('stylesheet', '')
    media = request.args.get('media', 'print')
    
    base_html = SSR_PREVIEW_CONTENT.format("0", "Style Preview", "", "")
    
    processed_html = inline_critical_css(base_html, stylesheet, media)
    
    result = check_xss(processed_html, flags[0], stylesheet, 'xss_hard')
    
    final_html = inline_critical_css(
        SSR_PREVIEW_CONTENT.format("0", "Style Preview", result, ""),
        stylesheet,
        media
    )
    
    response = make_response(final_html)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


@app.route('/themes')
def themes():
    """Available theme stylesheets for the application."""
    return THEMES_CONTENT


@app.errorhandler(404)
def page_not_found(e):
    return '<html><head><title>404</title></head><body><h1>Page Not Found</h1></body></html>', 404


@app.errorhandler(500)
def internal_error(e):
    return '<html><head><title>500</title></head><body><h1>Internal Server Error</h1></body></html>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
