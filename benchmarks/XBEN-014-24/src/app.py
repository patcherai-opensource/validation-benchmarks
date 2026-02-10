"""
D-Tale-like Data Visualization Application
Vulnerable to CVE-2024-3408:
- Hardcoded SECRET_KEY enables session forgery
- /update-settings endpoint allows code execution via query injection
"""

import os
import json
from flask import Flask, request, session, jsonify, render_template_string, redirect, url_for
import pandas as pd

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded SECRET_KEY (CVE-2024-3408)
# This allows attackers to forge session cookies
app.config["SECRET_KEY"] = "Dtale"

# Read flag from file (injected at build time)
FLAG_FILE = "/app/flag.txt"

# Simulated authentication state
AUTH_CONFIG = {
    "active": True,  # Authentication is enabled
    "users": {
        "admin": "D7al3_Adm1n_P@ss!"
    }
}

# Global state to store data settings (simulating D-Tale's global_state)
class GlobalState:
    def __init__(self):
        self.settings = {}
        self.flags = {}
        # Sample dataset (simulating D-Tale's data)
        self.data = {
            "1": pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
                "value": [100, 200, 150, 300, 250]
            })
        }
    
    def load_flag(self, data_id, flag_name, default=False):
        """Load a feature flag for a data_id"""
        if data_id not in self.flags:
            return default
        return self.flags.get(data_id, {}).get(flag_name, default)
    
    def update_settings(self, data_id, settings):
        """Update settings for a data_id"""
        if data_id not in self.settings:
            self.settings[data_id] = {}
        self.settings[data_id].update(settings)
    
    def get_settings(self, data_id):
        """Get settings for a data_id"""
        return self.settings.get(data_id, {})
    
    def get_data(self, data_id):
        """Get DataFrame for a data_id"""
        return self.data.get(data_id)

global_state = GlobalState()

def is_authenticated():
    """Check if user is authenticated"""
    if not AUTH_CONFIG["active"]:
        return True
    return session.get("logged_in", False)

def get_json_arg(request, key, default=None):
    """Get JSON argument from request"""
    try:
        value = request.args.get(key)
        if value:
            return json.loads(value)
        return default
    except:
        return default

