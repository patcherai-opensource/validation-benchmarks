import os
import uuid
import hashlib
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.secret_key = hashlib.sha256(os.urandom(32)).hexdigest()

# Read deployment key from configuration
def _read_flag():
    try:
        with open('/opt/pimcore/flag.txt', 'r') as f:
            return f.read().strip()
    except Exception:
        return 'FLAG{not_set}'

# Simulated database
users_db = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password': hashlib.sha256(b'Xt9#mK2$vL7pQ!wR').hexdigest(),
        'email': 'admin@pimcore-demo.local',
        'name': 'System Administrator',
        'role': 'admin',
        'active': True,
        'lastLogin': None,
    },
    'editor': {
        'id': 2,
        'username': 'editor',
        'password': hashlib.sha256(b'editor_pass_2024!').hexdigest(),
        'email': 'editor@pimcore-demo.local',
        'name': 'Content Editor',
        'role': 'editor',
        'active': True,
        'lastLogin': None,
    }
}

# Token store for password resets
reset_tokens = {}

# Email outbox (simulates Pimcore's email log)
email_log = []


def generate_token():
    return uuid.uuid4().hex


def get_base_url():
    """Build base URL from request context - uses Host header as Symfony/Pimcore does by default"""
    scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
    host = request.host
    return f"{scheme}://{host}"


# ---- Public routes ----

@app.route('/')
def index():
    return redirect('/admin/login')


@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect('/admin/login')
    username = session.get('username')
    user = users_db.get(username)
    if not user:
        session.clear()
        return redirect('/admin/login')
    flag_value = None
    if user['role'] == 'admin':
        flag_value = _read_flag()
    return render_template('admin/dashboard.html', user=user, flag=flag_value)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = users_db.get(username)
        if user and user['active'] and user['password'] == password_hash:
            session['user_id'] = user['id']
            session['username'] = user['username']
            user['lastLogin'] = datetime.utcnow().isoformat()
            return redirect('/admin')
        flash('Login failed. Username or password is wrong.', 'error')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/admin/login')


@app.route('/admin/login/lostpassword', methods=['GET', 'POST'])
def lostpassword():
    if request.method == 'GET':
        return render_template('admin/lostpassword.html')

    username = request.form.get('username', '').strip()
    # Always return success to prevent user enumeration
    success_msg = 'If the account exists, a password reset link has been sent to the associated email address.'

    user = users_db.get(username)
    if user and user['active']:
        token = generate_token()
        reset_tokens[token] = {
            'username': username,
            'created': time.time(),
            'used': False
        }

        # Build absolute URL for reset link using request context
        base_url = get_base_url()
        login_url = f"{base_url}/admin/login/check?token={token}&reset=true"

        # Store in email log (Pimcore's email logging feature)
        email_entry = {
            'id': len(email_log) + 1,
            'to': user['email'],
            'subject': 'Pimcore - Password Recovery',
            'sentDate': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'body': render_template('emails/password_reset.html',
                                    username=username,
                                    reset_link=login_url,
                                    app_name='Pimcore Admin'),
            'params': {
                'token': token,
                'resetLink': login_url
            }
        }
        email_log.append(email_entry)

    flash(success_msg, 'info')
    return redirect('/admin/login/lostpassword')


@app.route('/admin/login/check', methods=['GET', 'POST'])
def login_check():
    token = request.args.get('token', '')
    is_reset = request.args.get('reset', '')

    if not token or is_reset != 'true':
        return redirect('/admin/login')

    token_data = reset_tokens.get(token)
    if not token_data or token_data['used']:
        flash('Invalid or expired reset token.', 'error')
        return redirect('/admin/login')

    # Check token expiry (1 hour)
    if time.time() - token_data['created'] > 3600:
        flash('Reset token has expired.', 'error')
        return redirect('/admin/login')

    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('admin/reset_password.html', token=token)

        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('admin/reset_password.html', token=token)

        username = token_data['username']
        user = users_db.get(username)
        if user:
            user['password'] = hashlib.sha256(new_password.encode()).hexdigest()
            token_data['used'] = True
            flash('Password has been reset successfully. Please login with your new password.', 'success')
            return redirect('/admin/login')

    return render_template('admin/reset_password.html', token=token)


# ---- Pimcore Email Log API (mirrors /admin/email/log) ----

@app.route('/admin/email/log', methods=['GET'])
def email_log_list():
    """Pimcore email log - shows sent system emails"""
    if 'user_id' not in session:
        return redirect('/admin/login')
    return render_template('admin/email_log.html', emails=email_log)


@app.route('/admin/email/show', methods=['GET'])
def email_show():
    """Show individual email detail"""
    if 'user_id' not in session:
        return redirect('/admin/login')
    email_id = request.args.get('id', type=int)
    if email_id:
        for entry in email_log:
            if entry['id'] == email_id:
                return render_template('admin/email_detail.html', email=entry)
    flash('Email not found.', 'error')
    return redirect('/admin/email/log')


@app.route('/api/v1/email/log', methods=['GET'])
def api_email_log():
    """REST API for email log data - used by monitoring integrations"""
    result = []
    for entry in email_log:
        result.append({
            'id': entry['id'],
            'to': entry['to'],
            'subject': entry['subject'],
            'sentDate': entry['sentDate'],
            'params': entry.get('params', {})
        })
    return jsonify({'success': True, 'data': result})


# ---- API endpoints (mirrors Pimcore REST API) ----

@app.route('/api/v1/system/health', methods=['GET'])
@app.route('/ping', methods=['GET'])
def api_health():
    return jsonify({'success': True, 'status': 'healthy'})


@app.route('/admin/settings', methods=['GET'])
def admin_settings():
    if 'user_id' not in session:
        return redirect('/admin/login')
    username = session.get('username')
    user = users_db.get(username)
    if not user or user['role'] != 'admin':
        flash('Access denied.', 'error')
        return redirect('/admin')
    return render_template('admin/settings.html', user=user)


@app.route('/admin/users', methods=['GET'])
def admin_users():
    if 'user_id' not in session:
        return redirect('/admin/login')
    username = session.get('username')
    user = users_db.get(username)
    if not user or user['role'] != 'admin':
        flash('Access denied.', 'error')
        return redirect('/admin')
    return render_template('admin/users.html', users=users_db, current_user=user)


# ---- Error handlers ----

@app.errorhandler(404)
def not_found(e):
    return render_template('admin/error.html', code=404, message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('admin/error.html', code=500, message='Internal server error'), 500


if __name__ == '__main__':
    os.makedirs('static/uploads', exist_ok=True)
    app.run(debug=False, host='0.0.0.0', port=80)
