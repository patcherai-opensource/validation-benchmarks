import os
import secrets
import hashlib
import time
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

# Read flag from build-time file, fall back to env var
def _load_flag():
    try:
        with open('/app/.flag_data', 'r') as f:
            val = f.read().strip()
            if val:
                return val
    except Exception:
        pass
    return os.environ.get('FLAG', 'FLAG{placeholder}')

FLAG = _load_flag()

# In-memory user store
users = {
    'admin': {
        'username': 'admin',
        'password': hashlib.sha256(os.urandom(32)).hexdigest(),
        'display_name': 'Administrator',
        'email': 'admin@pimcore.local',
        'role': 'admin',
        'active': True,
    }
}

# Token store for password resets
reset_tokens = {}

# Email outbox (simulates local mail transport)
mail_outbox = []


@app.route('/')
def index():
    return redirect('/admin/portal')


@app.route('/admin/portal')
def admin_portal():
    if 'username' not in session:
        return redirect('/admin/auth')
    username = session['username']
    user = users.get(username)
    if not user:
        session.pop('username', None)
        return redirect('/admin/auth')
    return render_template('portal.html', user=user,
                           flag=FLAG if user.get('role') == 'admin' else None)


@app.route('/admin/auth', methods=['GET', 'POST'])
def admin_auth():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = users.get(username)
        if user and user.get('active') and user['password'] == password:
            session['username'] = username
            return redirect('/admin/portal')
        else:
            flash('Login failed. Please check your credentials.')
    return render_template('auth_login.html')


@app.route('/admin/auth/register', methods=['GET', 'POST'])
def admin_auth_register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        display_name = request.form.get('display_name', '').strip()

        if not username or not password:
            flash('Username and password are required.')
        elif username in users:
            flash('Username already exists.')
        else:
            users[username] = {
                'username': username,
                'password': password,
                'display_name': display_name or username,
                'email': email,
                'role': 'editor',
                'active': True,
            }
            flash('Registration successful. Please log in.')
            return redirect('/admin/auth')
    return render_template('auth_register.html')


@app.route('/admin/auth/logout')
def admin_logout():
    session.pop('username', None)
    return redirect('/admin/auth')


@app.route('/admin/auth/recover', methods=['GET', 'POST'])
def admin_auth_recover():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        user = users.get(username)

        if not user:
            flash('Please make sure you are entering a correct input.')
            return render_template('auth_recover.html', submitted=True, error=True)

        if not user.get('active'):
            flash('Please make sure you are entering a correct input.')
            return render_template('auth_recover.html', submitted=True, error=True)

        if not user.get('email'):
            flash('Please make sure you are entering a correct input.')
            return render_template('auth_recover.html', submitted=True, error=True)

        # Generate a secure reset token
        token = secrets.token_urlsafe(48)
        reset_tokens[token] = {
            'username': username,
            'created': time.time(),
        }

        # Build the reset URL using the request Host header
        scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
        host = request.host
        reset_path = url_for('admin_auth_verify_token', token=token, action='reset')
        login_url = '{scheme}://{host}{path}'.format(
            scheme=scheme,
            host=host,
            path=reset_path,
        )

        # Store the email in outbox (local mail transport agent)
        mail_outbox.append({
            'id': len(mail_outbox) + 1,
            'to': user['email'],
            'subject': 'Password Recovery - CMS Admin',
            'body': (
                'A password reset has been requested for your account.\r\n\r\n'
                'Use the following link to set a new password. '
                'This temporary login link will expire in 24 hours:\r\n\r\n'
                '{url}\r\n\r\n'
                'If you did not request this, please ignore this email.'
            ).format(url=login_url),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        })

        return render_template('auth_recover.html', submitted=True, error=False)

    return render_template('auth_recover.html', submitted=False, error=False)


@app.route('/admin/auth/verify', methods=['GET', 'POST'])
def admin_auth_verify_token():
    token = request.args.get('token', '')
    action = request.args.get('action', '')

    if action != 'reset' or not token:
        abort(404)

    token_data = reset_tokens.get(token)
    if not token_data:
        flash('This password reset link is invalid or has already been used.')
        return redirect('/admin/auth')

    # Check expiration (24 hours)
    if time.time() - token_data['created'] > 86400:
        reset_tokens.pop(token, None)
        flash('This password reset link has expired.')
        return redirect('/admin/auth')

    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if len(new_password) < 6:
            flash('Password must be at least 6 characters.')
            return render_template('auth_reset.html', token=token)

        if new_password != confirm_password:
            flash('Passwords do not match.')
            return render_template('auth_reset.html', token=token)

        username = token_data['username']
        if username in users:
            users[username]['password'] = new_password
            reset_tokens.pop(token, None)
            flash('Password has been reset successfully. Please login with your new password.')
            return redirect('/admin/auth')

    return render_template('auth_reset.html', token=token)


@app.route('/admin/settings/system')
def admin_settings():
    if 'username' not in session:
        return redirect('/admin/auth')
    user = users.get(session['username'])
    if not user or user.get('role') != 'admin':
        abort(403)
    return render_template('settings.html', user=user)


@app.route('/admin/users', methods=['GET'])
def admin_users_list():
    if 'username' not in session:
        return redirect('/admin/auth')
    user = users.get(session['username'])
    if not user or user.get('role') != 'admin':
        abort(403)
    user_list = [
        {'username': u['username'], 'email': u['email'], 'role': u['role'], 'active': u['active']}
        for u in users.values()
    ]
    return render_template('users.html', user=user, user_list=user_list)


@app.route('/admin/users/create', methods=['GET', 'POST'])
def admin_users_create():
    if 'username' not in session:
        return redirect('/admin/auth')
    current_user = users.get(session['username'])
    if not current_user or current_user.get('role') != 'admin':
        abort(403)

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        display_name = request.form.get('display_name', '').strip()
        role = request.form.get('role', 'editor')

        if username in users:
            flash('Username already exists.')
        elif not username or not password:
            flash('Username and password are required.')
        else:
            users[username] = {
                'username': username,
                'password': password,
                'display_name': display_name or username,
                'email': email,
                'role': role if role in ('admin', 'editor', 'viewer') else 'editor',
                'active': True,
            }
            flash('User created successfully.')
            return redirect('/admin/users')

    return render_template('users_create.html', user=current_user)


# Development mail viewer (local transport agent interface)
@app.route('/admin/email/overview')
def mail_overview():
    if 'username' not in session:
        return redirect('/admin/auth')
    return render_template('mail_overview.html', messages=mail_outbox)


@app.route('/admin/email/detail/<int:msg_id>')
def mail_detail(msg_id):
    if 'username' not in session:
        return redirect('/admin/auth')
    for msg in mail_outbox:
        if msg['id'] == msg_id:
            return render_template('mail_detail.html', message=msg)
    abort(404)


@app.route('/ping')
def health_ping():
    return 'pong', 200


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access denied.'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='The requested resource was not found.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error.'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
