import os
from functools import wraps
from flask import Flask, request, redirect, url_for, render_template_string, session, make_response

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration loaded from config.yaml
CONFIG = {
    "accessControl": {
        "autologinLocal": True,
        "autologinAs": "admin"
    },
    "server": {
        "reverseProxy": {
            "trustedProxies": []
        }
    }
}

# User database
USERS = {
    "admin": {
        "password": "octoprintadmin2024!",
        "role": "admin",
        "apikey": "A7F2D91BC4E85063"
    },
    "operator": {
        "password": "operator123",
        "role": "user",
        "apikey": "B8G3E02CD5F96174"
    }
}

def get_system_key():
    """Read system configuration key"""
    try:
        with open('/app/data/flag.txt', 'r') as f:
            return f.read().strip()
    except:
        return "NOT_CONFIGURED"

def get_remote_address(req):
    """Determine the client's IP address from request headers."""
    forwarded_for = req.headers.get('X-Forwarded-For')
    if forwarded_for:
        client_ip = forwarded_for.split(',')[0].strip()
        return client_ip
    return req.remote_addr

def is_local_request(req):
    """Check if request originates from local network"""
    remote_addr = get_remote_address(req)
    local_addresses = ['127.0.0.1', '::1', 'localhost']
    return remote_addr in local_addresses

def check_autologin(req):
    """Check if request qualifies for automatic local login."""
    if CONFIG["accessControl"]["autologinLocal"]:
        if is_local_request(req):
            return CONFIG["accessControl"]["autologinAs"]
    return None

def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for auto-login first
        autologin_user = check_autologin(request)
        if autologin_user:
            session['user'] = autologin_user
            session['role'] = USERS[autologin_user]['role']
        
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for auto-login first
        autologin_user = check_autologin(request)
        if autologin_user:
            session['user'] = autologin_user
            session['role'] = USERS[autologin_user]['role']
        
        if 'user' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return render_template_string(ERROR_PAGE, error="Access denied. Admin privileges required."), 403
        return f(*args, **kwargs)
    return decorated_function

