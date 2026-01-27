from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, make_response, jsonify

from app import app
from app.models import UserPreferences, Notification
from app.crypto import encrypt_cookie, decrypt_cookie, APP_KEY
from uuid import uuid4
import pickle
import base64
import json
import os
import hmac
import hashlib


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'ArtisanCMS/5.6.29'
    response.headers['X-Framework'] = 'PHP/7.2.0'
    return response


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    """Main dashboard showing user session info"""
    session_data = None
    user_id = None
    deserialized_value = None
    
    if request.cookies.get('artisan_session'):
        try:
            # Decrypt and unserialize the session cookie
            # VULNERABILITY: Insecure deserialization of cookie data
            encrypted_value = request.cookies.get('artisan_session')
            decrypted = decrypt_cookie(encrypted_value)
            if decrypted:
                # This is the vulnerable unserialize call - similar to Laravel's behavior
                session_data = pickle.loads(decrypted)
                
                # If the deserialized object is a string (e.g., from os.getenv), 
                # it will be displayed. This is how the flag gets leaked.
                if isinstance(session_data, str):
                    deserialized_value = session_data
                    user_id = 'deserialized_data'
                else:
                    user_id = getattr(session_data, 'user_id', 'anonymous')
        except Exception as e:
            # Session corrupted or tampered
            session_data = None
    
    if session_data is None:
        # Create new session
        user_id = uuid4().hex[:8]
        session_obj = UserPreferences(user_id=user_id, theme='light', notifications=True)
        encrypted = encrypt_cookie(pickle.dumps(session_obj))
        
        response = make_response(render_template('dashboard.html', 
                                                  user_id=user_id, 
                                                  session=session_obj,
                                                  notifications=[],
                                                  deserialized_value=None))
        response.set_cookie('artisan_session', encrypted, httponly=False)
        return response
    
    # Get notifications from xsrf_token cookie if present
    notifications = []
    if request.cookies.get('xsrf_token'):
        try:
            encrypted_value = request.cookies.get('xsrf_token')
            decrypted = decrypt_cookie(encrypted_value)
            if decrypted:
                # Another vulnerable unserialize call
                result = pickle.loads(decrypted)
                if isinstance(result, list):
                    notifications = result
                elif isinstance(result, str):
                    # If it's a string (e.g., flag from os.getenv), display it
                    deserialized_value = result
        except:
            notifications = []
    
    return render_template('dashboard.html', 
                          user_id=user_id, 
                          session=session_data if not isinstance(session_data, str) else None,
                          notifications=notifications,
                          deserialized_value=deserialized_value)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile page"""
    if request.method == 'GET':
        session_data = None
        if request.cookies.get('artisan_session'):
            try:
                encrypted_value = request.cookies.get('artisan_session')
                decrypted = decrypt_cookie(encrypted_value)
                if decrypted:
                    session_data = pickle.loads(decrypted)
                    if isinstance(session_data, str):
                        # Deserialized to a string - return it
                        return render_template('profile.html', session=None, deserialized_value=session_data)
            except:
                pass
        return render_template('profile.html', session=session_data, deserialized_value=None)
    
    # POST - update profile
    if request.cookies.get('artisan_session'):
        try:
            encrypted_value = request.cookies.get('artisan_session')
            decrypted = decrypt_cookie(encrypted_value)
            if decrypted:
                session_data = pickle.loads(decrypted)
                
                # Only update if it's a proper session object
                if hasattr(session_data, 'theme'):
                    session_data.theme = request.form.get('theme', 'light')
                    session_data.notifications = request.form.get('notifications') == 'on'
                    session_data.display_name = request.form.get('display_name', '')
                    
                    encrypted = encrypt_cookie(pickle.dumps(session_data))
                    response = make_response(redirect(url_for('profile')))
                    response.set_cookie('artisan_session', encrypted, httponly=False)
                    return response
        except:
            pass
    
    return redirect(url_for('dashboard'))


@app.route('/notifications')
def notifications():
    """View notifications"""
    notif_list = []
    deserialized_value = None
    
    if request.cookies.get('xsrf_token'):
        try:
            encrypted_value = request.cookies.get('xsrf_token')
            decrypted = decrypt_cookie(encrypted_value)
            if decrypted:
                result = pickle.loads(decrypted)
                if isinstance(result, list):
                    notif_list = result
                elif isinstance(result, str):
                    deserialized_value = result
        except:
            notif_list = []
    
    return render_template('notifications.html', notifications=notif_list, deserialized_value=deserialized_value)


@app.route('/api/add-notification', methods=['POST'])
def add_notification():
    """Add a notification (for demo purposes)"""
    message = request.form.get('message', 'New notification')
    
    notif_list = []
    if request.cookies.get('xsrf_token'):
        try:
            encrypted_value = request.cookies.get('xsrf_token')
            decrypted = decrypt_cookie(encrypted_value)
            if decrypted:
                result = pickle.loads(decrypted)
                if isinstance(result, list):
                    notif_list = result
        except:
            notif_list = []
    
    notif_list.append(Notification(message=message))
    encrypted = encrypt_cookie(pickle.dumps(notif_list))
    
    response = make_response(redirect(url_for('notifications')))
    response.set_cookie('xsrf_token', encrypted, httponly=False)
    return response


@app.route('/settings')
def settings():
    """Settings page showing app configuration"""
    return render_template('settings.html')


@app.route('/api/debug/config')
def debug_config():
    """Debug endpoint - exposes some configuration (common in dev environments)"""
    # This endpoint intentionally leaks the APP_KEY for exploitation
    config = {
        'app_name': 'ArtisanCMS',
        'version': '5.6.29',
        'environment': 'development',
        'debug': True,
        'app_key': APP_KEY,  # Leaked! This allows forging cookies
        'cipher': 'AES-256-CBC',
        'session_driver': 'cookie',
        'session_cookie': 'artisan_session'
    }
    return jsonify(config)


@app.route('/logout')
def logout():
    """Clear session"""
    response = make_response(redirect(url_for('dashboard')))
    response.delete_cookie('artisan_session')
    response.delete_cookie('xsrf_token')
    return response


@app.route('/about')
def about():
    return render_template('about.html')
