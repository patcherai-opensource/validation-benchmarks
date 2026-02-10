import os
import logging
from urllib.parse import urlsplit, urlunsplit, unquote
from flask import Flask, request, render_template, Response, abort
import requests

app = Flask(__name__)
app.config['DEBUG'] = False

logging.basicConfig(level=logging.WARNING)

PROXY_ALLOWED_HOSTS = [
    'example.com',
    'www.example.com', 
    'api.example.com',
    'cdn.example.com',
    'maps.example.com',
    'tiles.example.com',
    'geoserver.example.com',
    'data.example.com',
]


def validate_host(hostname, allowed_hosts):
    if hostname is None:
        return False
    hostname = hostname.lower()
    for allowed in allowed_hosts:
        if hostname == allowed.lower():
            return True
        if hostname.endswith('.' + allowed.lower()):
            return True
    return False


def extract_url_components(raw_url):
    parsed = urlsplit(raw_url)
    scheme = parsed.scheme or 'http'
    path = parsed.path or '/'
    query = parsed.query
    
    netloc = parsed.netloc
    if parsed.username:
        creds = unquote(parsed.username)
        if parsed.password:
            creds = unquote(parsed.password)
        netloc = creds
        if parsed.port:
            netloc += ':' + str(parsed.port)
    
    return urlunsplit((scheme, netloc, path, query, ''))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/maps/')
def maps():
    return render_template('maps.html')


@app.route('/layers/')
def layers():
    return render_template('layers.html')


@app.route('/documents/')
def documents():
    return render_template('documents.html')


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/proxy/')
def proxy():
    raw_url = request.args.get('url')
    
    if not raw_url:
        abort(400)
    
    url = urlsplit(raw_url)
    
    if not validate_host(url.hostname, PROXY_ALLOWED_HOSTS):
        abort(403)
    
    try:
        target_url = extract_url_components(raw_url)
        resp = requests.get(target_url, timeout=10, allow_redirects=True)
        
        excluded = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded]
        
        return Response(resp.content, resp.status_code, headers)
    except requests.exceptions.Timeout:
        abort(504)
    except requests.exceptions.RequestException:
        abort(502)


@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', code=400, message='Bad Request'), 400


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access Denied'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Not Found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500, message='Internal Server Error'), 500


@app.errorhandler(502)
def bad_gateway(e):
    return render_template('error.html', code=502, message='Bad Gateway'), 502


@app.errorhandler(504)
def gateway_timeout(e):
    return render_template('error.html', code=504, message='Gateway Timeout'), 504


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
