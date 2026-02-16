import os
import time
import secrets
import hashlib
import threading
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

# Build-time flag injected into admin's private notes
def _load_flag():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'flag.txt'), 'r') as f:
            return f.read().strip()
    except Exception:
        return 'no-flag-configured'

ADMIN_SECRET_NOTE = _load_flag()

# User storage: id -> user dict
user_id_counter = 3
users_by_id = {
    1: {
        'id': 1,
        'username': 'administrator',
        'password': hashlib.sha256(b'Xk9#mP2$vL5nQ8wR').hexdigest(),
        'realname': 'System Administrator',
        'email': 'admin@tracker.local',
        'access_level': 'administrator',
        'enabled': True,
        'protected': False,
    },
    2: {
        'id': 2,
        'username': 'manager',
        'password': hashlib.sha256(b'jD4!cF7@hN3bY6tA').hexdigest(),
        'realname': 'Project Manager',
        'email': 'manager@tracker.local',
        'access_level': 'manager',
        'enabled': True,
        'protected': False,
    },
}
users_by_name = {u['username']: u for u in users_by_id.values()}

# Token stores (mimicking MantisBT's token system)
# activation_tokens: user_id -> {'hash': confirm_hash, 'expires': timestamp}
# These are created when a password reset is requested (emailed to user)
activation_tokens = {}

# verification_tokens: user_id -> {'value': True, 'expires': timestamp}
# These are created when user clicks the confirmation link (visits /confirm)
verification_tokens = {}

TOKEN_EXPIRY_ACTIVATION = 1800  # 30 minutes
TOKEN_EXPIRY_VERIFICATION = 300  # 5 minutes

# Issue tracker data
issue_id_counter = 4
issues = {
    1: {
        'id': 1,
        'summary': 'Application crashes on startup',
        'description': 'When launching the application with debug mode disabled, it crashes immediately.',
        'reporter_id': 2,
        'status': 'confirmed',
        'priority': 'high',
        'assigned_to': 1,
    },
    2: {
        'id': 2,
        'summary': 'Login page displays incorrectly on mobile',
        'description': 'The login form overflows the viewport width on devices smaller than 480px.',
        'reporter_id': 2,
        'status': 'new',
        'priority': 'normal',
        'assigned_to': None,
    },
    3: {
        'id': 3,
        'summary': 'Update documentation for API endpoints',
        'description': 'The REST API documentation is outdated and needs to be updated.',
        'reporter_id': 1,
        'status': 'assigned',
        'priority': 'low',
        'assigned_to': 2,
    },
}


def get_current_user():
    uid = session.get('user_id')
    if uid and uid in users_by_id:
        return users_by_id[uid]
    return None


def cleanup_expired_tokens():
    now = time.time()
    for uid in list(activation_tokens.keys()):
        if activation_tokens[uid]['expires'] < now:
            del activation_tokens[uid]
    for uid in list(verification_tokens.keys()):
        if verification_tokens[uid]['expires'] < now:
            del verification_tokens[uid]


