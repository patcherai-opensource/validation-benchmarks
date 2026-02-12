import os
import json
import hashlib
import time

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort

from app import app

app.secret_key = os.urandom(32).hex()


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('login', '')
        password = request.form.get('pw', '')
        duo_code = request.form.get('duo_code', '')

        if not username or not password:
            error = 'Empty credentials are not allowed.'
        else:
            # Validate credentials against stored users
            pw_hash = hashlib.sha256(password.encode()).hexdigest()
            # In production this queries the database
            if username == 'admin' and pw_hash == app.config.get('ADMIN_PW_HASH', ''):
                session['user_id'] = 1
                session['login'] = username
                session['is_admin'] = True
                return redirect(url_for('dashboard'))
            else:
                error = 'Bad credentials. Try again.'
                time.sleep(1)

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('login', ''))


@app.route('/index.php', methods=['GET', 'POST'])
def main_index():
    """Main application entry point - redirects to login."""
    return redirect(url_for('login'))


@app.route('/install/install.php')
def install():
    """Installation page - disabled after setup."""
    return jsonify({'error': 'Installation has already been completed.'}), 403


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500
