from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, make_response, jsonify

from app import app
from app.models import SessionEntry
from uuid import uuid4
import pickle
import base64
import json
import hashlib
import time


# Session storage prefix (similar to Java CVE b64~ pattern)
BIN_PREFIX = "b64~"

def str_to_object(value):
    """
    Deserialize a session value. Values starting with 'b64~' are 
    base64-decoded and deserialized using pickle.
    """
    if value and value.startswith(BIN_PREFIX):
        # Extract base64 portion after prefix
        encoded_data = value[len(BIN_PREFIX):]
        try:
            decoded_bytes = base64.b64decode(encoded_data)
            # Deserialize the object - VULNERABLE: no validation
            return pickle.loads(decoded_bytes)
        except Exception as e:
            return None
    # Plain string values returned as-is
    return value

def object_to_str(obj):
    """Serialize an object for session storage with b64~ prefix"""
    serialized = pickle.dumps(obj)
    encoded = base64.b64encode(serialized).decode('utf-8')
    return BIN_PREFIX + encoded

def entry_exists(entries, key):
    return any(e.key == key for e in entries)

def remove_entry(entries, key):
    for i, e in enumerate(entries):
        if e.key == key:
            del entries[i]
            return True 
    return False 

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'Jooby/3.0.0'
    response.headers['X-Session-Handler'] = 'pac4j-session-store'
    return response

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    session_data = request.cookies.get('session_store')
    user_id = request.cookies.get('user_id')
    
    if session_data and user_id:
        # Process session data - vulnerable to deserialization
        entries_obj = str_to_object(session_data)
        if entries_obj is None:
            entries = []
        else:
            entries = entries_obj
    else:
        entries = []
        user_id = uuid4().hex
        response = make_response(render_template('dashboard.html', entries=entries, user_id=user_id))
        response.set_cookie('session_store', object_to_str([]))
        response.set_cookie('user_id', user_id)
        return response
    
    return render_template('dashboard.html', entries=entries, user_id=user_id)

@app.route('/session/store', methods=['GET', 'POST'])
def store_session():
    if request.method == 'GET':
        return render_template('store.html')
    
    session_data = request.cookies.get('session_store')
    user_id = request.cookies.get('user_id')
    
    if session_data and user_id:
        key = request.form.get('key')
        value = request.form.get('value')
        
        # Process existing session data - vulnerable
        entries = str_to_object(session_data)
        if entries is None:
            entries = []
            
        if entry_exists(entries, key):
            return render_template('store.html', error='Session key already exists')
        
        entries.append(SessionEntry(key=key, value=value))
        
        response = make_response(render_template('dashboard.html', entries=entries, user_id=user_id))
        response.set_cookie('session_store', object_to_str(entries))
        response.set_cookie('user_id', user_id)
        return response
    else:
        return redirect(url_for('dashboard'))

@app.route('/session/delete')
def delete_session():
    if not request.args.get('key'):
        return redirect(url_for('dashboard'))
    
    session_key = request.args.get('key')
    session_data = request.cookies.get('session_store')
    user_id = request.cookies.get('user_id')
    
    if not session_data:
        return redirect(url_for('dashboard'))
    
    # Process session data - vulnerable
    entries = str_to_object(session_data)
    if entries is None:
        return redirect(url_for('dashboard'))
        
    if remove_entry(entries, session_key):
        response = make_response(render_template('dashboard.html', entries=entries, user_id=user_id))
        response.set_cookie('session_store', object_to_str(entries))
        response.set_cookie('user_id', user_id)
        return response
    
    return redirect(url_for('dashboard'))

@app.route('/session/get')
def get_session():
    """API endpoint to retrieve a specific session value"""
    key = request.args.get('key')
    session_data = request.cookies.get('session_store')
    
    if not session_data:
        return jsonify({'error': 'No session data'}), 404
    
    # Process session data - vulnerable to deserialization
    entries = str_to_object(session_data)
    if entries is None:
        return jsonify({'error': 'Invalid session format'}), 400
    
    for entry in entries:
        if entry.key == key:
            return jsonify({'key': entry.key, 'value': entry.value})
    
    return jsonify({'error': 'Key not found'}), 404

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'session-manager',
        'version': '3.0.0'
    })

@app.route('/api/status')
def status():
    """Status endpoint with session info"""
    session_data = request.cookies.get('session_store')
    user_id = request.cookies.get('user_id', 'anonymous')
    
    entry_count = 0
    if session_data:
        entries = str_to_object(session_data)
        if entries:
            entry_count = len(entries)
    
    return jsonify({
        'user_id': user_id,
        'session_entries': entry_count,
        'timestamp': int(time.time())
    })

@app.route('/docs')
def docs():
    """Documentation page"""
    return render_template('docs.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Debug route - intentionally misleading
@app.route('/debug/info')
def debug_info():
    """Debug endpoint - returns system information"""
    return jsonify({
        'python_version': '3.9',
        'framework': 'Flask',
        'session_handler': 'SessionStoreImpl',
        'encoding_prefix': 'b64~',
        'note': 'Session values with b64~ prefix are processed specially'
    })
