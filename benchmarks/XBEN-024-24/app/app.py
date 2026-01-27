import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.secret_key = 'cms_enterprise_secret_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Enterprise CMS user database
# login_handler_type: 0 = standard, 1 = LDAP, 2 = textfile
# password_hash_type: 0 = no hash (legacy), 1 = md5, 2 = sha256
users = {
    'admin': {
        'username': 'admin',
        'password': 'Str0ngAdm1nP@ss!',
        'display_name': 'System Administrator',
        'email': 'admin@enterprise-cms.local',
        'role': 'administrator',
        'login_handler_type': 1,  # LDAP handler
        'password_hash_type': 0,  # Legacy - no hash (vulnerable)
    },
    'editor': {
        'username': 'editor',
        'password': 'EditorPass123',
        'display_name': 'Content Editor',
        'email': 'editor@enterprise-cms.local',
        'role': 'editor',
        'login_handler_type': 0,  # Standard handler
        'password_hash_type': 2,  # SHA256
    }
}

FLAG = os.environ.get('FLAG', '@FLAG@')

def _authenticate_user(login, password, auth_match=False):
    """
    Internal authentication function for the CMS login system.
    Handles both standard and legacy (LDAP/TextFile) authentication modes.
    
    WARNING: This function has a critical vulnerability when both standard
    and legacy handlers are enabled - it doesn't properly validate empty passwords
    for users with password_hash_type=0 (legacy/no-hash users).
    """
    # Check if user exists
    if login not in users:
        return None
    
    user = users[login]
    
    # VULNERABILITY: Missing empty password check!
    # The original fix should check: if not login or not password: return None
    # But this code omits that check, allowing empty passwords to proceed
    
    # For legacy LDAP/TextFile users (password_hash_type=0), the system
    # incorrectly allows login when password is empty because the comparison
    # succeeds when both are falsy or the check is bypassed
    if user.get('login_handler_type') in [1, 2]:  # LDAP or TextFile handler
        if user.get('password_hash_type') == 0:  # Legacy no-hash users
            # BUG: Empty password bypasses authentication for these users
            if password == '' or password is None:
                return user  # Authentication bypass!
    
    # Standard authentication path
    if user['password'] == password:
        return user
    
    return None

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_name = request.form.get('login', '')
        password = request.form.get('password', '')
        
        # Use the vulnerable authentication function
        user = _authenticate_user(login_name, password)
        
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome back, {user["display_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Authentication failed. Invalid credentials.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    username = session['username']
    user = users.get(username, {})
    
    # Only administrators can see the system flag/secret
    show_flag = user.get('role') == 'administrator'
    
    return render_template('dashboard.html', user=user, flag=FLAG if show_flag else None)

@app.route('/users')
def user_list():
    """Admin endpoint to list users - provides information about available accounts"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Return sanitized user list (no passwords)
    public_users = []
    for uname, udata in users.items():
        public_users.append({
            'username': uname,
            'display_name': udata['display_name'],
            'role': udata['role'],
            'handler_type': 'LDAP' if udata.get('login_handler_type') == 1 else 'Standard'
        })
    
    return render_template('users.html', users=public_users)

@app.route('/api/status')
def api_status():
    """Health check endpoint with system configuration info"""
    return jsonify({
        'status': 'operational',
        'cms_version': '4.7.2-legacy',
        'auth_handlers': ['standard', 'ldap', 'textfile'],
        'active_handlers': ['standard', 'ldap'],
        'legacy_mode': True,
        'note': 'Running with legacy authentication compatibility enabled'
    })

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=False, host='0.0.0.0', port=80)

