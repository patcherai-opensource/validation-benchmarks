import os
import secrets
import hashlib
from functools import wraps
from flask import Flask, request, render_template_string, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

USERS = {
    'admin': {
        'password_hash': hashlib.sha256('craftadmin2024'.encode()).hexdigest(),
        'role': 'admin'
    }
}

# Configuration
ALLOW_ADMIN_CHANGES = True

# Base paths for the CMS
BASE_PATH = '/var/www/craft'
ASSETS_BASE = os.path.join(BASE_PATH, 'web/assets')
TEMPLATES_PATH = os.path.join(BASE_PATH, 'templates')

asset_volumes = {}

SYSTEM_DIRS = [
    '/var/www/craft/config',
    '/var/www/craft/storage',
    '/var/www/craft/vendor',
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def absolute_path(path, from_path=None):
    """
    Convert a relative path to an absolute path.
    """
    if os.path.isabs(path):
        return path
    
    if from_path is None:
        from_path = ASSETS_BASE
    
    return from_path + '/' + path

def is_system_dir(path):
    """
    Check if a path is a protected system directory.
    """
    for sys_dir in SYSTEM_DIRS:
        if path.startswith(sys_dir):
            return True
    return False

def validate_path(path):
    """
    Validate that the path is safe to use.
    """
    if is_system_dir(path):
        return False
    return True

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Craft CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        h1 { color: #e5422b; margin-bottom: 10px; font-size: 28px; }
        .subtitle { color: #666; margin-bottom: 30px; }
        .btn { display: inline-block; background: #e5422b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: 500; }
        .btn:hover { background: #c73724; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Craft CMS</h1>
        <p class="subtitle">Content Management System</p>
        <a href="/admin" class="btn">Admin Login</a>
    </div>
</body>
</html>
''')

@app.route('/admin')
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username in USERS:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if USERS[username]['password_hash'] == password_hash:
                session['user'] = username
                session['role'] = USERS[username]['role']
                return redirect(url_for('dashboard'))
        
        error = 'Invalid credentials'
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Craft CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        h1 { color: #e5422b; margin-bottom: 30px; text-align: center; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        input:focus { outline: none; border-color: #e5422b; }
        .btn { width: 100%; background: #e5422b; color: white; padding: 14px; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; font-weight: 500; }
        .btn:hover { background: #c73724; }
        .error { background: #fee; color: #c00; padding: 10px; border-radius: 4px; margin-bottom: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Craft CMS</h1>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Sign in</button>
        </form>
    </div>
</body>
</html>
''', error=error)

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def dashboard():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Craft CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #e5422b; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 20px; }
        .nav a { color: white; text-decoration: none; margin-left: 20px; }
        .nav a:hover { text-decoration: underline; }
        .main { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #2d3748; padding: 20px 0; }
        .sidebar a { display: block; color: #a0aec0; padding: 12px 25px; text-decoration: none; }
        .sidebar a:hover, .sidebar a.active { background: #4a5568; color: white; }
        .content { flex: 1; padding: 30px; }
        .card { background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card h2 { color: #2d3748; margin-bottom: 15px; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .stat-value { font-size: 32px; font-weight: bold; color: #e5422b; }
        .stat-label { color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Craft CMS</h1>
        <div class="nav">
            <span>Welcome, {{ session.user }}</span>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <a href="{{ url_for('dashboard') }}" class="active">Dashboard</a>
            <a href="{{ url_for('entries') }}">Entries</a>
            <a href="{{ url_for('assets') }}">Assets</a>
            <a href="{{ url_for('settings') }}">Settings</a>
        </div>
        <div class="content">
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">12</div>
                    <div class="stat-label">Entries</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ asset_volumes|length }}</div>
                    <div class="stat-label">Asset Volumes</div>
                </div>
                <div class="stat">
                    <div class="stat-value">3</div>
                    <div class="stat-label">Users</div>
                </div>
            </div>
            <div class="card">
                <h2>Recent Activity</h2>
                <p>No recent activity to display.</p>
            </div>
        </div>
    </div>
</body>
</html>
''', asset_volumes=asset_volumes)

@app.route('/admin/entries')
@login_required
def entries():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entries - Craft CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #e5422b; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 20px; }
        .nav a { color: white; text-decoration: none; margin-left: 20px; }
        .main { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #2d3748; padding: 20px 0; }
        .sidebar a { display: block; color: #a0aec0; padding: 12px 25px; text-decoration: none; }
        .sidebar a:hover, .sidebar a.active { background: #4a5568; color: white; }
        .content { flex: 1; padding: 30px; }
        .card { background: white; border-radius: 8px; padding: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Craft CMS</h1>
        <div class="nav">
            <span>Welcome, {{ session.user }}</span>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('entries') }}" class="active">Entries</a>
            <a href="{{ url_for('assets') }}">Assets</a>
            <a href="{{ url_for('settings') }}">Settings</a>
        </div>
        <div class="content">
            <div class="card">
                <h2 style="margin-bottom: 20px;">Entries</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Section</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Welcome to Craft CMS</td>
                            <td>Blog</td>
                            <td>Published</td>
                            <td>2024-01-15</td>
                        </tr>
                        <tr>
                            <td>Getting Started Guide</td>
                            <td>Documentation</td>
                            <td>Published</td>
                            <td>2024-01-10</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
''')

@app.route('/admin/assets')
@login_required
def assets():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assets - Craft CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #e5422b; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 20px; }
        .nav a { color: white; text-decoration: none; margin-left: 20px; }
        .main { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #2d3748; padding: 20px 0; }
        .sidebar a { display: block; color: #a0aec0; padding: 12px 25px; text-decoration: none; }
        .sidebar a:hover, .sidebar a.active { background: #4a5568; color: white; }
        .content { flex: 1; padding: 30px; }
        .card { background: white; border-radius: 8px; padding: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .btn { display: inline-block; background: #e5422b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-bottom: 20px; }
        .volume-list { list-style: none; }
        .volume-list li { padding: 15px; border: 1px solid #eee; margin-bottom: 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }
        .volume-name { font-weight: 500; }
        .volume-path { color: #666; font-size: 14px; }
        .upload-btn { background: #4a5568; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Craft CMS</h1>
        <div class="nav">
            <span>Welcome, {{ session.user }}</span>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('entries') }}">Entries</a>
            <a href="{{ url_for('assets') }}" class="active">Assets</a>
            <a href="{{ url_for('settings') }}">Settings</a>
        </div>
        <div class="content">
            <div class="card">
                <h2 style="margin-bottom: 20px;">Asset Volumes</h2>
                <a href="{{ url_for('settings_filesystems') }}" class="btn">Manage Filesystems</a>
                <ul class="volume-list">
                    {% for name, vol in asset_volumes.items() %}
                    <li>
                        <div>
                            <div class="volume-name">{{ name }}</div>
                            <div class="volume-path">{{ vol.path }}</div>
                        </div>
                        <a href="{{ url_for('upload_asset', volume=name) }}" class="upload-btn">Upload</a>
                    </li>
                    {% else %}
                    <li>No asset volumes configured. <a href="{{ url_for('settings_filesystems') }}">Create one</a>.</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
''', asset_volumes=asset_volumes)

@app.route('/admin/settings')
@admin_required
def settings():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings - Craft CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #e5422b; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 20px; }
        .nav a { color: white; text-decoration: none; margin-left: 20px; }
        .main { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #2d3748; padding: 20px 0; }
        .sidebar a { display: block; color: #a0aec0; padding: 12px 25px; text-decoration: none; }
        .sidebar a:hover, .sidebar a.active { background: #4a5568; color: white; }
        .content { flex: 1; padding: 30px; }
        .card { background: white; border-radius: 8px; padding: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .settings-list a { display: block; padding: 15px; border: 1px solid #eee; margin-bottom: 10px; border-radius: 4px; text-decoration: none; color: #333; }
        .settings-list a:hover { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Craft CMS</h1>
        <div class="nav">
            <span>Welcome, {{ session.user }}</span>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('entries') }}">Entries</a>
            <a href="{{ url_for('assets') }}">Assets</a>
            <a href="{{ url_for('settings') }}" class="active">Settings</a>
        </div>
        <div class="content">
            <div class="card">
                <h2 style="margin-bottom: 20px;">Settings</h2>
                <div class="settings-list">
                    <a href="{{ url_for('settings_general') }}">General</a>
                    <a href="{{ url_for('settings_filesystems') }}">Filesystems</a>
                    <a href="{{ url_for('settings_users') }}">Users</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
''')

@app.route('/admin/settings/general')
@admin_required
def settings_general():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>General Settings - Craft CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #e5422b; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 20px; }
        .nav a { color: white; text-decoration: none; margin-left: 20px; }
        .main { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #2d3748; padding: 20px 0; }
        .sidebar a { display: block; color: #a0aec0; padding: 12px 25px; text-decoration: none; }
        .sidebar a:hover, .sidebar a.active { background: #4a5568; color: white; }
        .content { flex: 1; padding: 30px; }
        .card { background: white; border-radius: 8px; padding: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; }
        input[type="text"] { width: 100%; max-width: 400px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .info { background: #e8f4fd; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1a73e8; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Craft CMS</h1>
        <div class="nav">
            <span>Welcome, {{ session.user }}</span>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('entries') }}">Entries</a>
            <a href="{{ url_for('assets') }}">Assets</a>
            <a href="{{ url_for('settings') }}" class="active">Settings</a>
        </div>
        <div class="content">
            <div class="card">
                <h2 style="margin-bottom: 20px;">General Settings</h2>
                <div class="info">ALLOW_ADMIN_CHANGES is enabled.</div>
                <div class="form-group">
                    <label>Site Name</label>
                    <input type="text" value="Craft CMS" readonly>
                </div>
                <div class="form-group">
                    <label>System Email</label>
                    <input type="text" value="admin@example.com" readonly>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
''')

@app.route('/admin/settings/filesystems', methods=['GET', 'POST'])
@admin_required
def settings_filesystems():
    message = None
    error = None
    
    if not ALLOW_ADMIN_CHANGES:
        error = 'Admin changes are disabled'
    elif request.method == 'POST':
        name = request.form.get('name', '').strip()
        path = request.form.get('path', '').strip()
        
        if not name or not path:
            error = 'Name and path are required'
        elif name in asset_volumes:
            error = 'Volume with this name already exists'
        else:
            # Convert the relative path to absolute using the vulnerable function
            abs_path = absolute_path(path)
            
            # Validate the path (vulnerable check - uses non-normalized path)
            if not validate_path(abs_path):
                error = 'Invalid path: access to system directories is not allowed'
            else:
                # Create the directory if it doesn't exist
                try:
                    real_path = os.path.realpath(abs_path)
                    os.makedirs(real_path, exist_ok=True)
                    asset_volumes[name] = {
                        'path': abs_path,
                        'real_path': real_path
                    }
                    message = f'Filesystem "{name}" created successfully'
                except Exception as e:
                    error = 'Failed to create filesystem'
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Filesystems - Craft CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #e5422b; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 20px; }
        .nav a { color: white; text-decoration: none; margin-left: 20px; }
        .main { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #2d3748; padding: 20px 0; }
        .sidebar a { display: block; color: #a0aec0; padding: 12px 25px; text-decoration: none; }
        .sidebar a:hover, .sidebar a.active { background: #4a5568; color: white; }
        .content { flex: 1; padding: 30px; }
        .card { background: white; border-radius: 8px; padding: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; }
        input[type="text"] { width: 100%; max-width: 400px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { background: #e5422b; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #c73724; }
        .message { padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .volume-list { list-style: none; }
        .volume-list li { padding: 15px; border: 1px solid #eee; margin-bottom: 10px; border-radius: 4px; }
        .volume-name { font-weight: 500; }
        .volume-path { color: #666; font-size: 14px; }
        .help-text { font-size: 12px; color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Craft CMS</h1>
        <div class="nav">
            <span>Welcome, {{ session.user }}</span>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('entries') }}">Entries</a>
            <a href="{{ url_for('assets') }}">Assets</a>
            <a href="{{ url_for('settings') }}" class="active">Settings</a>
        </div>
        <div class="content">
            <div class="card">
                <h2 style="margin-bottom: 20px;">Create New Filesystem</h2>
                {% if message %}
                <div class="message success">{{ message }}</div>
                {% endif %}
                {% if error %}
                <div class="message error">{{ error }}</div>
                {% endif %}
                <form method="POST">
                    <div class="form-group">
                        <label for="name">Handle</label>
                        <input type="text" id="name" name="name" placeholder="my-assets">
                        <div class="help-text">The unique identifier for this filesystem</div>
                    </div>
                    <div class="form-group">
                        <label for="path">Base Path</label>
                        <input type="text" id="path" name="path" placeholder="uploads">
                        <div class="help-text">The path relative to the assets directory</div>
                    </div>
                    <button type="submit" class="btn">Create Filesystem</button>
                </form>
            </div>
            
            <div class="card">
                <h2 style="margin-bottom: 20px;">Existing Filesystems</h2>
                <ul class="volume-list">
                    {% for name, vol in asset_volumes.items() %}
                    <li>
                        <div class="volume-name">{{ name }}</div>
                        <div class="volume-path">{{ vol.path }}</div>
                    </li>
                    {% else %}
                    <li>No filesystems configured.</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
''', message=message, error=error, asset_volumes=asset_volumes)

@app.route('/admin/settings/users')
@admin_required
def settings_users():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Users - Craft CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #e5422b; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 20px; }
        .nav a { color: white; text-decoration: none; margin-left: 20px; }
        .main { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #2d3748; padding: 20px 0; }
        .sidebar a { display: block; color: #a0aec0; padding: 12px 25px; text-decoration: none; }
        .sidebar a:hover, .sidebar a.active { background: #4a5568; color: white; }
        .content { flex: 1; padding: 30px; }
        .card { background: white; border-radius: 8px; padding: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Craft CMS</h1>
        <div class="nav">
            <span>Welcome, {{ session.user }}</span>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('entries') }}">Entries</a>
            <a href="{{ url_for('assets') }}">Assets</a>
            <a href="{{ url_for('settings') }}" class="active">Settings</a>
        </div>
        <div class="content">
            <div class="card">
                <h2 style="margin-bottom: 20px;">Users</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Role</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>admin</td>
                            <td>Admin</td>
                            <td>Active</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
''')

@app.route('/admin/assets/<volume>/upload', methods=['GET', 'POST'])
@login_required
def upload_asset(volume):
    if volume not in asset_volumes:
        abort(404)
    
    message = None
    error = None
    vol = asset_volumes[volume]
    
    if request.method == 'POST':
        if 'file' not in request.files:
            error = 'No file provided'
        else:
            file = request.files['file']
            if file.filename == '':
                error = 'No file selected'
            else:
                filename = file.filename
                filename = os.path.basename(filename)
                
                try:
                    filepath = os.path.join(vol['real_path'], filename)
                    file.save(filepath)
                    message = f'File "{filename}" uploaded successfully'
                except Exception as e:
                    error = 'Failed to upload file'
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Asset - Craft CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #e5422b; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 20px; }
        .nav a { color: white; text-decoration: none; margin-left: 20px; }
        .main { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #2d3748; padding: 20px 0; }
        .sidebar a { display: block; color: #a0aec0; padding: 12px 25px; text-decoration: none; }
        .sidebar a:hover, .sidebar a.active { background: #4a5568; color: white; }
        .content { flex: 1; padding: 30px; }
        .card { background: white; border-radius: 8px; padding: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; }
        input[type="file"] { padding: 10px; border: 1px solid #ddd; border-radius: 4px; width: 100%; max-width: 400px; }
        .btn { background: #e5422b; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #c73724; }
        .message { padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #e5422b; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Craft CMS</h1>
        <div class="nav">
            <span>Welcome, {{ session.user }}</span>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('entries') }}">Entries</a>
            <a href="{{ url_for('assets') }}" class="active">Assets</a>
            <a href="{{ url_for('settings') }}">Settings</a>
        </div>
        <div class="content">
            <div class="card">
                <a href="{{ url_for('assets') }}" class="back-link">&larr; Back to Assets</a>
                <h2 style="margin-bottom: 20px;">Upload to {{ volume }}</h2>
                {% if message %}
                <div class="message success">{{ message }}</div>
                {% endif %}
                {% if error %}
                <div class="message error">{{ error }}</div>
                {% endif %}
                <form method="POST" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="file">Select File</label>
                        <input type="file" id="file" name="file">
                    </div>
                    <button type="submit" class="btn">Upload</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
''', volume=volume, message=message, error=error)

@app.route('/render/<path:template_name>')
def render_custom_template(template_name):
    """
    Render a template from the templates directory.
    """
    if '..' in template_name or template_name.startswith('/'):
        abort(404)
    
    template_path = os.path.join(TEMPLATES_PATH, template_name)
    
    if not os.path.isfile(template_path):
        abort(404)
    
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        return render_template_string(template_content)
    except Exception:
        abort(500)

@app.errorhandler(403)
def forbidden(e):
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>403 Forbidden</title></head>
<body><h1>403 Forbidden</h1><p>You do not have permission to access this resource.</p></body>
</html>
'''), 403

@app.errorhandler(404)
def not_found(e):
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>404 Not Found</title></head>
<body><h1>404 Not Found</h1><p>The requested resource was not found.</p></body>
</html>
'''), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>500 Internal Server Error</title></head>
<body><h1>500 Internal Server Error</h1><p>An unexpected error occurred.</p></body>
</html>
'''), 500

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(ASSETS_BASE, exist_ok=True)
    os.makedirs(TEMPLATES_PATH, exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000)
