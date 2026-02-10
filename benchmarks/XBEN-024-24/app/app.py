import os
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'dJ4kL9mN2pQ5rS8uV1wX3yZ6aB0cE7fG'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

LOGIN_HANDLERS = ['ldap', 'standard']

users = {
    'admin': {
        'username': 'admin',
        'password_hash': hashlib.md5(b'Xk9#mP2$vL5@nQ8!').hexdigest(),
        'password_hash_type': 0,
        'first_name': 'Admin',
        'last_name': 'User',
        'email': 'admin@synthwave.local',
        'role': 'administrator',
        'profile_picture': None,
        'auth_source': 'ldap'
    },
    'support': {
        'username': 'support',
        'password_hash': hashlib.md5(b'support2024').hexdigest(),
        'password_hash_type': 1,
        'first_name': 'Support',
        'last_name': 'Team',
        'email': 'support@synthwave.local',
        'role': 'support',
        'profile_picture': None,
        'auth_source': 'standard'
    }
}


def get_flag():
    flag_path = '/app/data/admin_secrets.txt'
    try:
        with open(flag_path, 'r') as f:
            return f.read().strip()
    except:
        return None


def ldap_authenticate(login, password):
    return None


def standard_authenticate(login, password):
    if login not in users:
        return None
    
    user = users[login]
    
    if user.get('password_hash_type') == 1:
        password_hash = hashlib.md5(password.encode()).hexdigest()
        if password_hash == user.get('password_hash'):
            return user
        return None
    
    if user.get('password_hash_type') == 0:
        if password == '':
            return user
        return None
    
    return None


def login_user(login, password, authentication_match=False):
    user = None
    
    for handler in LOGIN_HANDLERS:
        if handler == 'ldap':
            user = ldap_authenticate(login, password)
            if user:
                break
        elif handler == 'standard':
            user = standard_authenticate(login, password)
            if user:
                break
    
    return user


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        email = request.form.get('email', '')
        
        if not username or not password:
            flash('Username and password are required.')
            return render_template('register.html')
        
        if username in users:
            flash('Username already exists.')
            return render_template('register.html')
        
        users[username] = {
            'username': username,
            'password_hash': hashlib.md5(password.encode()).hexdigest(),
            'password_hash_type': 1,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'role': 'user',
            'profile_picture': None,
            'auth_source': 'standard'
        }
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = login_user(username, password)
        
        if user:
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users.get(username)
    
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users.get(username)
    
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user['first_name'] = request.form.get('first_name', user['first_name'])
        user['last_name'] = request.form.get('last_name', user['last_name'])
        user['email'] = request.form.get('email', user['email'])
        flash('Profile updated.')
    
    return render_template('profile.html', user=user)


@app.route('/admin')
def admin_panel():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') != 'administrator':
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    flag = get_flag()
    return render_template('admin.html', flag=flag)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Internal server error'), 500


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('/app/data', exist_ok=True)
    app.run(debug=False, host='0.0.0.0', port=80)

