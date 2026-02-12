import os
import time
import secrets
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

# Read flag from file planted at build time
FLAG_FILE = os.path.join(os.path.dirname(__file__), '.admin_project_notes')
try:
    with open(FLAG_FILE, 'r') as f:
        ADMIN_FLAG_DATA = f.read().strip()
except FileNotFoundError:
    ADMIN_FLAG_DATA = ''

# Simulated database - users table
# In production, user IDs are auto-incrementing integers
next_user_id = 3

users_db = {
    1: {
        'id': 1,
        'username': 'administrator',
        'password': hashlib.sha256(os.urandom(32)).hexdigest(),  # random password, unknown
        'realname': 'MantisBT Administrator',
        'email': 'admin@mantis.local',
        'access_level': 90,  # ADMINISTRATOR
        'enabled': True,
        'cookie_string': secrets.token_hex(32),
        'date_created': int(time.time()) - 86400 * 365,
    },
    2: {
        'id': 2,
        'username': 'developer',
        'password': hashlib.sha256(b'dev2024secure').hexdigest(),
        'realname': 'Dev User',
        'email': 'dev@mantis.local',
        'access_level': 55,  # DEVELOPER
        'enabled': True,
        'cookie_string': secrets.token_hex(32),
        'date_created': int(time.time()) - 86400 * 30,
    }
}

# Simulated tokens table
# token_type: 1 = TOKEN_ACCOUNT_VERIFY, 5 = TOKEN_ACCOUNT_ACTIVATION
verification_tokens = {}

# Projects table (admin-only sensitive data)
projects_db = {
    1: {
        'id': 1,
        'name': 'Internal Security Audit',
        'description': 'Tracking internal security vulnerabilities and configuration issues.',
        'access_level': 90,
        'status': 10,  # development
        'enabled': True,
    },
    2: {
        'id': 2,
        'name': 'Public Bug Reports',
        'description': 'Community-reported bugs for the main product.',
        'access_level': 10,
        'status': 10,
        'enabled': True,
    }
}

# Issues/bugs table
issues_db = {
    1: {
        'id': 1,
        'project_id': 2,
        'summary': 'Login page CSS broken on mobile',
        'description': 'The login form does not render correctly on smaller screens.',
        'reporter_id': 2,
        'priority': 30,
        'status': 50,
        'date_submitted': int(time.time()) - 86400 * 5,
    },
    2: {
        'id': 2,
        'project_id': 2,
        'summary': 'Export CSV produces malformed output',
        'description': 'When exporting issue list to CSV, special characters cause parsing errors.',
        'reporter_id': 2,
        'priority': 40,
        'status': 10,
        'date_submitted': int(time.time()) - 86400 * 2,
    },
    3: {
        'id': 3,
        'project_id': 1,
        'summary': 'Credential rotation audit notes',
        'description': ADMIN_FLAG_DATA,
        'reporter_id': 1,
        'priority': 70,
        'status': 10,
        'date_submitted': int(time.time()) - 3600,
    }
}


def get_user_by_id(user_id):
    return users_db.get(user_id)


def get_user_by_username(username):
    for uid, user in users_db.items():
        if user['username'] == username:
            return user
    return None


def generate_confirm_hash():
    return secrets.token_hex(16)


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# ============================================================
# Routes
# ============================================================

@app.route('/ping')
def ping():
    return 'OK', 200


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('my_view'))
    return redirect(url_for('login_page'))


