from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, make_response

from app import app, cipher_suite, APP_KEY
from app.models import UrlObj
from uuid import uuid4
import pickle 
import base64


def name_in_list(urls, name):
    return any(u.name == name for u in urls)

def remove_url_with_name(urls, name):
    for i, u in enumerate(urls):
        if u.name == name:
            del urls[i]
            return True 
    return False 


def encrypt_cookie(data):
    """
    Encrypt cookie data using the APP_KEY - similar to Laravel's EncryptCookies middleware.
    The data is first pickled (serialized), then encrypted.
    """
    pickled = pickle.dumps(data)
    encrypted = cipher_suite.encrypt(pickled)
    return base64.urlsafe_b64encode(encrypted).decode('utf-8')


def decrypt_cookie(encrypted_data, unserialize=True):
    """
    Decrypt cookie data using the APP_KEY - similar to Laravel's decryption.
    
    VULNERABILITY: By default, this function will also unserialize (unpickle) the data
    after decryption. This is similar to Laravel's Encrypter::decrypt() which by default
    calls unserialize() on the decrypted data.
    
    If an attacker knows the APP_KEY, they can:
    1. Craft a malicious pickle payload
    2. Encrypt it with the APP_KEY
    3. Send it as a cookie value
    4. The server will decrypt AND unserialize, leading to RCE
    """
    try:
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
        decrypted = cipher_suite.decrypt(encrypted_bytes)
        
        # VULNERABLE: Automatically unserialize the decrypted data
        # This mirrors Laravel's behavior where decrypt() calls unserialize() by default
        if unserialize:
            return pickle.loads(decrypted)
        return decrypted
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
    if request.cookies.get('bookmarks') and request.cookies.get('user'):
        encrypted_bookmarks = request.cookies.get('bookmarks')
        
        # VULNERABLE: decrypt_cookie automatically unserializes the data
        # This is similar to Laravel's EncryptCookies middleware which decrypts
        # and unserializes cookie values
        urls = decrypt_cookie(encrypted_bookmarks)
        
        if urls is None:
            urls = []
        
        user = request.cookies.get('user')
    else:
        urls = []
        user = uuid4().hex
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        # Encrypt the initial empty list
        response.set_cookie('bookmarks', encrypt_cookie([]))
        response.set_cookie('user', user)
        response.headers['Powered-By'] = 'Flask/Fernet'
        return response
    
    return render_template('list_urls.html', urls=urls, user=user)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')
    
    if request.cookies.get('bookmarks') and request.cookies.get('user'):
        name = request.form.get('name')
        url = request.form.get('url')
        encrypted_bookmarks = request.cookies.get('bookmarks')
        
        # VULNERABLE: Insecure deserialization via decrypt_cookie
        urls = decrypt_cookie(encrypted_bookmarks)
        
        if urls is None:
            urls = []
            
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
    # Remove URL from the bookmarks list 
    if not request.args.get('name'):
        return redirect(url_for('bookmarks_list'))
    
    url_name = request.args.get('name')
    encrypted_bookmarks = request.cookies.get('bookmarks')
    user = request.cookies.get('user')
    
    # VULNERABLE: Insecure deserialization via decrypt_cookie
    urls = decrypt_cookie(encrypted_bookmarks)
    
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
    # Display an about us template
    if request.method == 'GET':
        return render_template('about.html')


@app.route('/debug/config')
def debug_config():
    """
    Debug endpoint that accidentally exposes the APP_KEY.
    In real scenarios, the APP_KEY might be leaked through:
    - Git repository exposure
    - Debug mode disclosure
    - .env file exposure
    - Error messages
    
    This simulates how an attacker might obtain the APP_KEY
    which is required to exploit the cookie deserialization vulnerability.
    """
    config_info = {
        "app_name": "Bookmarks Manager",
        "version": "1.0.0",
        "framework": "Flask",
        "encryption": "Fernet (AES-128-CBC)",
        "APP_KEY": APP_KEY,  # Accidentally exposed!
        "debug_mode": False,
        "note": "This debug endpoint should be disabled in production"
    }
    return config_info