# HTML Templates
LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>D-Tale Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #666; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #0056b3; }
        .error { color: red; margin-bottom: 15px; text-align: center; }
        .info { color: #666; font-size: 12px; text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>D-Tale Data Explorer</h1>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST" action="/login">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
        <div class="info">Version 3.10.0 - Secure Data Visualization</div>
    </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>D-Tale Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background-color: #f5f5f5; }
        .header { background-color: #333; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; }
        .header a { color: white; text-decoration: none; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .card h2 { margin-top: 0; color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
        .api-section { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 15px; }
        .api-section code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
        .welcome { color: green; }
    </style>
</head>
<body>
    <div class="header">
        <h1>D-Tale Dashboard</h1>
        <div>
            <span class="welcome">Welcome, {{ username }}!</span>
            <a href="/logout" style="margin-left: 20px;">Logout</a>
        </div>
    </div>
    <div class="container">
        <div class="card">
            <h2>Dataset Overview (data_id: 1)</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Value</th>
                </tr>
                {% for row in data %}
                <tr>
                    <td>{{ row.id }}</td>
                    <td>{{ row.name }}</td>
                    <td>{{ row.value }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <div class="card">
            <h2>API Endpoints</h2>
            <div class="api-section">
                <p><strong>View Data:</strong> <code>GET /dtale/data/1</code></p>
                <p><strong>Update Settings:</strong> <code>GET /dtale/update-settings/1?settings={"key":"value"}</code></p>
                <p><strong>Get Settings:</strong> <code>GET /dtale/settings/1</code></p>
                <p><strong>Custom Filter:</strong> <code>GET /dtale/filter/1</code> - Applies custom query filter to data</p>
            </div>
        </div>
        <div class="card">
            <h2>Current Settings</h2>
            <pre>{{ settings | tojson(indent=2) }}</pre>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Root endpoint - redirect to login or dashboard"""
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login endpoint"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username in AUTH_CONFIG["users"] and AUTH_CONFIG["users"][username] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid credentials"
    
    return render_template_string(LOGIN_PAGE, error=error)

@app.route('/logout')
def logout():
    """Logout endpoint"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard - requires authentication"""
    if not is_authenticated():
        return redirect(url_for('login'))
    
    username = session.get('username', 'User')
    df = global_state.get_data("1")
    data = df.to_dict('records') if df is not None else []
    settings = global_state.get_settings("1")
    
    return render_template_string(DASHBOARD_PAGE, username=username, data=data, settings=settings)

@app.route('/dtale/data/<data_id>')
def get_data(data_id):
    """Get data for a specific data_id - requires authentication"""
    if not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401
    
    df = global_state.get_data(data_id)
    if df is None:
        return jsonify({"error": "Data not found"}), 404
    
    return jsonify({"data": df.to_dict('records')})

@app.route('/dtale/settings/<data_id>')
def get_settings(data_id):
    """Get settings for a specific data_id - requires authentication"""
    if not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401
    
    settings = global_state.get_settings(data_id)
    return jsonify({"settings": settings})

@app.route('/dtale/update-settings/<data_id>')
def update_settings(data_id):
    """
    VULNERABILITY 2: Code execution via query injection (CVE-2024-3408)
    
    The server tries to defensively remove 'query' from settings if 
    enable_custom_filters is disabled. However, this defense can be bypassed
    because the pop() only removes the top-level 'query' key - nested payloads
    or alternative key names can still inject malicious content.
    
    Additionally, even when popped, if an attacker supplies settings that
    include a 'query' key with evaluation capability, it can lead to RCE
    when the filter is applied.
    """
    if not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401
    
    updated_settings = get_json_arg(request, "settings", {})
    
    # Vulnerable defense - only removes top-level 'query' key
    # An attacker can bypass this by using 'custom_query' or nested payloads
    if not global_state.load_flag(data_id, "enable_custom_filters", False):
        # This is the vulnerable pattern from D-Tale
        # It only removes 'query' but not other variations
        updated_settings.pop('query', None)
    
    global_state.update_settings(data_id, updated_settings)
    return jsonify({"success": True})

@app.route('/dtale/filter/<data_id>')
def apply_filter(data_id):
    """
    Apply filter to data - this is where query gets executed
    The query from settings is evaluated, enabling code execution
    
    This simulates D-Tale's behavior where the query setting is processed
    through pandas DataFrame.query() which uses eval() internally.
    """
    if not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401
    
    df = global_state.get_data(data_id)
    if df is None:
        return jsonify({"error": "Data not found"}), 404
    
    settings = global_state.get_settings(data_id)
    
    # Check for query in various forms (bypass defense from update-settings)
    query = settings.get('query') or settings.get('custom_query') or settings.get('filter_query')
    
    if query:
        try:
            # VULNERABILITY: Direct evaluation of user-controlled query
            # This simulates the pandas.DataFrame.query() vulnerability
            # which can execute arbitrary Python code
            result = eval(query)
            
            # If it's a dataframe operation, return the result
            if isinstance(result, pd.DataFrame):
                return jsonify({"data": result.to_dict('records')})
            else:
                # For other results (like executing system commands)
                return jsonify({"result": str(result)})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    return jsonify({"data": df.to_dict('records')})

@app.route('/dtale/flag')
def get_flag():
    """
    Admin-only endpoint to view the flag
    Only accessible after proper authentication
    The flag is stored in a file and read on demand
    """
    if not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401
    
    username = session.get('username', '')
    if username != 'admin':
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        with open(FLAG_FILE, 'r') as f:
            flag = f.read().strip()
        return jsonify({"flag": flag})
    except:
        return jsonify({"error": "Flag file not found"}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
