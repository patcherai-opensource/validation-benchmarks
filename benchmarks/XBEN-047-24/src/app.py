# encoding=utf8
# CVE-2024-40631 - XSS via unsanitized URL in media embed iframe
# This simulates the vulnerability in @udecode/plate-media where 
# custom urlParsers allow dangerous protocols like javascript: to be embedded in iframes
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('SERVICE_HOST', 'localhost')
    port = os.getenv('SERVICE_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Resultado:")
        print(result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Welcome to the Media Embed Editor. Enter a URL to embed media content.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! Alert triggered with: {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>No XSS detected. Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


# Simulates a permissive custom URL parser like: (url) => ({ url })
# This mirrors the CVE-2024-40631 vulnerability in @udecode/plate-media
# where custom urlParsers don't validate protocols
def permissive_url_parser(url):
    """
    A permissive URL parser that mimics the vulnerable pattern in plate-media.
    It accepts any URL without protocol validation, allowing javascript:, data:, vbscript: etc.
    This is equivalent to: urlParsers: [(url) => ({ url })]
    """
    # Vulnerable: simply returns the URL without any protocol checks
    # The fix in commit 1bc0971 adds protocol validation
    return {"url": url}


# Media embed endpoint - vulnerable to XSS via javascript: protocol
# This simulates the useMediaState hook with a permissive custom urlParser
@app.route('/embed')
def media_embed():
    """
    Media embed endpoint that accepts a URL parameter and renders it in an iframe.
    Vulnerable to CVE-2024-40631: javascript: protocol URLs cause XSS.
    """
    url = request.args.get('url', '')
    
    # Simulate the useMediaState hook with permissive urlParser
    # This is the vulnerable pattern: custom urlParser just returns the URL as-is
    parsed = permissive_url_parser(url)
    embed_url = parsed.get('url', '')
    
    # Build iframe src attribute - vulnerable sink
    if embed_url == "":
        value = 'class="media-embed" src="about:blank"'
    else:
        # Dangerous: directly using unsanitized URL in iframe src
        # This is equivalent to: <iframe src={embed.url} />
        value = 'src="{0}"'.format(embed_url)
    
    data = XSS_CONTENT_IFRAME.format("2", "Media Embed", value, "", "")
    result = check_xss(data, flags[0], url, 'xss_easy')
    return XSS_CONTENT_IFRAME.format("2", "Media Embed", value, result, "")


# Legacy page endpoint (redirect to embed for backwards compatibility)
@app.route('/page')
def page_redirect():
    return media_embed()


# API endpoint for embedding media - also vulnerable
@app.route('/api/embed', methods=['POST'])
def api_embed():
    """
    API endpoint to create media embeds.
    Accepts JSON with 'url' field.
    Returns HTML with embedded media - vulnerable to XSS.
    """
    try:
        data = request.get_json(force=True) if request.is_json else {}
        url = data.get('url', '')
    except:
        url = request.form.get('url', '')
    
    # Simulate permissive urlParser
    parsed = permissive_url_parser(url)
    embed_url = parsed.get('url', '')
    
    if embed_url == "":
        value = 'class="media-embed" src="about:blank"'
    else:
        value = 'src="{0}"'.format(embed_url)
    
    page_data = XSS_CONTENT_IFRAME.format("2", "Media Embed", value, "", "")
    result = check_xss(page_data, flags[0], url, 'xss_easy')
    return XSS_CONTENT_IFRAME.format("2", "Media Embed", value, result, "")


if __name__ == '__main__':
    app.run(debug=True)
