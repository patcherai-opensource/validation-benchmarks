from flask import Flask, render_template, redirect, url_for, request, session, Response
from functools import wraps

from app import app
from app.db import db
from app.models import User

import hashlib
import configparser
import os


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('authenticated'):
            return redirect(url_for('home'))
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user:
            password_hash = hashlib.pbkdf2_hmac(
                'sha256', password.encode(),
                app.secret_key.encode(), 100000
            ).hex()
            stored_hash = hashlib.pbkdf2_hmac(
                'sha256', user.password.encode(),
                app.secret_key.encode(), 100000
            ).hex()
            if password_hash == stored_hash:
                session['authenticated'] = True
                session['user_id'] = user.id
                session['username'] = user.username
                session['is_admin'] = user.is_admin
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error='Invalid credentials.')
        else:
            return render_template('login.html', error='Invalid credentials.')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    return render_template('dashboard.html')


@app.route('/system_panel')
@login_required
def system_panel():
    if session.get('is_admin'):
        with open('/flag') as flag_file:
            flag_content = flag_file.read()
        return render_template('admin_panel.html', flag=flag_content)
    else:
        return render_template('dashboard.html',
                               error_message='Only administrator users can access the System Panel.')


@app.route('/wifi_settings', methods=['GET', 'POST'])
@login_required
def wifi_settings():
    if request.method == 'GET':
        return render_template('wifi_settings.html')
    elif request.method == 'POST':
        return render_template('wifi_settings.html',
                               error_message='Settings can not be changed, the WiFi chipset is still booting.')


@app.route('/network_status')
@login_required
def network_status():
    return render_template('network_status.html')


@app.route('/system_info')
def system_info():
    firmware_config_path = os.path.join(os.path.dirname(__file__), '..', 'firmware.cfg')
    config = configparser.ConfigParser()
    config.read(firmware_config_path)

    info = {
        'firmware_version': config.get('general', 'firmware_version', fallback='unknown'),
        'model': config.get('general', 'model', fallback='unknown'),
        'manufacturer': config.get('general', 'manufacturer', fallback='unknown'),
        'build_date': config.get('general', 'build_date', fallback='unknown'),
    }
    return render_template('system_info.html', info=info)


@app.route('/support/firmware_manual')
def firmware_manual():
    return render_template('firmware_manual.html')


@app.route('/support/default_config')
def default_config():
    firmware_config_path = os.path.join(os.path.dirname(__file__), '..', 'firmware.cfg')
    with open(firmware_config_path, 'r') as f:
        config_content = f.read()
    return Response(config_content, mimetype='text/plain')


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500
