from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, make_response

from app import app
from app.models import UrlObj
from uuid import uuid4
import pickle
import base64
import json

# Session storage simulation (in-memory for simplicity)
# In production, this would be a database or distributed cache
session_store = {}

# Prefix that triggers deserialization (mimics jooby-pac4j "b64~" pattern)
BIN_PREFIX = "b64~"


def str_to_object(value):
    """
    Convert string value to object. If value starts with "b64~",
    decode base64 and deserialize the object.
    
    This mimics the vulnerable strToObject() method from jooby-pac4j
    SessionStoreImpl.java where values prefixed with "b64~" are
    base64 decoded and deserialized with ObjectInputStream.
    
    VULNERABILITY: Insecure deserialization - if an attacker can store
    a crafted value starting with "b64~", they can trigger arbitrary
    object deserialization leading to RCE.
    """
    if value is None:
        return None
    
    if isinstance(value, str) and value.startswith(BIN_PREFIX):
        # Extract the base64 encoded part after the prefix
        b64_data = value[len(BIN_PREFIX):]
        try:
            # Decode base64 and deserialize using pickle (Python equivalent of Java ObjectInputStream)
            decoded_bytes = base64.b64decode(b64_data)
            # VULNERABLE: Deserializing untrusted data
            return pickle.loads(decoded_bytes)
        except Exception as e:
            return f"Deserialization error: {str(e)}"
    
    # Return value as-is if no prefix
    return value


def object_to_str(obj):
    """
    Convert object to string for storage.
    Complex objects are serialized and prefixed with "b64~".
    """
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return str(obj)
    # Serialize complex objects
    serialized = base64.b64encode(pickle.dumps(obj)).decode('utf-8')
    return BIN_PREFIX + serialized


def get_session(session_id):
    """Get session data for a session ID"""
    return session_store.get(session_id, {})


def set_session_value(session_id, key, value):
    """Set a value in the session"""
    if session_id not in session_store:
        session_store[session_id] = {}
    session_store[session_id][key] = value


def get_session_value(session_id, key):
    """
    Get a value from the session.
    If the value starts with "b64~", deserialize it.
    """
    session_data = session_store.get(session_id, {})
    value = session_data.get(key)
    # Vulnerable deserialization happens here
    return str_to_object(value)


def name_in_list(urls, name):
    return any(u.name == name for u in urls)


def remove_url_with_name(urls, name):
    for i, u in enumerate(urls):
        if u.name == name:
            del urls[i]
            return True
    return False


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


@app.route('/')
def index():
    return redirect(url_for('bookmarks_list'))


@app.route('/list')
def bookmarks_list():
    session_id = request.cookies.get('session_id')
    
    if session_id:
        # Retrieve bookmarks from session - this triggers str_to_object if value has b64~ prefix
        bookmarks_data = get_session_value(session_id, 'bookmarks')
        user = get_session_value(session_id, 'user')
        
        if bookmarks_data is None:
            bookmarks_data = []
        
        # Convert to list if it's a string (from deserialized data)
        if isinstance(bookmarks_data, str):
            try:
                bookmarks_data = json.loads(bookmarks_data)
            except:
                bookmarks_data = []
        
        urls = []
        if isinstance(bookmarks_data, list):
            for item in bookmarks_data:
                if isinstance(item, dict):
                    urls.append(UrlObj(name=item.get('name', ''), url=item.get('url', '')))
                elif isinstance(item, UrlObj):
                    urls.append(item)
    else:
        urls = []
        session_id = uuid4().hex
        user = uuid4().hex
        
        # Initialize session
        set_session_value(session_id, 'bookmarks', json.dumps([]))
        set_session_value(session_id, 'user', user)
        
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('session_id', session_id)
        response.headers['Powered-By'] = 'Flask/Jooby-style-session'
        return response
    
    return render_template('list_urls.html', urls=urls, user=user if user else 'anonymous')


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')
    
    session_id = request.cookies.get('session_id')
    
    if session_id:
        name = request.form.get('name')
        url = request.form.get('url')
        
        # Get current bookmarks - triggers deserialization if prefixed
        bookmarks_data = get_session_value(session_id, 'bookmarks')
        user = get_session_value(session_id, 'user')
        
        if bookmarks_data is None:
            bookmarks_data = []
        
        if isinstance(bookmarks_data, str):
            try:
                bookmarks_data = json.loads(bookmarks_data)
            except:
                bookmarks_data = []
        
        # Check for duplicate names
        for item in bookmarks_data:
            item_name = item.get('name', '') if isinstance(item, dict) else getattr(item, 'name', '')
            if item_name == name:
                return render_template('add.html', error='Name already used')
        
        # Add new bookmark
        bookmarks_data.append({'name': name, 'url': url})
        set_session_value(session_id, 'bookmarks', json.dumps(bookmarks_data))
        
        urls = [UrlObj(name=item.get('name', ''), url=item.get('url', '')) for item in bookmarks_data]
        
        response = make_response(render_template('list_urls.html', urls=urls, user=user))
        response.set_cookie('session_id', session_id)
        return response
    else:
        return redirect(url_for('bookmarks_list'))


