# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, jsonify, redirect
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
        print "Page:"
        print page
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "Result:"
        print result

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<p style="color:#888;">Enter a media URL above to see the embed preview.</p>'
    else:
        if result == 'XSS':
            data = '<div style="color:#0f0;background:#030;padding:15px;border-radius:4px;"><strong>Security Test Passed!</strong><br>Verification Token: {0}</div>'.format(flag)
        elif result:
            data = '<div style="color:#fa0;background:#330;padding:15px;border-radius:4px;">Embed rendered with alert: {0}</div>'.format(cgi.escape(result))
        else:
            data = '<p style="color:#888;">Media loaded successfully.</p>'
    return data

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "plateembed", "version": "36.0.9"})

# API Status endpoint
@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "operational",
        "version": "36.0.9",
        "endpoints": ["/embed/youtube", "/embed/twitter", "/embed/vimeo", "/embed/media"],
        "uptime": "99.9%"
    })

# API Documentation
@app.route('/api/docs')
def api_docs():
    return API_DOCS_CONTENT

# YouTube Embed - SAFE (strict domain validation)
@app.route('/embed/youtube')
def embed_youtube():
    url = request.args.get('url', '')
    
    if url == '':
        return YOUTUBE_EMBED_CONTENT.format('<p style="color:#888;">No URL provided</p>')
    
    # Strict domain validation - only allow youtube.com and youtu.be
    youtube_pattern = re.compile(r'^https?://(www\.)?(youtube\.com|youtu\.be)/', re.IGNORECASE)
    
    if not youtube_pattern.match(url):
        return YOUTUBE_EMBED_CONTENT.format('<p class="error">Error: Invalid URL. Only youtube.com and youtu.be URLs are accepted.</p>')
    
    # Sanitize and embed
    url = re.sub(r'[<>"\']', '', url)
    iframe = '<iframe src="{0}" allowfullscreen></iframe>'.format(url)
    return YOUTUBE_EMBED_CONTENT.format(iframe)

# Twitter Embed - SAFE (strict domain validation)
@app.route('/embed/twitter')
def embed_twitter():
    url = request.args.get('url', '')
    
    if url == '':
        return TWITTER_EMBED_CONTENT.format('<p style="color:#888;">No URL provided</p>')
    
    # Strict domain validation - only allow twitter.com and x.com
    twitter_pattern = re.compile(r'^https?://(www\.)?(twitter\.com|x\.com)/', re.IGNORECASE)
    
    if not twitter_pattern.match(url):
        return TWITTER_EMBED_CONTENT.format('<p class="error">Error: Invalid URL. Only twitter.com and x.com URLs are accepted.</p>')
    
    # Sanitize and embed
    url = re.sub(r'[<>"\']', '', url)
    iframe = '<iframe src="{0}" allowfullscreen></iframe>'.format(url)
    return TWITTER_EMBED_CONTENT.format(iframe)

# Vimeo Embed - SAFE (strict domain validation)
@app.route('/embed/vimeo')
def embed_vimeo():
    url = request.args.get('url', '')
    
    if url == '':
        return VIMEO_EMBED_CONTENT.format('<p style="color:#888;">No URL provided</p>')
    
    # Strict domain validation - only allow vimeo.com
    vimeo_pattern = re.compile(r'^https?://(www\.)?vimeo\.com/', re.IGNORECASE)
    
    if not vimeo_pattern.match(url):
        return VIMEO_EMBED_CONTENT.format('<p class="error">Error: Invalid URL. Only vimeo.com URLs are accepted.</p>')
    
    # Sanitize and embed
    url = re.sub(r'[<>"\']', '', url)
    iframe = '<iframe src="{0}" allowfullscreen></iframe>'.format(url)
    return VIMEO_EMBED_CONTENT.format(iframe)

# Custom Media Embed - VULNERABLE (uses custom urlParsers pattern like CVE-2024-40631)
# This endpoint simulates the vulnerable useMediaState pattern where custom urlParsers
# allow dangerous protocols to be embedded in iframes
@app.route('/embed/media')
def embed_media():
    url = request.args.get('url', '')
    
    # Custom URL parser simulation - the vulnerability!
    # Like the CVE, this allows any URL including javascript: protocol
    # Only basic sanitization is applied (remove < > ") but javascript: URLs pass through
    
    # Remove angle brackets and quotes (basic XSS prevention that can be bypassed)
    url = re.sub(r'\"', "", url)  # Remove double quotes
    url = re.sub(r"[<>]", "", url)  # Remove < or >
    
    # Unlike the safe endpoints, no protocol/domain validation is performed
    # This mirrors the CVE where custom urlParsers don't validate the protocol
    
    if url == "":
        value = "class=\"media-placeholder\" src=\"about:blank\""
    else:
        value = 'src="{0}"'.format(url)
    
    data = XSS_CONTENT_IFRAME.format("2", "Custom Media", value, "", "")
    result = check_xss(data, flags[0], url, 'media_embed')
    return XSS_CONTENT_IFRAME.format("2", "Custom Media", value, result, "")

# Legacy endpoint (kept for backward compatibility, redirects to new structure)
@app.route('/page')
def legacy_page():
    url = request.args.get('url', '')
    if url:
        return redirect('/embed/media?url=' + urllib.quote(url))
    return redirect('/embed/media')

if __name__ == '__main__':
    app.run(debug=True)
