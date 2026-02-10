from flask import Flask, render_template, redirect, url_for, request, make_response, abort

from app import app, APP_KEY
from app.models import UrlObj
from uuid import uuid4
import pickle
import base64
import hashlib
import json
import hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os as _os


def get_encryption_key():
    key_str = APP_KEY
    if key_str.startswith('base64:'):
        key_str = key_str[7:]
    raw_key = base64.b64decode(key_str)
    return hashlib.sha256(raw_key).digest()


def encrypt_cookie(data):
    key = get_encryption_key()
    iv = _os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    serialized = pickle.dumps(data)
    
    pad_len = 16 - (len(serialized) % 16)
    serialized += bytes([pad_len]) * pad_len
    
    encrypted = encryptor.update(serialized) + encryptor.finalize()
    
    payload = {
        'iv': base64.b64encode(iv).decode(),
        'value': base64.b64encode(encrypted).decode()
    }
    
    payload_json = json.dumps(payload)
    mac = hmac.new(key, payload_json.encode(), hashlib.sha256).hexdigest()
    payload['mac'] = mac
    
    return base64.b64encode(json.dumps(payload).encode()).decode()


def decrypt_cookie(cookie_value):
    key = get_encryption_key()
    
    payload = json.loads(base64.b64decode(cookie_value))
    
    iv = base64.b64decode(payload['iv'])
    encrypted = base64.b64decode(payload['value'])
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    decrypted = decryptor.update(encrypted) + decryptor.finalize()
    
    pad_len = decrypted[-1]
    decrypted = decrypted[:-pad_len]
    
    return pickle.loads(decrypted)


def name_in_list(urls, name):
    return any(u.name == name for u in urls)


def remove_url_with_name(urls, name):
    for i, u in enumerate(urls):
        if u.name == name:
            del urls[i]
            return True
    return False


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/')
def index():
    return redirect(url_for('bookmarks_list'))


@app.route('/list')
def bookmarks_list():
    if request.cookies.get('session_data') and request.cookies.get('user'):
        try:
            urls = decrypt_cookie(request.cookies.get('session_data'))
            user = request.cookies.get('user')
        except Exception:
            return redirect(url_for('bookmarks_list'))
    else:
        urls = []
        user = uuid4().hex
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('session_data', encrypt_cookie([]))
        response.set_cookie('user', user)
        return response

    return render_template('list_urls.html', urls=urls, user=user)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')

    if request.cookies.get('session_data') and request.cookies.get('user'):
        name = request.form.get('name')
        url = request.form.get('url')
        try:
            urls = decrypt_cookie(request.cookies.get('session_data'))
        except Exception:
            return redirect(url_for('bookmarks_list'))
        if name_in_list(urls, name):
            return render_template('add.html', error='Name already used')
        user = request.cookies.get('user')
        urls.append(UrlObj(name=name, url=url))
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('session_data', encrypt_cookie(urls))
        response.set_cookie('user', user)
        return response
    else:
        return redirect(url_for('bookmarks_list'))


@app.route('/delete')
def delete():
    if not request.args.get('name'):
        return redirect(url_for('bookmarks_list'))

    url_name = request.args.get('name')
    try:
        urls = decrypt_cookie(request.cookies.get('session_data'))
    except Exception:
        return redirect(url_for('bookmarks_list'))
    user = request.cookies.get('user')

    if remove_url_with_name(urls, url_name):
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('session_data', encrypt_cookie(urls))
        response.set_cookie('user', user)
        return response

    return redirect(url_for('bookmarks_list'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/.env')
def env_file():
    env_content = """# Application Environment Configuration
APP_NAME=BookmarkManager
APP_ENV=production
APP_DEBUG=false
APP_KEY=base64:kT9Xp2mNvHj3qL8wRzY5bC6dF4eG1aI0

DB_CONNECTION=sqlite
DB_DATABASE=/var/data/bookmarks.db

CACHE_DRIVER=file
SESSION_DRIVER=cookie
SESSION_LIFETIME=120
"""
    response = make_response(env_content)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/robots.txt')
def robots():
    content = """User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /.env
"""
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Internal server error'), 500
