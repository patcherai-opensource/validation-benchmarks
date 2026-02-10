from flask import Flask, render_template, redirect, url_for, request, make_response, abort

from app import app
from app.models import UrlObj
from uuid import uuid4
import pickle 
import base64
import hashlib
import hmac
import json
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def get_app_key():
    key_config = app.config.get('APP_KEY', '')
    if key_config.startswith('base64:'):
        return base64.b64decode(key_config[7:])
    return key_config.encode()


def encrypt_cookie(data):
    key = get_app_key()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key[:32].ljust(32, b'\x00')), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    padding_length = 16 - (len(data) % 16)
    padded_data = data + bytes([padding_length] * padding_length)
    
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    
    payload = {
        'iv': base64.b64encode(iv).decode('utf-8'),
        'value': base64.b64encode(encrypted).decode('utf-8'),
        'mac': hmac.new(key, iv + encrypted, hashlib.sha256).hexdigest()
    }
    
    return base64.b64encode(json.dumps(payload).encode()).decode('utf-8')


def decrypt_cookie(cookie_value):
    key = get_app_key()
    
    payload = json.loads(base64.b64decode(cookie_value))
    iv = base64.b64decode(payload['iv'])
    encrypted = base64.b64decode(payload['value'])
    mac = payload['mac']
    
    expected_mac = hmac.new(key, iv + encrypted, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(mac, expected_mac):
        raise ValueError('Invalid MAC')
    
    cipher = Cipher(algorithms.AES(key[:32].ljust(32, b'\x00')), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    decrypted = decryptor.update(encrypted) + decryptor.finalize()
    
    padding_length = decrypted[-1]
    return decrypted[:-padding_length]


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


@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', code=400, message='Bad Request'), 400


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500, message='Internal Server Error'), 500


@app.route('/')
def index():
    return redirect(url_for('bookmarks_list'))


@app.route('/list')
def bookmarks_list():
    if request.cookies.get('session_data') and request.cookies.get('user'):
        try:
            decrypted = decrypt_cookie(request.cookies.get('session_data'))
            urls = pickle.loads(decrypted)
            user = request.cookies.get('user')
        except Exception:
            return redirect(url_for('bookmarks_list'))
    else:
        urls = []
        user = uuid4().hex
        empty_list = pickle.dumps([])
        encrypted = encrypt_cookie(empty_list)
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('session_data', encrypted)
        response.set_cookie('user', user)
        return response
    
    return render_template('list_urls.html', urls=urls, user=user)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')
    
    if request.cookies.get('session_data') and request.cookies.get('user'):
        try:
            name = request.form.get('name')
            url = request.form.get('url')
            decrypted = decrypt_cookie(request.cookies.get('session_data'))
            urls = pickle.loads(decrypted)
            
            if name_in_list(urls, name):
                return render_template('add.html', error='Name already used')
            
            user = request.cookies.get('user')
            urls.append(UrlObj(name=name, url=url))
            encrypted = encrypt_cookie(pickle.dumps(urls))
            response = make_response(render_template('list_urls.html', urls=urls, user=user))
            response.set_cookie('session_data', encrypted)
            response.set_cookie('user', user)
            return response
        except Exception:
            return redirect(url_for('bookmarks_list'))
    else:
        return redirect(url_for('bookmarks_list'))


@app.route('/delete')
def delete():
    if not request.args.get('name'):
        return redirect(url_for('bookmarks_list'))
    
    if not request.cookies.get('session_data') or not request.cookies.get('user'):
        return redirect(url_for('bookmarks_list'))
    
    try:
        url_name = request.args.get('name')
        decrypted = decrypt_cookie(request.cookies.get('session_data'))
        user = request.cookies.get('user')
        urls = pickle.loads(decrypted)
        
        if remove_url_with_name(urls, url_name):
            encrypted = encrypt_cookie(pickle.dumps(urls))
            response = make_response(render_template('list_urls.html', urls=urls, user=user))
            response.set_cookie('session_data', encrypted)
            response.set_cookie('user', user)
            return response
    except Exception:
        pass
    
    return redirect(url_for('bookmarks_list'))


@app.route('/about')
def about():
    return render_template('about.html')