@app.route('/delete')
def delete():
    if not request.args.get('name'):
        return redirect(url_for('bookmarks_list'))
    
    session_id = request.cookies.get('session_id')
    
    if not session_id:
        return redirect(url_for('bookmarks_list'))
    
    url_name = request.args.get('name')
    
    # Get bookmarks - triggers deserialization if prefixed
    bookmarks_data = get_session_value(session_id, 'bookmarks')
    user = get_session_value(session_id, 'user')
    
    if bookmarks_data is None:
        return redirect(url_for('bookmarks_list'))
    
    if isinstance(bookmarks_data, str):
        try:
            bookmarks_data = json.loads(bookmarks_data)
        except:
            return redirect(url_for('bookmarks_list'))
    
    # Remove the bookmark
    bookmarks_data = [item for item in bookmarks_data if item.get('name') != url_name]
    set_session_value(session_id, 'bookmarks', json.dumps(bookmarks_data))
    
    urls = [UrlObj(name=item.get('name', ''), url=item.get('url', '')) for item in bookmarks_data]
    
    response = make_response(render_template('list_urls.html', urls=urls, user=user))
    response.set_cookie('session_id', session_id)
    return response


@app.route('/session/set', methods=['GET', 'POST'])
def session_set():
    """
    Endpoint to set session values. Accepts key-value pairs from query params or form data.
    This mimics an endpoint that saves user-provided data to session storage.
    
    Example usage:
    GET /session/set?token=some_value
    POST /session/set with form data key=token&value=some_value
    
    VULNERABILITY: User can store arbitrary values including "b64~" prefixed payloads
    that will be deserialized when retrieved via /session/get or when the session
    is accessed by other endpoints.
    """
    session_id = request.cookies.get('session_id')
    
    if not session_id:
        session_id = uuid4().hex
    
    # Accept key-value from query params (mimics the CVE example: /?token=b64~...)
    for key in request.args:
        value = request.args.get(key)
        set_session_value(session_id, key, value)
    
    # Also accept from form data
    for key in request.form:
        value = request.form.get(key)
        set_session_value(session_id, key, value)
    
    response = make_response(json.dumps({
        'status': 'ok',
        'message': 'Session values set successfully',
        'session_id': session_id
    }))
    response.headers['Content-Type'] = 'application/json'
    response.set_cookie('session_id', session_id)
    return response


@app.route('/session/get')
def session_get():
    """
    Endpoint to get session values. Returns the value for a given key.
    
    Example usage:
    GET /session/get?key=token
    
    VULNERABILITY: When retrieving a value that starts with "b64~",
    the str_to_object function deserializes it, triggering RCE if
    the payload contains a malicious pickled object.
    """
    session_id = request.cookies.get('session_id')
    
    if not session_id:
        return json.dumps({'error': 'No session found'}), 404
    
    key = request.args.get('key')
    if not key:
        # Return all session data (each value triggers str_to_object)
        session_data = get_session(session_id)
        result = {}
        for k, v in session_data.items():
            # Deserialization happens here for each value
            result[k] = str(str_to_object(v))
        response = make_response(json.dumps(result))
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Get specific key - triggers deserialization if prefixed with b64~
    value = get_session_value(session_id, key)
    
    response = make_response(json.dumps({
        'key': key,
        'value': str(value) if value else None
    }))
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/about')
def about():
    # Display an about us template
    if request.method == 'GET':
        return render_template('about.html')
