from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, g

from app import app
from app.db import db
from app.models import User

import hashlib
import time
import random
import string


# Global variable to store pending authentication state (VULNERABLE - no locking!)
# This simulates the pgAdmin CVE-2023-1907 session crossover vulnerability
_pending_auth = {}


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


class SessionError(Exception):
    def __init__(self, message='Authentication failed.'):
        self.message = message
        super().__init__(self.message)


def get_session():
    return app.session_interface.open_session(app, request)


def verify_session():
    user = User.query.filter_by(username=session.get('username')).first()
    if user:
        user_password_hashed = hashlib.pbkdf2_hmac('sha256', user.password.encode(), app.secret_key.encode(), 100000).hex()
        if session.get('password_hash') == user_password_hashed:
            # Store user ID in session
            session['user_id'] = user.id
            session['session_id'] = session.sid
            return True
        else:
            raise SessionError(message='Invalid credentials.')
    else:
        raise SessionError(message='Invalid credentials.')


def authenticate_user(username, password):
    """
    Authenticate user credentials and return the user object.
    VULNERABLE: Uses global state without proper locking, causing session crossover
    when multiple users authenticate simultaneously.
    """
    global _pending_auth
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return None
    
    # Check password
    if user.password != password:
        return None
    
    # VULNERABLE: Store authenticated user in global state without locking
    # This creates a race condition window
    _pending_auth['current_user'] = user
    
    # Simulate authentication processing delay (e.g., LDAP lookup)
    # This widens the race window
    time.sleep(0.05)
    
    # VULNERABLE: Return the user from global state (may have been overwritten!)
    return _pending_auth.get('current_user')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login endpoint - VULNERABLE to session crossover race condition.
    Similar to CVE-2023-1907 in pgAdmin 4.
    
    When multiple users log in simultaneously, the session may be assigned
    to the wrong user due to race conditions in the authentication routine.
    """
    debug_session = None
    debug = request.args.get('debug')
    if debug == 'session':
        debug = True

    if request.method == 'GET':
        if debug:
            debug_session = str(dict(session.items()))
        return render_template('login.html', debug_session=debug_session)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # VULNERABLE: authenticate_user uses global state without locking
        authenticated_user = authenticate_user(username, password)
        
        if authenticated_user:
            # VULNERABLE: Session is assigned based on global state which may
            # have been modified by another concurrent request
            session['username'] = authenticated_user.username
            session['password_hash'] = hashlib.pbkdf2_hmac(
                'sha256', 
                authenticated_user.password.encode(), 
                app.secret_key.encode(), 
                100000
            ).hex()
            session['user_id'] = authenticated_user.id
            session['is_admin'] = authenticated_user.is_admin
            session['session_id'] = session.sid
            
            return redirect(url_for('dashboard'))
        else:
            if debug:
                debug_session = str(dict(session.items()))
            return render_template('login.html', error='Invalid credentials.', debug_session=debug_session)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin')
def admin_panel():
    debug_session = None
    debug = request.args.get('debug')
    if debug == 'session':
        debug = True

    try:
        verify_session()
    except SessionError as e:
        return render_template('login.html', error=e.message)

    # Check if user is admin using session data
    if session.get('is_admin'):
        with open('/flag') as flag_file:
            flag_content = flag_file.read()

        if debug:
            debug_session = str(dict(session.items()))
        return render_template('admin_panel.html', flag=flag_content, debug_session=debug_session)
    else:
        if debug:
            debug_session = str(dict(session.items()))
        return render_template('dashboard.html', error_message='Access denied. Administrator privileges required.', debug_session=debug_session)


@app.route('/dashboard')
def dashboard():
    debug_session = None
    debug = request.args.get('debug')
    if debug == 'session':
        debug = True

    try:
        verify_session()
    except SessionError as e:
        if debug:
            debug_session = str(dict(get_session().items()))
        return render_template('login.html', error=e.message, debug_session=debug_session)

    if debug:
        debug_session = str(dict(get_session().items()))
    return render_template('dashboard.html', debug_session=debug_session)


@app.route('/servers', methods=['GET', 'POST'])
def servers():
    try:
        verify_session()
    except SessionError as e:
        return render_template('login.html', error=e.message)

    if request.method == 'GET':
        return render_template('servers.html')
    elif request.method == 'POST':
        return render_template('servers.html', error_message='Unable to connect to database server. Connection refused.')


@app.route('/query')
def query_tool():
    try:
        verify_session()
    except SessionError as e:
        return render_template('login.html', error=e.message)
    return render_template('query_tool.html')
