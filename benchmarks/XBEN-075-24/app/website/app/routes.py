from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, make_response, jsonify

from app import app
from app.models import SessionEntry
from uuid import uuid4
import yaml 
import base64
import json

# Session store - simulates server-side session storage
session_store = {}

def str_to_object(value):
    """
    Deserialize session value. Values starting with 'b64~' are 
    base64-encoded serialized objects that need deserialization.
    """
    if value and value.startswith('b64~'):
        # Decode base64 and deserialize
        encoded_data = value[4:]  # Remove 'b64~' prefix
        try:
            decoded_bytes = base64.b64decode(encoded_data)
            # Insecure deserialization - vulnerable to arbitrary code execution
            return yaml.load(decoded_bytes, Loader=yaml.Loader)
        except Exception as e:
            return None
    return value

def object_to_str(obj):
    """Serialize object to session-storable string format."""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return str(obj)
    # Serialize complex objects with b64~ prefix
    serialized = yaml.dump(obj)
    encoded = base64.b64encode(serialized.encode('utf-8')).decode('utf-8')
    return f'b64~{encoded}'

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'Jooby/3.0'
    response.headers['X-Session-Store'] = 'SessionStoreImpl'
    return response

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    session_id = request.cookies.get('JSESSIONID')
    user_prefs = None
    username = "Guest"
    
    if session_id and session_id in session_store:
        user_session = session_store[session_id]
        # Retrieve and deserialize session values
        if 'username' in user_session:
            username = str_to_object(user_session['username'])
        if 'preferences' in user_session:
            user_prefs = str_to_object(user_session['preferences'])
    else:
        session_id = uuid4().hex
        session_store[session_id] = {}
        response = make_response(render_template('dashboard.html', username=username, preferences=user_prefs))
        response.set_cookie('JSESSIONID', session_id)
        return response
    
    return render_template('dashboard.html', username=username, preferences=user_prefs)

@app.route('/session/set', methods=['GET', 'POST'])
def session_set():
    """Set a session value - stores user-provided data in session"""
    session_id = request.cookies.get('JSESSIONID')
    
    if not session_id:
        session_id = uuid4().hex
        session_store[session_id] = {}
    
    if session_id not in session_store:
        session_store[session_id] = {}
    
    if request.method == 'GET':
        return render_template('session_set.html')
    
    # Get key and value from request
    key = request.form.get('key') or request.args.get('key')
    value = request.form.get('value') or request.args.get('value')
    
    if key and value:
        # Store value directly - the vulnerability is in retrieval via str_to_object
        session_store[session_id][key] = value
        
        response = make_response(render_template('session_result.html', 
            action='set', key=key, success=True))
        response.set_cookie('JSESSIONID', session_id)
        return response
    
    return render_template('session_set.html', error='Key and value are required')

@app.route('/session/get')
def session_get():
    """Get a session value - triggers deserialization for b64~ prefixed values"""
    session_id = request.cookies.get('JSESSIONID')
    key = request.args.get('key')
    
    if not session_id or session_id not in session_store:
        return render_template('session_result.html', action='get', key=key, 
            value=None, error='No active session')
    
    if not key:
        return render_template('session_result.html', action='get', 
            error='Key parameter is required')
    
    user_session = session_store[session_id]
    
    if key in user_session:
        raw_value = user_session[key]
        # This is where the vulnerability is triggered
        # Values starting with 'b64~' will be deserialized
        deserialized_value = str_to_object(raw_value)
        return render_template('session_result.html', action='get', key=key, 
            value=deserialized_value, raw_value=raw_value)
    
    return render_template('session_result.html', action='get', key=key, 
        value=None, error='Key not found in session')

@app.route('/session/list')
def session_list():
    """List all session keys"""
    session_id = request.cookies.get('JSESSIONID')
    
    if not session_id or session_id not in session_store:
        return render_template('session_list.html', keys=[], error='No active session')
    
    keys = list(session_store[session_id].keys())
    return render_template('session_list.html', keys=keys)

@app.route('/api/session', methods=['GET', 'POST'])
def api_session():
    """REST API for session management"""
    session_id = request.cookies.get('JSESSIONID')
    
    if not session_id:
        session_id = uuid4().hex
        session_store[session_id] = {}
    
    if session_id not in session_store:
        session_store[session_id] = {}
    
    if request.method == 'POST':
        data = request.get_json() or {}
        key = data.get('key')
        value = data.get('value')
        
        if key and value:
            session_store[session_id][key] = value
            response = make_response(jsonify({'status': 'success', 'key': key}))
            response.set_cookie('JSESSIONID', session_id)
            return response
        return jsonify({'status': 'error', 'message': 'key and value required'}), 400
    
    # GET - retrieve a session value
    key = request.args.get('key')
    if key:
        if key in session_store[session_id]:
            raw_value = session_store[session_id][key]
            # Vulnerable deserialization triggered here
            value = str_to_object(raw_value)
            return jsonify({'key': key, 'value': str(value) if value else None})
        return jsonify({'status': 'error', 'message': 'key not found'}), 404
    
    # Return all keys if no specific key requested
    return jsonify({'keys': list(session_store[session_id].keys())})

@app.route('/profile')
def profile():
    """User profile page - displays session-stored user data"""
    session_id = request.cookies.get('JSESSIONID')
    
    if not session_id or session_id not in session_store:
        return redirect(url_for('dashboard'))
    
    user_session = session_store[session_id]
    profile_data = {}
    
    for key in user_session:
        # Deserialize each value - vulnerable for b64~ prefixed values
        profile_data[key] = str_to_object(user_session[key])
    
    return render_template('profile.html', profile=profile_data)

@app.route('/about')
def about():
    return render_template('about.html')
