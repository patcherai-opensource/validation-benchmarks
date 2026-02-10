# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, jsonify
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

flag_content = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

@app.errorhandler(404)
def not_found(e):
    return '<html><body><h1>404 Not Found</h1></body></html>', 404

@app.errorhandler(500)
def server_error(e):
    return '<html><body><h1>500 Internal Server Error</h1></body></html>', 500

@app.route('/')
def index():
    return INDEX_CONTENT

def parse_media_url(url):
    """
    Custom URL parser for media embeds.
    Similar to urlParsers in @udecode/plate-media.
    Returns the URL for embedding if valid format.
    """
    if not url or url.strip() == '':
        return None
    
    url = url.strip()
    url = re.sub(r'[<>]', '', url)
    
    return url

def render_embed_preview(embed_url, result_msg=''):
    """Render the media embed preview component"""
    if not embed_url:
        iframe_attrs = 'class="embed-placeholder" src="about:blank"'
    else:
        iframe_attrs = 'src="{}"'.format(embed_url)
    
    return MEDIA_EMBED_CONTENT.format(iframe_attrs, result_msg)

def verify_embed_execution(page_content, embed_url):
    """
    Server-side verification of embed rendering.
    Checks if JavaScript executes properly in the embedded content.
    """
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], 
                          stdout=subprocess.PIPE, 
                          stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('SERVICE_HOST', 'localhost')
    port = os.getenv('SERVICE_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    
    result = ''
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
    
    return result

@app.route('/embed')
def media_embed():
    """
    Media embed preview endpoint.
    Accepts a URL parameter and renders an iframe preview.
    Used by the document editor for embedding external media.
    """
    url = request.args.get('url', '')
    
    embed_url = parse_media_url(url)
    
    page_content = render_embed_preview(embed_url)
    
    result_msg = ''
    if embed_url:
        exec_result = verify_embed_execution(page_content, embed_url)
        if exec_result == 'XSS':
            result_msg = '<div class="embed-status success">Content verified. Reference: {}</div>'.format(flag_content)
        elif exec_result:
            result_msg = '<div class="embed-status warning">Embed loaded with message: {}</div>'.format(cgi.escape(exec_result))
    
    return render_embed_preview(embed_url, result_msg)

@app.route('/api/media/parse', methods=['POST'])
def api_parse_media():
    """
    API endpoint for parsing media URLs.
    Returns parsed embed configuration.
    """
    data = request.get_json(silent=True) or {}
    url = data.get('url', '')
    
    parsed = parse_media_url(url)
    
    if parsed:
        return jsonify({
            'success': True,
            'embed': {
                'url': parsed,
                'type': 'iframe'
            }
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Invalid URL format'
        }), 400

@app.route('/docs')
def documentation():
    """Documentation page for the media embed API"""
    return DOCS_CONTENT

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