# Templates
BASE_STYLE = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; }
    .navbar { background: #16213e; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.3); }
    .navbar h1 { color: #00d4ff; font-size: 1.5rem; }
    .navbar a { color: #aaa; text-decoration: none; margin-left: 1.5rem; }
    .navbar a:hover { color: #00d4ff; }
    .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
    .card { background: #16213e; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
    .card h2 { color: #00d4ff; margin-bottom: 1rem; font-size: 1.2rem; }
    .btn { background: #00d4ff; color: #1a1a2e; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; font-size: 1rem; text-decoration: none; display: inline-block; }
    .btn:hover { background: #00b8e6; }
    .btn-danger { background: #ff4757; color: white; }
    .btn-danger:hover { background: #ff3344; }
    input[type="text"], input[type="password"] { width: 100%; padding: 0.75rem; margin: 0.5rem 0; border: 1px solid #333; border-radius: 4px; background: #0f0f23; color: #eee; font-size: 1rem; }
    .form-group { margin-bottom: 1rem; }
    label { display: block; margin-bottom: 0.5rem; color: #aaa; }
    .alert { padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
    .alert-error { background: #ff475733; border: 1px solid #ff4757; }
    .alert-success { background: #2ed57333; border: 1px solid #2ed573; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #333; }
    th { color: #00d4ff; }
    .status-online { color: #2ed573; }
    .status-offline { color: #ff4757; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
    .temp-display { font-size: 2rem; font-weight: bold; color: #00d4ff; }
    .progress { background: #333; border-radius: 4px; height: 8px; overflow: hidden; }
    .progress-bar { background: #00d4ff; height: 100%; transition: width 0.3s; }
    .footer { text-align: center; padding: 2rem; color: #666; font-size: 0.9rem; }
</style>
"""

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>OctoPrint - Login</title>
    """ + BASE_STYLE + """
</head>
<body>
    <nav class="navbar">
        <h1>🐙 OctoPrint</h1>
    </nav>
    <div class="container">
        <div style="max-width: 400px; margin: 4rem auto;">
            <div class="card">
                <h2>Sign In</h2>
                {% if error %}
                <div class="alert alert-error">{{ error }}</div>
                {% endif %}
                <form method="POST">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn" style="width: 100%;">Login</button>
                </form>
            </div>
            <p style="text-align: center; color: #666; margin-top: 1rem;">OctoPrint 1.10.0</p>
        </div>
    </div>
</body>
</html>
"""

INDEX_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>OctoPrint</title>
    """ + BASE_STYLE + """
</head>
<body>
    <nav class="navbar">
        <h1>🐙 OctoPrint</h1>
        <div>
            <a href="/">Dashboard</a>
            <a href="/files">Files</a>
            <a href="/terminal">Terminal</a>
            {% if role == 'admin' %}<a href="/settings">Settings</a>{% endif %}
            <a href="/logout">Logout ({{ user }})</a>
        </div>
    </nav>
    <div class="container">
        <div class="grid">
            <div class="card">
                <h2>🌡️ Temperatures</h2>
                <div style="display: flex; justify-content: space-around; margin: 1rem 0;">
                    <div style="text-align: center;">
                        <div class="temp-display">215°C</div>
                        <div style="color: #aaa;">Hotend</div>
                    </div>
                    <div style="text-align: center;">
                        <div class="temp-display">60°C</div>
                        <div style="color: #aaa;">Bed</div>
                    </div>
                </div>
            </div>
            <div class="card">
                <h2>📊 Print Status</h2>
                <p style="margin-bottom: 1rem;"><span class="status-offline">●</span> No print job active</p>
                <div class="progress">
                    <div class="progress-bar" style="width: 0%;"></div>
                </div>
                <p style="color: #aaa; margin-top: 0.5rem;">Progress: 0%</p>
            </div>
            <div class="card">
                <h2>🖨️ Printer State</h2>
                <table>
                    <tr><td>State</td><td><span class="status-online">Operational</span></td></tr>
                    <tr><td>File</td><td>-</td></tr>
                    <tr><td>Estimated</td><td>-</td></tr>
                    <tr><td>Print Time</td><td>-</td></tr>
                </table>
            </div>
            <div class="card">
                <h2>📡 Connection</h2>
                <table>
                    <tr><td>Port</td><td>/dev/ttyUSB0</td></tr>
                    <tr><td>Baudrate</td><td>115200</td></tr>
                    <tr><td>Printer Profile</td><td>Default</td></tr>
                </table>
                <button class="btn" style="margin-top: 1rem;">Connect</button>
            </div>
        </div>
    </div>
    <div class="footer">
        OctoPrint 1.10.0 &copy; 2024
    </div>
</body>
</html>
"""

FILES_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>OctoPrint - Files</title>
    """ + BASE_STYLE + """
</head>
<body>
    <nav class="navbar">
        <h1>🐙 OctoPrint</h1>
        <div>
            <a href="/">Dashboard</a>
            <a href="/files">Files</a>
            <a href="/terminal">Terminal</a>
            {% if role == 'admin' %}<a href="/settings">Settings</a>{% endif %}
            <a href="/logout">Logout ({{ user }})</a>
        </div>
    </nav>
    <div class="container">
        <div class="card">
            <h2>📁 Files</h2>
            <table>
                <thead>
                    <tr><th>Name</th><th>Size</th><th>Uploaded</th><th>Actions</th></tr>
                </thead>
                <tbody>
                    <tr><td>benchy.gcode</td><td>2.4 MB</td><td>2024-01-15</td><td><button class="btn">Print</button></td></tr>
                    <tr><td>calibration_cube.gcode</td><td>1.1 MB</td><td>2024-01-14</td><td><button class="btn">Print</button></td></tr>
                    <tr><td>phone_stand.gcode</td><td>3.8 MB</td><td>2024-01-12</td><td><button class="btn">Print</button></td></tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

TERMINAL_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>OctoPrint - Terminal</title>
    """ + BASE_STYLE + """
</head>
<body>
    <nav class="navbar">
        <h1>🐙 OctoPrint</h1>
        <div>
            <a href="/">Dashboard</a>
            <a href="/files">Files</a>
            <a href="/terminal">Terminal</a>
            {% if role == 'admin' %}<a href="/settings">Settings</a>{% endif %}
            <a href="/logout">Logout ({{ user }})</a>
        </div>
    </nav>
    <div class="container">
        <div class="card">
            <h2>💻 Terminal</h2>
            <div style="background: #0f0f23; padding: 1rem; border-radius: 4px; font-family: monospace; height: 300px; overflow-y: auto;">
                <div style="color: #00d4ff;">Recv: ok</div>
                <div style="color: #aaa;">Send: M105</div>
                <div style="color: #00d4ff;">Recv: ok T:215.0 /215.0 B:60.0 /60.0</div>
                <div style="color: #aaa;">Send: M114</div>
                <div style="color: #00d4ff;">Recv: ok X:0.00 Y:0.00 Z:0.00 E:0.00</div>
            </div>
            <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                <input type="text" placeholder="Enter G-code command..." style="flex: 1;">
                <button class="btn">Send</button>
            </div>
        </div>
    </div>
</body>
</html>
"""

SETTINGS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>OctoPrint - Settings</title>
    """ + BASE_STYLE + """
</head>
<body>
    <nav class="navbar">
        <h1>🐙 OctoPrint</h1>
        <div>
            <a href="/">Dashboard</a>
            <a href="/files">Files</a>
            <a href="/terminal">Terminal</a>
            <a href="/settings">Settings</a>
            <a href="/logout">Logout ({{ user }})</a>
        </div>
    </nav>
    <div class="container">
        <div class="grid">
            <div class="card">
                <h2>⚙️ General Settings</h2>
                <div class="form-group">
                    <label>Instance Name</label>
                    <input type="text" value="OctoPrint">
                </div>
                <div class="form-group">
                    <label>Default Language</label>
                    <input type="text" value="English">
                </div>
            </div>
            <div class="card">
                <h2>🔐 Access Control</h2>
                <table>
                    <tr><td>Auto-login (local)</td><td><span class="status-online">Enabled</span></td></tr>
                    <tr><td>Auto-login user</td><td>admin</td></tr>
                    <tr><td>Guest access</td><td><span class="status-offline">Disabled</span></td></tr>
                </table>
            </div>
            <div class="card">
                <h2>🔑 API Keys</h2>
                <p style="margin-bottom: 1rem;">Your API key provides full access to this OctoPrint instance.</p>
                <div style="background: #0f0f23; padding: 0.75rem; border-radius: 4px; font-family: monospace; word-break: break-all;">
                    {{ apikey }}
                </div>
            </div>
            <div class="card">
                <h2>🏆 System Information</h2>
                <table>
                    <tr><td>Version</td><td>1.10.0</td></tr>
                    <tr><td>Python</td><td>3.9.7</td></tr>
                    <tr><td>License Key</td><td style="font-family: monospace; color: #2ed573;">{{ license_key }}</td></tr>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

ERROR_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>OctoPrint - Error</title>
    """ + BASE_STYLE + """
</head>
<body>
    <nav class="navbar">
        <h1>🐙 OctoPrint</h1>
    </nav>
    <div class="container">
        <div class="card" style="max-width: 500px; margin: 4rem auto; text-align: center;">
            <h2 style="color: #ff4757;">Error</h2>
            <p>{{ error }}</p>
            <a href="/" class="btn" style="margin-top: 1rem;">Go Back</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
@login_required
def index():
    return render_template_string(INDEX_PAGE, 
                                  user=session.get('user'), 
                                  role=session.get('role'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['role'] = USERS[username]['role']
            return redirect(url_for('index'))
        
        return render_template_string(LOGIN_PAGE, error="Invalid username or password")
    
    # Check for auto-login on GET request
    autologin_user = check_autologin(request)
    if autologin_user:
        session['user'] = autologin_user
        session['role'] = USERS[autologin_user]['role']
        return redirect(url_for('index'))
    
    return render_template_string(LOGIN_PAGE, error=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/files')
@login_required
def files():
    return render_template_string(FILES_PAGE, 
                                  user=session.get('user'), 
                                  role=session.get('role'))

@app.route('/terminal')
@login_required
def terminal():
    return render_template_string(TERMINAL_PAGE, 
                                  user=session.get('user'), 
                                  role=session.get('role'))

@app.route('/settings')
@admin_required
def settings():
    user = session.get('user')
    apikey = USERS.get(user, {}).get('apikey', 'N/A')
    license_key = get_system_key()
    return render_template_string(SETTINGS_PAGE, 
                                  user=user, 
                                  role=session.get('role'),
                                  apikey=apikey,
                                  license_key=license_key)

@app.route('/api/version')
def api_version():
    return {"server": "1.10.0", "api": "0.1", "text": "OctoPrint 1.10.0"}

@app.route('/api/settings')
@admin_required
def api_settings():
    user = session.get('user')
    return {
        "api": {"key": USERS.get(user, {}).get('apikey', '')},
        "accessControl": CONFIG["accessControl"],
        "server": {"version": "1.10.0"}
    }

@app.errorhandler(404)
def not_found(e):
    return render_template_string(ERROR_PAGE, error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template_string(ERROR_PAGE, error="Internal server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
