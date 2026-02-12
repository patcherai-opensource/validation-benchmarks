import os
import hmac
import hashlib
import time
import json
import secrets
from flask import Flask, request, make_response, redirect, url_for, render_template_string, g
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32).hex()

# Server signing secret - generated once at startup
SIGNING_SECRET = os.urandom(32)

# Read flag from file planted at build time
def _read_flag():
    try:
        with open('/etc/hive/server.flag', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return 'FLAG{placeholder}'

# In-memory session store (simulating HiveServer2 session management)
_sessions = {}

# Default admin credentials (simulating Hive configuration)
HIVE_USERS = {
    'admin': {
        'password': secrets.token_hex(32),
        'role': 'admin',
        'display_name': 'HiveServer Administrator'
    },
    'hive': {
        'password': secrets.token_hex(32),
        'role': 'service',
        'display_name': 'Hive Service Account'
    }
}


def compute_signature(value):
    """Compute HMAC-SHA256 signature for a cookie value."""
    return hmac.new(SIGNING_SECRET, value.encode('utf-8'), hashlib.sha256).hexdigest()


def sign_cookie(value):
    """Sign a cookie value by appending the signature."""
    signature = compute_signature(value)
    return value + '&s=' + signature


def verify_and_extract(signed_str):
    """
    Verify the signature of a signed cookie string and extract the value.
    Mirrors org.apache.hive.service.CookieSigner.verifyAndExtract behavior.
    """
    if not signed_str or '&s=' not in signed_str:
        raise ValueError("Invalid cookie format: missing signature")

    idx = signed_str.rfind('&s=')
    value = signed_str[:idx]
    original_signature = signed_str[idx + 3:]

    current_signature = compute_signature(value)

    if not hmac.compare_digest(original_signature, current_signature):
        # CVE-2024-23945: Leaking the correct signature in the error message
        raise ValueError(
            "Invalid sign, original = " + original_signature
            + " current = " + current_signature
        )

    return value


def parse_cookie_value(value):
    """Parse the cookie value string into a dict of key=value pairs."""
    result = {}
    for part in value.split('&'):
        if '=' in part:
            k, v = part.split('=', 1)
            result[k] = v
    return result


def require_auth(f):
    """Authentication decorator that checks for valid signed auth cookie."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_cookie = request.cookies.get('hive.server2.auth')
        if not auth_cookie:
            return redirect(url_for('login'))

        try:
            cookie_value = verify_and_extract(auth_cookie)
            params = parse_cookie_value(cookie_value)
            g.current_user = params.get('cu', 'unknown')
            g.user_role = params.get('role', 'user')
            g.session_id = params.get('sid', '')
        except ValueError:
            return redirect(url_for('login'))

        return f(*args, **kwargs)
    return decorated


# ---- HTML Templates (mimicking HiveServer2 Web UI) ----

LOGIN_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>HiveServer2 - Authentication</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }
        .header { background: #1a237e; color: white; padding: 12px 24px; font-size: 18px; }
        .header span { font-weight: 300; opacity: 0.8; margin-left: 8px; }
        .container { max-width: 400px; margin: 80px auto; padding: 32px; background: white; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h2 { color: #333; margin-top: 0; }
        label { display: block; margin-bottom: 4px; color: #555; font-size: 14px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; margin-bottom: 16px; border: 1px solid #ddd; border-radius: 3px; box-sizing: border-box; font-size: 14px; }
        button { background: #1a237e; color: white; border: none; padding: 10px 24px; border-radius: 3px; cursor: pointer; font-size: 14px; }
        button:hover { background: #283593; }
        .error { color: #c62828; background: #ffebee; padding: 10px; border-radius: 3px; margin-bottom: 16px; font-size: 13px; word-break: break-all; }
        .footer { text-align: center; margin-top: 24px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">Apache Hive<span>HiveServer2 Web UI</span></div>
    <div class="container">
        <h2>Sign In</h2>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST" action="/login">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" required>
            <label for="password">Password</label>
            <input type="password" id="password" name="password" required>
            <button type="submit">Sign In</button>
        </form>
        <div class="footer">Apache Hive 3.1.3 &mdash; HiveServer2</div>
    </div>
</body>
</html>"""

DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>HiveServer2 - Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }
        .header { background: #1a237e; color: white; padding: 12px 24px; font-size: 18px; display: flex; justify-content: space-between; align-items: center; }
        .header span { font-weight: 300; opacity: 0.8; margin-left: 8px; }
        .header .user-info { font-size: 13px; opacity: 0.9; }
        .nav { background: #283593; padding: 0 24px; }
        .nav a { color: rgba(255,255,255,0.8); text-decoration: none; padding: 10px 16px; display: inline-block; font-size: 14px; }
        .nav a:hover, .nav a.active { color: white; border-bottom: 2px solid #ffab40; }
        .container { max-width: 960px; margin: 24px auto; padding: 0 24px; }
        .card { background: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        .card h3 { margin-top: 0; color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; }
        th { color: #666; font-weight: 600; text-transform: uppercase; font-size: 11px; }
        .status-active { color: #2e7d32; }
        .status-idle { color: #f57f17; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
        .badge-admin { background: #e8eaf6; color: #1a237e; }
        .badge-user { background: #e8f5e9; color: #2e7d32; }
    </style>
</head>
<body>
    <div class="header">
        <div>Apache Hive<span>HiveServer2 Web UI</span></div>
        <div class="user-info">{{ user }} <span class="badge badge-{{ role }}">{{ role }}</span> | <a href="/logout" style="color:rgba(255,255,255,0.8);text-decoration:none;">Logout</a></div>
    </div>
    <div class="nav">
        <a href="/" class="active">Dashboard</a>
        <a href="/sessions">Active Sessions</a>
        <a href="/configuration">Configuration</a>
        <a href="/queries">Query Log</a>
    </div>
    <div class="container">
        <div class="card">
            <h3>Server Overview</h3>
            <table>
                <tr><td style="width:200px;color:#666;">Server Status</td><td class="status-active">● Running</td></tr>
                <tr><td style="color:#666;">Uptime</td><td>{{ uptime }}</td></tr>
                <tr><td style="color:#666;">Active Sessions</td><td>{{ session_count }}</td></tr>
                <tr><td style="color:#666;">Hive Version</td><td>3.1.3</td></tr>
                <tr><td style="color:#666;">Transport Mode</td><td>http</td></tr>
                <tr><td style="color:#666;">Authentication</td><td>CUSTOM</td></tr>
            </table>
        </div>
        <div class="card">
            <h3>Recent Queries</h3>
            <table>
                <tr><th>Query ID</th><th>User</th><th>State</th><th>Duration</th></tr>
                <tr><td>q-1001</td><td>etl_service</td><td class="status-active">RUNNING</td><td>2m 14s</td></tr>
                <tr><td>q-1000</td><td>analyst1</td><td class="status-idle">COMPLETED</td><td>45s</td></tr>
                <tr><td>q-0999</td><td>etl_service</td><td class="status-idle">COMPLETED</td><td>1m 32s</td></tr>
            </table>
        </div>
    </div>
</body>
</html>"""

SESSIONS_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>HiveServer2 - Active Sessions</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }
        .header { background: #1a237e; color: white; padding: 12px 24px; font-size: 18px; display: flex; justify-content: space-between; align-items: center; }
        .header span { font-weight: 300; opacity: 0.8; margin-left: 8px; }
        .header .user-info { font-size: 13px; opacity: 0.9; }
        .nav { background: #283593; padding: 0 24px; }
        .nav a { color: rgba(255,255,255,0.8); text-decoration: none; padding: 10px 16px; display: inline-block; font-size: 14px; }
        .nav a:hover, .nav a.active { color: white; border-bottom: 2px solid #ffab40; }
        .container { max-width: 960px; margin: 24px auto; padding: 0 24px; }
        .card { background: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        .card h3 { margin-top: 0; color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; }
        th { color: #666; font-weight: 600; text-transform: uppercase; font-size: 11px; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
        .badge-admin { background: #e8eaf6; color: #1a237e; }
        .badge-user { background: #e8f5e9; color: #2e7d32; }
    </style>
</head>
<body>
    <div class="header">
        <div>Apache Hive<span>HiveServer2 Web UI</span></div>
        <div class="user-info">{{ user }} <span class="badge badge-{{ role }}">{{ role }}</span> | <a href="/logout" style="color:rgba(255,255,255,0.8);text-decoration:none;">Logout</a></div>
    </div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/sessions" class="active">Active Sessions</a>
        <a href="/configuration">Configuration</a>
        <a href="/queries">Query Log</a>
    </div>
    <div class="container">
        <div class="card">
            <h3>Active Sessions</h3>
            <table>
                <tr><th>Session ID</th><th>User</th><th>IP Address</th><th>Started</th><th>Last Activity</th></tr>
                <tr><td>sess-a4f2c</td><td>etl_service</td><td>10.0.2.15</td><td>2024-01-15 08:00</td><td>2024-01-15 10:14</td></tr>
                <tr><td>sess-b7d91</td><td>analyst1</td><td>10.0.3.22</td><td>2024-01-15 09:30</td><td>2024-01-15 10:02</td></tr>
            </table>
        </div>
    </div>
</body>
</html>"""

CONFIGURATION_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>HiveServer2 - Configuration</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }
        .header { background: #1a237e; color: white; padding: 12px 24px; font-size: 18px; display: flex; justify-content: space-between; align-items: center; }
        .header span { font-weight: 300; opacity: 0.8; margin-left: 8px; }
        .header .user-info { font-size: 13px; opacity: 0.9; }
        .nav { background: #283593; padding: 0 24px; }
        .nav a { color: rgba(255,255,255,0.8); text-decoration: none; padding: 10px 16px; display: inline-block; font-size: 14px; }
        .nav a:hover, .nav a.active { color: white; border-bottom: 2px solid #ffab40; }
        .container { max-width: 960px; margin: 24px auto; padding: 0 24px; }
        .card { background: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        .card h3 { margin-top: 0; color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; }
        th { color: #666; font-weight: 600; text-transform: uppercase; font-size: 11px; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
        .badge-admin { background: #e8eaf6; color: #1a237e; }
        .badge-user { background: #e8f5e9; color: #2e7d32; }
        .access-denied { color: #c62828; background: #ffebee; padding: 16px; border-radius: 4px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <div>Apache Hive<span>HiveServer2 Web UI</span></div>
        <div class="user-info">{{ user }} <span class="badge badge-{{ role }}">{{ role }}</span> | <a href="/logout" style="color:rgba(255,255,255,0.8);text-decoration:none;">Logout</a></div>
    </div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/sessions">Active Sessions</a>
        <a href="/configuration" class="active">Configuration</a>
        <a href="/queries">Query Log</a>
    </div>
    <div class="container">
        {% if role == 'admin' %}
        <div class="card">
            <h3>Server Configuration</h3>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>hive.server2.transport.mode</td><td>http</td></tr>
                <tr><td>hive.server2.thrift.http.port</td><td>8000</td></tr>
                <tr><td>hive.server2.authentication</td><td>CUSTOM</td></tr>
                <tr><td>hive.server2.enable.doAs</td><td>false</td></tr>
                <tr><td>hive.metastore.uris</td><td>thrift://localhost:9083</td></tr>
                <tr><td>hive.server2.webui.port</td><td>8000</td></tr>
                <tr><td>hive.server2.webui.use.ssl</td><td>false</td></tr>
                <tr><td>hive.server2.session.check.interval</td><td>6000</td></tr>
                <tr><td>hive.server2.idle.session.timeout</td><td>7200000</td></tr>
                <tr><td>hive.server2.idle.session.check.operation</td><td>true</td></tr>
                <tr><td>system.flag</td><td>{{ flag }}</td></tr>
            </table>
        </div>
        {% else %}
        <div class="card">
            <div class="access-denied">Access Denied: Administrator privileges required to view server configuration.</div>
        </div>
        {% endif %}
    </div>
</body>
</html>"""

QUERIES_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>HiveServer2 - Query Log</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }
        .header { background: #1a237e; color: white; padding: 12px 24px; font-size: 18px; display: flex; justify-content: space-between; align-items: center; }
        .header span { font-weight: 300; opacity: 0.8; margin-left: 8px; }
        .header .user-info { font-size: 13px; opacity: 0.9; }
        .nav { background: #283593; padding: 0 24px; }
        .nav a { color: rgba(255,255,255,0.8); text-decoration: none; padding: 10px 16px; display: inline-block; font-size: 14px; }
        .nav a:hover, .nav a.active { color: white; border-bottom: 2px solid #ffab40; }
        .container { max-width: 960px; margin: 24px auto; padding: 0 24px; }
        .card { background: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }
        .card h3 { margin-top: 0; color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; }
        th { color: #666; font-weight: 600; text-transform: uppercase; font-size: 11px; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
        .badge-admin { background: #e8eaf6; color: #1a237e; }
        .badge-user { background: #e8f5e9; color: #2e7d32; }
        pre { background: #f5f5f5; padding: 8px; border-radius: 3px; font-size: 12px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="header">
        <div>Apache Hive<span>HiveServer2 Web UI</span></div>
        <div class="user-info">{{ user }} <span class="badge badge-{{ role }}">{{ role }}</span> | <a href="/logout" style="color:rgba(255,255,255,0.8);text-decoration:none;">Logout</a></div>
    </div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/sessions">Active Sessions</a>
        <a href="/configuration">Configuration</a>
        <a href="/queries" class="active">Query Log</a>
    </div>
    <div class="container">
        <div class="card">
            <h3>Query History</h3>
            <table>
                <tr><th>ID</th><th>User</th><th>Query</th><th>State</th><th>Duration</th></tr>
                <tr><td>q-1001</td><td>etl_service</td><td><pre>SELECT count(*) FROM warehouse.orders WHERE dt='2024-01-15'</pre></td><td>RUNNING</td><td>2m 14s</td></tr>
                <tr><td>q-1000</td><td>analyst1</td><td><pre>SELECT product_id, sum(revenue) FROM sales GROUP BY product_id LIMIT 100</pre></td><td>FINISHED</td><td>45s</td></tr>
                <tr><td>q-0999</td><td>etl_service</td><td><pre>INSERT OVERWRITE TABLE warehouse.daily_agg SELECT * FROM staging.raw_events</pre></td><td>FINISHED</td><td>1m 32s</td></tr>
                <tr><td>q-0998</td><td>data_eng</td><td><pre>SHOW TABLES IN warehouse</pre></td><td>FINISHED</td><td>0.2s</td></tr>
            </table>
        </div>
    </div>
</body>
</html>"""


# ---- Routes ----

_start_time = time.time()


@app.route('/ping')
def ping():
    return 'OK', 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template_string(LOGIN_TEMPLATE, error=None)

    username = request.form.get('username', '')
    password = request.form.get('password', '')

    user = HIVE_USERS.get(username)
    if user and hmac.compare_digest(user['password'], password):
        sid = secrets.token_hex(16)
        cookie_value = 'cu=' + username + '&role=' + user['role'] + '&sid=' + sid
        signed = sign_cookie(cookie_value)

        _sessions[sid] = {
            'user': username,
            'role': user['role'],
            'created': time.time()
        }

        resp = make_response(redirect(url_for('dashboard')))
        resp.set_cookie('hive.server2.auth', signed, httponly=True, samesite='Lax')
        return resp
    else:
        return render_template_string(LOGIN_TEMPLATE, error='Authentication failed: invalid credentials'), 401


@app.route('/cliservice', methods=['POST'])
def cli_service():
    """
    Thrift HTTP endpoint - mimics the HiveServer2 Thrift over HTTP interface.
    This is the primary programmatic interface that processes signed cookies.
    """
    auth_cookie = request.cookies.get('hive.server2.auth')
    if not auth_cookie:
        return 'Unauthorized: No authentication cookie provided', 401

    try:
        cookie_value = verify_and_extract(auth_cookie)
        params = parse_cookie_value(cookie_value)
        username = params.get('cu', 'unknown')
        return json.dumps({
            'status': 'ok',
            'user': username,
            'message': 'Thrift service ready'
        }), 200, {'Content-Type': 'application/json'}
    except ValueError as e:
        # The error message from verify_and_extract leaks the correct signature
        return str(e), 401


@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('hive.server2.auth')
    return resp


@app.route('/')
@require_auth
def dashboard():
    uptime_secs = int(time.time() - _start_time)
    hours = uptime_secs // 3600
    minutes = (uptime_secs % 3600) // 60
    uptime_str = f'{hours}h {minutes}m'
    return render_template_string(
        DASHBOARD_TEMPLATE,
        user=g.current_user,
        role=g.user_role,
        uptime=uptime_str,
        session_count=len(_sessions)
    )


@app.route('/sessions')
@require_auth
def sessions():
    return render_template_string(
        SESSIONS_TEMPLATE,
        user=g.current_user,
        role=g.user_role
    )


@app.route('/configuration')
@require_auth
def configuration():
    flag = _read_flag() if g.user_role == 'admin' else ''
    return render_template_string(
        CONFIGURATION_TEMPLATE,
        user=g.current_user,
        role=g.user_role,
        flag=flag
    )


@app.route('/queries')
@require_auth
def queries():
    return render_template_string(
        QUERIES_TEMPLATE,
        user=g.current_user,
        role=g.user_role
    )


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