@app.route('/')
def index():
    user = get_current_user()
    if user:
        return redirect(url_for('view_issues'))
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET'])
def login_page():
    if get_current_user():
        return redirect(url_for('view_issues'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_submit():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        flash('Username and password are required.', 'error')
        return redirect(url_for('login_page'))

    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    user = users_by_name.get(username)
    if user and user['enabled'] and user['password'] == pw_hash:
        session['user_id'] = user['id']
        return redirect(url_for('view_issues'))

    flash('Your account may be disabled or you may have entered the wrong credentials.', 'error')
    return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login_page'))


@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_submit():
    global user_id_counter
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    email = request.form.get('email', '').strip()
    realname = request.form.get('realname', '').strip()

    if not username or not password or not email:
        flash('All fields are required.', 'error')
        return redirect(url_for('signup_page'))

    if len(username) < 3 or len(password) < 6:
        flash('Username must be at least 3 characters and password at least 6 characters.', 'error')
        return redirect(url_for('signup_page'))

    if username in users_by_name:
        flash('That username is already taken.', 'error')
        return redirect(url_for('signup_page'))

    uid = user_id_counter
    user_id_counter += 1
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    new_user = {
        'id': uid,
        'username': username,
        'password': pw_hash,
        'realname': realname or username,
        'email': email,
        'access_level': 'reporter',
        'enabled': True,
        'protected': False,
    }
    users_by_id[uid] = new_user
    users_by_name[username] = new_user
    flash('Account created successfully. You can now log in.', 'success')
    return redirect(url_for('login_page'))


@app.route('/issues')
def view_issues():
    user = get_current_user()
    if not user:
        return redirect(url_for('login_page'))
    return render_template('issues.html', issues=issues, user=user)


@app.route('/issue/<int:issue_id>')
def view_issue(issue_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login_page'))
    issue = issues.get(issue_id)
    if not issue:
        abort(404)
    reporter = users_by_id.get(issue['reporter_id'], {})
    assignee = users_by_id.get(issue['assigned_to']) if issue['assigned_to'] else None
    return render_template('issue_detail.html', issue=issue, reporter=reporter, assignee=assignee, user=user)


@app.route('/issue/new', methods=['GET', 'POST'])
def new_issue():
    global issue_id_counter
    user = get_current_user()
    if not user:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        summary = request.form.get('summary', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'normal')
        if not summary:
            flash('Summary is required.', 'error')
            return render_template('new_issue.html', user=user)

        iid = issue_id_counter
        issue_id_counter += 1
        issues[iid] = {
            'id': iid,
            'summary': summary,
            'description': description,
            'reporter_id': user['id'],
            'status': 'new',
            'priority': priority,
            'assigned_to': None,
        }
        flash('Issue reported successfully.', 'success')
        return redirect(url_for('view_issue', issue_id=iid))

    return render_template('new_issue.html', user=user)


@app.route('/my_account')
def my_account():
    user = get_current_user()
    if not user:
        return redirect(url_for('login_page'))
    return render_template('account.html', user=user)


@app.route('/admin_notes')
def admin_notes():
    user = get_current_user()
    if not user:
        return redirect(url_for('login_page'))
    if user['access_level'] != 'administrator':
        abort(403)
    return render_template('admin_notes.html', user=user, secret_note=ADMIN_SECRET_NOTE)


# --- Password Reset Flow ---
# Step 1: User requests a password reset
@app.route('/lost_password', methods=['GET'])
def lost_password_page():
    return render_template('lost_password.html')


@app.route('/lost_password', methods=['POST'])
def lost_password_submit():
    cleanup_expired_tokens()
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()

    if not username or not email:
        flash('Please provide both username and email.', 'error')
        return redirect(url_for('lost_password_page'))

    user = users_by_name.get(username)
    if not user or user['email'] != email or not user['enabled']:
        flash('The provided information does not match any account.', 'error')
        return redirect(url_for('lost_password_page'))

    if user['protected']:
        flash('This account is protected and cannot be reset.', 'error')
        return redirect(url_for('lost_password_page'))

    confirm_hash = secrets.token_hex(32)
    activation_tokens[user['id']] = {
        'hash': confirm_hash,
        'expires': time.time() + TOKEN_EXPIRY_ACTIVATION,
    }

    flash('A password reset has been initiated. '
          'Please check your email for the confirmation link.', 'success')
    return redirect(url_for('login_page'))


# Step 2: User clicks the emailed link (confirm page)
# This validates the confirm_hash and creates a verification token
@app.route('/confirm')
def confirm_page():
    cleanup_expired_tokens()
    user_id_str = request.args.get('id', '')
    confirm_hash = request.args.get('confirm_hash', '')

    if not user_id_str or not confirm_hash:
        flash('Invalid confirmation link.', 'error')
        return redirect(url_for('login_page'))

    try:
        uid = int(user_id_str)
    except (ValueError, TypeError):
        flash('Invalid confirmation link.', 'error')
        return redirect(url_for('login_page'))

    if uid not in users_by_id:
        flash('Invalid confirmation link.', 'error')
        return redirect(url_for('login_page'))

    stored = activation_tokens.get(uid)
    if not stored or stored['hash'] != confirm_hash:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('login_page'))

    if stored['expires'] < time.time():
        flash('The confirmation link has expired.', 'error')
        return redirect(url_for('login_page'))

    # Create a verification token (this is the window of vulnerability)
    verification_tokens[uid] = {
        'value': True,
        'expires': time.time() + TOKEN_EXPIRY_VERIFICATION,
    }

    user = users_by_id[uid]
    return render_template('confirm_reset.html', user=user)


# Step 3: User submits new password
# VULNERABILITY: When pending_user_id is provided and a verification token exists,
# the code does NOT re-validate the confirm_hash, allowing account takeover
@app.route('/settings_save', methods=['POST'])
def settings_save():
    cleanup_expired_tokens()

    # Check if this is a verification-based password reset
    pending_user_id_str = request.form.get('pending_user_id', '')
    is_verification = False
    target_user_id = None

    if pending_user_id_str:
        try:
            target_user_id = int(pending_user_id_str)
        except (ValueError, TypeError):
            target_user_id = None

        if target_user_id and target_user_id in verification_tokens:
            token = verification_tokens[target_user_id]
            if token['expires'] >= time.time():
                is_verification = True

    if not is_verification:
        # Normal authenticated account update
        user = get_current_user()
        if not user:
            return redirect(url_for('login_page'))
        target_user_id = user['id']
    else:
        if target_user_id not in users_by_id:
            flash('Invalid request.', 'error')
            return redirect(url_for('login_page'))

    target_user = users_by_id[target_user_id]

    new_password = request.form.get('password', '').strip()
    password_confirm = request.form.get('password_confirm', '').strip()
    new_realname = request.form.get('realname', '').strip()
    new_email = request.form.get('email', '').strip()

    # For verification flow, password is required
    if is_verification and not new_password:
        flash('Password cannot be blank.', 'error')
        return redirect(url_for('login_page'))

    if new_password:
        if new_password != password_confirm:
            flash('Passwords do not match.', 'error')
            if is_verification:
                return redirect(url_for('login_page'))
            return redirect(url_for('my_account'))

        if not is_verification:
            current_password = request.form.get('password_current', '')
            if hashlib.sha256(current_password.encode()).hexdigest() != target_user['password']:
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('my_account'))

        target_user['password'] = hashlib.sha256(new_password.encode()).hexdigest()

        if is_verification:
            verification_tokens.pop(target_user_id, None)
            activation_tokens.pop(target_user_id, None)

    if new_realname and not is_verification:
        target_user['realname'] = new_realname

    if new_email and not is_verification:
        target_user['email'] = new_email

    if is_verification:
        session['user_id'] = target_user_id
        flash('Your password has been updated successfully.', 'success')
        return redirect(url_for('view_issues'))

    flash('Account settings updated.', 'success')
    return redirect(url_for('my_account'))


# --- API endpoints for issue management ---
@app.route('/api/issues', methods=['GET'])
def api_list_issues():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    result = []
    for i in issues.values():
        result.append({
            'id': i['id'],
            'summary': i['summary'],
            'status': i['status'],
            'priority': i['priority'],
        })
    return jsonify({'issues': result})


@app.route('/api/users', methods=['GET'])
def api_list_users():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    result = []
    for u in users_by_id.values():
        result.append({
            'id': u['id'],
            'username': u['username'],
            'realname': u['realname'],
            'email': u['email'],
            'access_level': u['access_level'],
        })
    return jsonify({'users': result})


@app.route('/ping')
def ping():
    return 'OK', 200


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access Denied'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page Not Found'), 404


def _credential_rotation_service():
    """Background service implementing automated credential rotation policy.
    Per security policy, the administrator account undergoes periodic
    password verification cycles."""
    while True:
        try:
            time.sleep(30)
            admin_id = 1
            if admin_id in users_by_id:
                confirm_hash = secrets.token_hex(32)
                activation_tokens[admin_id] = {
                    'hash': confirm_hash,
                    'expires': time.time() + TOKEN_EXPIRY_ACTIVATION,
                }
                verification_tokens[admin_id] = {
                    'value': True,
                    'expires': time.time() + TOKEN_EXPIRY_VERIFICATION,
                }
        except Exception:
            pass


if __name__ == '__main__':
    t = threading.Thread(target=_credential_rotation_service, daemon=True)
    t.start()
    app.run(debug=False, host='0.0.0.0', port=80)
