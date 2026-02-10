from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import subprocess
import os
import secrets
import functools

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

USERS = {
    'admin': 'secret'
}

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in USERS and USERS[username] == password:
            session['user'] = username
            session['csrf_token'] = secrets.token_hex(16)
            return redirect(url_for('dashboard'))
        error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=session['user'], csrf_token=session.get('csrf_token', ''))

@app.route('/system/status')
@login_required
def system_status():
    return render_template('status.html', user=session['user'])

@app.route('/ajax/networking/get_wgkey.php', methods=['POST'])
@login_required
def get_wgkey():
    csrf_token = request.form.get('csrf_token', '')
    if csrf_token != session.get('csrf_token', ''):
        return jsonify({'status': 'error', 'message': 'Invalid CSRF token'}), 403
    
    entity = request.form.get('entity', '')
    
    if not entity:
        return jsonify({'status': 'error', 'message': 'Entity name required'}), 400
    
    pubkey_tmp = '/tmp/' + entity + '-public.key'
    privkey_tmp = '/tmp/' + entity + '-private.key'
    
    try:
        command = 'wg genkey | tee ' + privkey_tmp + ' | wg pubkey > ' + pubkey_tmp
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        
        pubkey = ''
        privkey = ''
        
        if os.path.exists(pubkey_tmp):
            with open(pubkey_tmp, 'r') as f:
                pubkey = f.read().strip()
        
        if os.path.exists(privkey_tmp):
            with open(privkey_tmp, 'r') as f:
                privkey = f.read().strip()
        
        return jsonify({
            'status': 'success',
            'pubkey': pubkey if pubkey else 'Key generation completed',
            'privkey': privkey if privkey else 'Key generation completed'
        })
    except Exception:
        return jsonify({'status': 'error', 'message': 'Key generation failed'}), 500

@app.route('/wireguard')
@login_required
def wireguard():
    return render_template('wireguard.html', user=session['user'], csrf_token=session.get('csrf_token', ''))

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
