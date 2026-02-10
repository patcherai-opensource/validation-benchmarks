from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, g

from app import app
from app.db import db
from app.models import User, AuthState

import hashlib
import time
import random
import string


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


class SessionError(Exception):
    def __init__(self, message='Session verifcation failed.'):
        self.message = message
        super().__init__(self.message)


@app.route('/')
def index():
    return redirect(url_for('login'))


def authenticate_user(username, password):
    """
    Vulnerable authentication function - mimics CVE-2023-1907
    
    The vulnerability: Authentication state is stored in a shared database table
    without proper synchronization. When multiple users authenticate simultaneously,
    the auth state can be overwritten between the time it's written and read,
    causing session crossover.
    
    This is exactly what happened in pgAdmin 4 CVE-2023-1907 where session
    assignments in the login handler were not protected by a lock.
    """
    # Phase 1: Validate credentials
    user = User.query.filter_by(username=username).first()
    if not user:
        return None, 'Invalid username.'
    
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), app.secret_key.encode(), 100000).hex()
    expected_hash = hashlib.pbkdf2_hmac('sha256', user.password.encode(), app.secret_key.encode(), 100000).hex()
    
    if password_hash != expected_hash:
        return None, 'Wrong password.'
    
    # Phase 2: Store auth data in shared database state (VULNERABLE - no lock)
    # This creates a race window where another process/thread can overwrite this data
    # Uses READ UNCOMMITTED isolation level for dirty reads
    auth_record = AuthState.query.first()
    if not auth_record:
        auth_record = AuthState(
            pending_username=username,
            pending_user_id=user.id,
            pending_is_admin=user.is_admin,
            pending_password_hash=password_hash
        )
        db.session.add(auth_record)
    else:
        auth_record.pending_username = username
        auth_record.pending_user_id = user.id
        auth_record.pending_is_admin = user.is_admin
        auth_record.pending_password_hash = password_hash
    
    db.session.commit()
    
    # Simulate processing delay - increases race window
    # In real pgAdmin, this was LDAP auth latency
    time.sleep(0.05)
    
    # Phase 3: Read back from shared state to get session data (VULNERABLE)
    # If another auth happened during the sleep, we read the wrong user's data!
    # The READ UNCOMMITTED isolation allows us to see uncommitted changes
    db.session.expire_all()  # Force fresh read
    auth_record = AuthState.query.first()
    
    if auth_record:
        auth_data = {
            'username': auth_record.pending_username,
            'password_hash': auth_record.pending_password_hash,
            'user_id': auth_record.pending_user_id,
            'is_admin': auth_record.pending_is_admin
        }
        return auth_data, None
    
    return None, 'Authentication state error.'


@app.route('/login', methods=['GET', 'POST'])
def login():
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
        
        # Authenticate using vulnerable function
        auth_data, error = authenticate_user(username, password)
        
        if error:
            if debug:
                debug_session = str(dict(session.items()))
            return render_template('login.html', error=error, debug_session=debug_session)
        
        # Assign session data from potentially race-corrupted auth_data
        # This is where session crossover occurs (like CVE-2023-1907)
        session['username'] = auth_data['username']
        session['password_hash'] = auth_data['password_hash']
        session['user_id'] = auth_data['user_id']
        session['is_admin'] = auth_data['is_admin']
        
        if debug:
            debug_session = str(dict(session.items()))
        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    # Clear session data
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('password_hash', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))


@app.route('/admin_panel')
def admin_panel():
    debug_session = None
    debug = request.args.get('debug')
    if debug == 'session':
        debug = True

    # Check if user is logged in
    if not session.get('user_id'):
        return render_template('login.html', error='Please login first.')
    
    # Check admin status from session (which could be from race condition crossover)
    if session.get('is_admin'):
        with open('/flag') as flag_file:
            flag_content = flag_file.read()

        if debug:
            debug_session = str(dict(session.items()))
        return render_template('admin_panel.html', flag=flag_content, debug_session=debug_session)
    else:
        if debug:
            debug_session = str(dict(session.items()))
        return render_template('dashboard.html', error_message='Only administrator users can open this section.', debug_session=debug_session)


@app.route('/dashboard')
def dashboard():
    debug_session = None
    debug = request.args.get('debug')
    if debug == 'session':
        debug = True

    if not session.get('user_id'):
        if debug:
            debug_session = str(dict(session.items()))
        return render_template('login.html', error='Please login first.', debug_session=debug_session)

    if debug:
        debug_session = str(dict(session.items()))
    return render_template('dashboard.html', debug_session=debug_session)


@app.route('/wifi_settings', methods=['GET', 'POST'])
def wifi_settings():
    if not session.get('user_id'):
        return render_template('login.html', error='Please login first.')

    if request.method == 'GET':
        return render_template('wifi_settings.html')
    elif request.method == 'POST':
        return render_template('wifi_settings.html', error_message='Settings can not be changed, the WiFi chipset is still booting.')


# Admin auto-login endpoint - simulates periodic admin activity
# In a real scenario, this would be an internal cron job or scheduled task
@app.route('/internal/admin_check', methods=['POST'])
def admin_check():
    """
    Internal endpoint that performs admin authentication.
    This simulates the admin user logging in periodically to check system status.
    An attacker can time their login to race with this endpoint.
    
    The race condition: When this endpoint authenticates the admin at the same
    time an attacker authenticates with test:test, the shared AuthState table
    can be corrupted, causing the attacker to receive admin's session data.
    """
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        # Perform admin authentication through vulnerable function
        auth_data, error = authenticate_user(admin.username, admin.password)
        if auth_data:
            return Response('Admin check completed', status=200)
    return Response('Admin check failed', status=500)
