from flask import Flask, render_template, redirect, url_for, request, session

from app import app, pending_auth
from app.db import db
from app.models import User

import hashlib
import time


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('login.html', error='Page not found.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('login.html', error='An error occurred.'), 500


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template('login.html', error='Invalid username.')
        
        user_password_hashed = hashlib.pbkdf2_hmac('sha256', user.password.encode(), app.secret_key.encode(), 100000).hex()
        provided_password_hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), app.secret_key.encode(), 100000).hex()
        
        if user_password_hashed != provided_password_hashed:
            return render_template('login.html', error='Wrong password.')
        
        auth_obj = {
            'username': user.username,
            'user_id': user.id,
            'is_admin': user.is_admin,
            'email': user.email
        }
        
        pending_auth['current_auth'] = auth_obj
        
        time.sleep(0.1)
        
        current_auth = pending_auth.get('current_auth')
        
        session['username'] = current_auth['username']
        session['user_id'] = current_auth['user_id']
        session['is_admin'] = current_auth['is_admin']
        session['email'] = current_auth['email']
        session['password_hash'] = provided_password_hashed
        
        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin_panel')
def admin_panel():
    if not session.get('user_id'):
        return render_template('login.html', error='Please login first.')
    
    if session.get('is_admin'):
        with open('/flag') as flag_file:
            flag_content = flag_file.read()
        return render_template('admin_panel.html', flag=flag_content)
    else:
        return render_template('dashboard.html', error_message='Only administrator users can open this section.')


@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return render_template('login.html', error='Please login first.')
    
    return render_template('dashboard.html')


@app.route('/wifi_settings', methods=['GET', 'POST'])
def wifi_settings():
    if not session.get('user_id'):
        return render_template('login.html', error='Please login first.')

    if request.method == 'GET':
        return render_template('wifi_settings.html')
    elif request.method == 'POST':
        return render_template('wifi_settings.html', error_message='Settings can not be changed, the WiFi chipset is still booting.')
