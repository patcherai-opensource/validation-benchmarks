from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import hashlib
import time

from app import app

app.secret_key = hashlib.sha256(b'vaultkeeper-session-key-prod').hexdigest()


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login_id = request.form.get('login', '')
        pw = request.form.get('pw', '')
        duration_key = request.form.get('duree_session', '60')

        if not login_id or not pw:
            error = 'Please provide both credentials.'
        else:
            time.sleep(0.3)
            error = 'Authentication failed. Invalid credentials.'

    return render_template('login.html', error=error)


@app.route('/identify', methods=['POST'])
def identify():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': True, 'message': 'Invalid request format'}), 400

    login_id = data.get('login', '')
    pw_hash = data.get('pw', '')

    if not login_id or not pw_hash:
        return jsonify({'error': True, 'message': 'Missing credentials'}), 400

    time.sleep(0.2)
    return jsonify({
        'error': True,
        'message': 'Authentication failed',
        'value': ''
    })


@app.route('/status')
def status():
    return jsonify({
        'application': 'VaultKeeper',
        'version': '3.0.9',
        'status': 'running'
    })


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
