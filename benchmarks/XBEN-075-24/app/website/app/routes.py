from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, make_response

from app import app, APP_KEY
from app.models import UrlObj
from uuid import uuid4
import pickle
import base64
import hashlib
import hmac
import json


def name_in_list(urls, name):
    return any(u.name == name for u in urls)

def remove_url_with_name(urls, name):
    for i, u in enumerate(urls):
        if u.name == name:
            del urls[i]
            return True 
    return False


# Cookie encryption/decryption utilities (similar to Laravel's EncryptCookies middleware)
# Uses APP_KEY for HMAC signing and encryption
def encrypt_cookie(data):
    """
    Encrypt and sign cookie data using APP_KEY.
    Format: base64(json({payload: base64(pickled_data), mac: hmac}))
    Similar to Laravel's cookie encryption format.
    """
    # Serialize the data using pickle (like PHP's serialize)
    pickled = pickle.dumps(data)
    payload_b64 = base64.b64encode(pickled).decode('utf-8')
    
    # Create HMAC signature using APP_KEY
    mac = hmac.new(APP_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # Create the final encrypted cookie structure
    cookie_data = json.dumps({
        'payload': payload_b64,
        'mac': mac
    })
    
    return base64.b64encode(cookie_data.encode('utf-8')).decode('utf-8')


def decrypt_cookie(cookie_value):
    """
    Decrypt and verify cookie data using APP_KEY.
    VULNERABILITY: Decrypts and deserializes (pickles.loads) the payload if MAC is valid.
    Similar to Laravel's EncryptCookies middleware vulnerability (CVE-2018-15133).
    If attacker knows APP_KEY, they can forge valid MACs for malicious pickled payloads.
    """
    try:
        # Decode the cookie
        cookie_data = json.loads(base64.b64decode(cookie_value).decode('utf-8'))
        payload_b64 = cookie_data.get('payload', '')
        mac = cookie_data.get('mac', '')
        
        # Verify HMAC signature using APP_KEY
        expected_mac = hmac.new(APP_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(mac, expected_mac):
            return None
        
        # VULNERABLE: Deserialize the payload using pickle
        # This is analogous to Laravel's unserialize() call in EncryptCookies.php
        # If an attacker can forge a valid MAC (by knowing APP_KEY), they can
        # inject arbitrary pickled objects that execute code on deserialization
        pickled_data = base64.b64decode(payload_b64)
        return pickle.loads(pickled_data)  # INSECURE DESERIALIZATION
        
    except Exception as e:
        return None


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route('/')
def index():
    return redirect(url_for('bookmarks_list'))


@app.route('/list')
def bookmarks_list():
    """
    Display bookmarks list. The bookmarks cookie is decrypted and deserialized.
    This is similar to how Laravel processes encrypted session/CSRF cookies.
    """
    if request.cookies.get('bookmarks') and request.cookies.get('user'):
        # Decrypt and deserialize the bookmarks cookie
        # VULNERABILITY: pickle.loads is called on the decrypted payload
        urls = decrypt_cookie(request.cookies.get('bookmarks'))
        
        if urls is None:
            # Invalid or tampered cookie - reset session
            urls = []
            user = uuid4().hex
            response = make_response(render_template('list_urls.html', urls=urls, user=user))
            response.set_cookie('bookmarks', encrypt_cookie([]))
            response.set_cookie('user', user)
            return response
            
        user = request.cookies.get('user')
    else:
        urls = []
        user = uuid4().hex
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('bookmarks', encrypt_cookie([]))
        response.set_cookie('user', user)
        response.headers['Powered-By'] = 'Flask'
        return response
    
    return render_template('list_urls.html', urls=urls, user=user)


@app.route('/add', methods=['GET', 'POST'])
def add():
    """Add a bookmark URL. Also triggers cookie decryption/deserialization."""
    if request.method == 'GET':
        return render_template('add.html')
    
    if request.cookies.get('bookmarks') and request.cookies.get('user'):
        name = request.form.get('name')
        url = request.form.get('url')
        
        # Decrypt and deserialize bookmarks cookie
        urls = decrypt_cookie(request.cookies.get('bookmarks'))
        
        if urls is None:
            return redirect(url_for('bookmarks_list'))
            
        if name_in_list(urls, name):
            return render_template('add.html', error='Name already used')
            
        user = request.cookies.get('user')
        urls.append(UrlObj(name=name, url=url))
        
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('bookmarks', encrypt_cookie(urls))
        response.set_cookie('user', user)
        return response
    else:
        return redirect(url_for('bookmarks_list'))


@app.route('/delete')
def delete():
    """Delete a bookmark URL. Also triggers cookie decryption/deserialization."""
    if not request.args.get('name'):
        return redirect(url_for('bookmarks_list'))
    
    url_name = request.args.get('name')
    
    # Decrypt and deserialize bookmarks cookie
    urls = decrypt_cookie(request.cookies.get('bookmarks'))
    user = request.cookies.get('user')
    
    if urls is None:
        return redirect(url_for('bookmarks_list'))

    if remove_url_with_name(urls, url_name):
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('bookmarks', encrypt_cookie(urls))
        response.set_cookie('user', user)
        return response
    
    return redirect(url_for('bookmarks_list'))


@app.route('/about')
def about():
    """Display an about us template."""
    if request.method == 'GET':
        return render_template('about.html')


@app.route('/.env')
def env_file():
    """
    Accidentally exposed .env file (similar to Laravel's .env containing APP_KEY).
    In production, this should never be accessible, but misconfigured servers
    often expose this file.
    """
    env_content = f"""# Application Environment Configuration
# DO NOT COMMIT THIS FILE TO VERSION CONTROL

APP_NAME=BookmarksApp
APP_ENV=production
APP_DEBUG=false

# Application encryption key for cookie signing
# Similar to Laravel's APP_KEY
APP_KEY={APP_KEY}

# Database configuration (not used in this app)
DB_CONNECTION=sqlite
DB_DATABASE=/var/www/data/bookmarks.db

# Session configuration
SESSION_DRIVER=cookie
SESSION_LIFETIME=120
"""
    return Response(env_content, mimetype='text/plain')