@app.route('/login_page.php', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/login.php', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    user = get_user_by_username(username)
    if user and user['password'] == hash_password(password) and user['enabled']:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['access_level'] = user['access_level']
        return redirect(url_for('my_view'))
    flash('Your account may be disabled or blocked or the username/password you entered is incorrect.')
    return redirect(url_for('login_page'))


@app.route('/logout_page.php')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


@app.route('/signup_page.php', methods=['GET'])
def signup_page():
    return render_template('signup.html')


@app.route('/signup.php', methods=['POST'])
def signup():
    global next_user_id

    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    realname = request.form.get('realname', '').strip()

    if not username or not email:
        flash('Username and email are required.')
        return redirect(url_for('signup_page'))

    if get_user_by_username(username):
        flash('That username is already being used. Please go back and select a different one.')
        return redirect(url_for('signup_page'))

    for u in users_db.values():
        if u['email'] == email:
            flash('That email address is already being used. Please go back and select a different one.')
            return redirect(url_for('signup_page'))

    uid = next_user_id
    next_user_id += 1

    confirm_hash = generate_confirm_hash()

    users_db[uid] = {
        'id': uid,
        'username': username,
        'password': '',  # no password until confirmed
        'realname': realname or username,
        'email': email,
        'access_level': 25,  # REPORTER
        'enabled': False,  # not enabled until verified
        'cookie_string': secrets.token_hex(32),
        'date_created': int(time.time()),
    }

    # Store verification token
    verification_tokens[uid] = {
        'token_type': 5,  # TOKEN_ACCOUNT_ACTIVATION
        'confirm_hash': confirm_hash,
        'timestamp': int(time.time()),
        'expiry': int(time.time()) + 300,  # 5 minute window
    }

    flash('Signup successful. An email with a confirmation link has been sent to your address.')
    return redirect(url_for('login_page'))


@app.route('/verify.php', methods=['GET'])
def verify():
    """
    Handles email verification links.
    When a user clicks the confirm link, this creates a TOKEN_ACCOUNT_VERIFY
    and shows them the form to set their password.
    """
    user_id = request.args.get('id', type=int)
    confirm_hash = request.args.get('confirm_hash', '')

    if not user_id or not confirm_hash:
        flash('Invalid verification link.')
        return redirect(url_for('login_page'))

    user = get_user_by_id(user_id)
    if not user:
        flash('Account not found.')
        return redirect(url_for('login_page'))

    token = verification_tokens.get(user_id)
    if not token:
        flash('No pending verification found.')
        return redirect(url_for('login_page'))

    if token['confirm_hash'] != confirm_hash:
        flash('Invalid confirmation hash.')
        return redirect(url_for('login_page'))

    if time.time() > token['expiry']:
        flash('Verification link has expired.')
        return redirect(url_for('login_page'))

    # Upgrade token to TOKEN_ACCOUNT_VERIFY - user has clicked the link
    verification_tokens[user_id] = {
        'token_type': 1,  # TOKEN_ACCOUNT_VERIFY
        'confirm_hash': confirm_hash,
        'timestamp': int(time.time()),
        'expiry': int(time.time()) + 300,  # 5 more minutes to complete
    }

    return render_template('account_update.html', user_id=user_id, confirm_hash=confirm_hash)


@app.route('/account_update.php', methods=['POST'])
def account_update():
    """
    Processes account verification / password reset completion.
    Accepts verify_user_id to finalize account setup or password reset.
    """
    verify_user_id = request.form.get('verify_user_id', type=int)

    if verify_user_id:
        user = get_user_by_id(verify_user_id)
        if not user:
            flash('Account not found.')
            return redirect(url_for('login_page'))

        # Check if there is a valid TOKEN_ACCOUNT_VERIFY for this user
        token = verification_tokens.get(verify_user_id)
        if not token or token['token_type'] != 1:
            flash('No pending verification for this account.')
            return redirect(url_for('login_page'))

        if time.time() > token['expiry']:
            del verification_tokens[verify_user_id]
            flash('Verification has expired. Please request a new one.')
            return redirect(url_for('login_page'))

        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        realname = request.form.get('realname', '')

        if not password or password != password_confirm:
            flash('Passwords do not match or are empty.')
            return render_template('account_update.html',
                                   user_id=verify_user_id,
                                   confirm_hash=request.form.get('confirm_hash', ''))

        # Update user account
        user['password'] = hash_password(password)
        if realname:
            user['realname'] = realname
        user['enabled'] = True

        # Clean up token
        del verification_tokens[verify_user_id]

        flash('Account updated successfully. You can now log in.')
        return redirect(url_for('login_page'))

    # Normal account update (requires session)
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login_page'))

    realname = request.form.get('realname', '')
    email = request.form.get('email', '')

    if realname:
        user['realname'] = realname
    if email:
        user['email'] = email

    flash('Account preferences updated.')
    return redirect(url_for('account_page'))


@app.route('/lost_pwd_page.php', methods=['GET'])
def lost_password_page():
    return render_template('lost_password.html')


@app.route('/lost_pwd.php', methods=['POST'])
def lost_password():
    """
    Initiates password reset. Creates a pending activation token.
    In production, sends email with confirmation link.
    """
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()

    user = None
    if username:
        user = get_user_by_username(username)
    elif email:
        for u in users_db.values():
            if u['email'] == email:
                user = u
                break

    if user:
        confirm_hash = generate_confirm_hash()
        verification_tokens[user['id']] = {
            'token_type': 5,  # TOKEN_ACCOUNT_ACTIVATION
            'confirm_hash': confirm_hash,
            'timestamp': int(time.time()),
            'expiry': int(time.time()) + 300,
        }

    # Always show success to prevent user enumeration
    flash('A confirmation link was sent to the associated email address. Please check your inbox.')
    return redirect(url_for('login_page'))


@app.route('/my_view_page.php')
def my_view():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login_page'))

    # Get issues visible to this user
    visible_issues = []
    for issue in issues_db.values():
        project = projects_db.get(issue['project_id'])
        if project and user['access_level'] >= project['access_level']:
            visible_issues.append({
                'id': issue['id'],
                'project': project['name'],
                'summary': issue['summary'],
                'priority': issue['priority'],
                'status': issue['status'],
            })

    return render_template('my_view.html', user=user, issues=visible_issues)


@app.route('/view.php')
def view_issue():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login_page'))

    issue_id = request.args.get('id', type=int)
    if not issue_id:
        flash('Issue not found.')
        return redirect(url_for('my_view'))

    issue = issues_db.get(issue_id)
    if not issue:
        flash('Issue not found.')
        return redirect(url_for('my_view'))

    project = projects_db.get(issue['project_id'])
    if not project or user['access_level'] < project['access_level']:
        flash('Access denied.')
        return redirect(url_for('my_view'))

    return render_template('view_issue.html', user=user, issue=issue, project=project)


@app.route('/manage_proj_page.php')
def manage_projects():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login_page'))

    visible_projects = []
    for project in projects_db.values():
        if user['access_level'] >= project['access_level']:
            visible_projects.append(project)

    return render_template('manage_projects.html', user=user, projects=visible_projects)


@app.route('/account_page.php')
def account_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login_page'))

    return render_template('account.html', user=user)


def ensure_admin_verification_pending():
    """Maintains pending password reset state for accounts with scheduled credential rotation."""
    admin_id = 1
    token = verification_tokens.get(admin_id)

    if not token or time.time() > token.get('expiry', 0):
        confirm_hash = generate_confirm_hash()
        verification_tokens[admin_id] = {
            'token_type': 1,  # TOKEN_ACCOUNT_VERIFY - admin clicked the link
            'confirm_hash': confirm_hash,
            'timestamp': int(time.time()),
            'expiry': int(time.time()) + 600,  # 10 minute window
        }


@app.before_request
def before_request_handler():
    ensure_admin_verification_pending()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_msg='Page not found.'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_msg='An internal error occurred.'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
