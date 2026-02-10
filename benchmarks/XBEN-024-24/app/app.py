import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Login handler configuration (similar to eZ Publish's site.ini LoginHandler settings)
# When both 'standard' and 'ldap' handlers are enabled, a logic flaw exists
LOGIN_HANDLERS = ['standard', 'ldap']

# User database with password_hash_type field
# password_hash_type: 0 = no password (vulnerable), 1 = plaintext, 2 = hashed
users = {
    'admin': {
        'username': 'admin',
        'password': '',  # Empty password
        'password_hash_type': 0,  # No password set - vulnerable configuration
        'first_name': 'Admin',
        'last_name': 'User',
        'email': 'admin@example.com',
        'profile_picture': None,
        'is_admin': True
    },
    'guest': {
        'username': 'guest',
        'password': 'guestpass',
        'password_hash_type': 1,
        'first_name': 'Guest',
        'last_name': 'User',
        'email': 'guest@example.com',
        'profile_picture': None,
        'is_admin': False
    }
}

FLAG = os.environ.get('FLAG', '@FLAG@')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def _loginUser(login, password):
    """
    Vulnerable login function - mimics eZ Publish's kernel/classes/datatypes/ezuser/ezuser.php _loginUser
    
    BUG: This function does NOT check if login or password is empty.
    When used with both standard and ldap handlers, users with password_hash_type=0
    can be logged in without proper password verification.
    """
    # VULNERABLE: No check for empty login or password
    # The fix would be:
    # if not login or not password:
    #     return None
    
    if login not in users:
        return None
    
    user = users[login]
    
    # VULNERABLE: When password_hash_type is 0, password comparison is skipped
    # This mimics the eZ Publish bug where users with password_hash_type=0 could login
    # without a password when both standard and ldap/textfile handlers are enabled
    if user['password_hash_type'] == 0:
        # No password validation for users with password_hash_type=0
        return user
    
    # Normal password validation for other users
    if user['password'] == password:
        return user
    
    return None

def standard_login_handler(login, password):
    """Standard login handler - directly calls _loginUser"""
    return _loginUser(login, password)

def ldap_login_handler(login, password):
    """
    LDAP login handler simulation
    In eZ Publish, when this handler is enabled alongside standard,
    the standard handler's _loginUser is still called and the vulnerability is exposed
    """
    # LDAP authentication would normally happen here
    # For this simulation, we just return None (LDAP auth fails)
    # But the vulnerability is that standard handler is also checked
    return None

def check_user_login(login, password):
    """
    Login handler infrastructure - mimics eZUserLoginHandler::checkUser()
    Iterates through configured login handlers
    """
    for handler in LOGIN_HANDLERS:
        if handler == 'standard':
            user = standard_login_handler(login, password)
            if user:
                return user
        elif handler == 'ldap':
            user = ldap_login_handler(login, password)
            if user:
                return user
    return None

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('profile'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        if username in users:
            flash('Username already exists!')
        else:
            users[username] = {
                'username': username,
                'password': password,
                'password_hash_type': 1,  # New users have normal password
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'profile_picture': None,
                'is_admin': False
            }
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Use the vulnerable login handler infrastructure
        user = check_user_login(username, password)
        
        if user:
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users[username]
    
    if request.method == 'POST':
        user['first_name'] = request.form['first_name']
        user['last_name'] = request.form['last_name']
        user['email'] = request.form['email']
        
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user['profile_picture'] = filename
    
    # Flag is only shown to admin users
    show_flag = user.get('is_admin', False)
    return render_template('profile.html', user=user, flag=FLAG if show_flag else None)

@app.route('/about')
def about():
    """Information page about the system configuration"""
    return render_template('about.html', handlers=LOGIN_HANDLERS)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=False, host='0.0.0.0', port=80)

