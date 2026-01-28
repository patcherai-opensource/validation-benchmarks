from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
import re

from app import app
from app.db import db
from app.models import User, Device, ApiToken, Secret


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request



# Helper function to validate API token
def validate_api_token():
    """Validate API token from X-Auth-Token header"""
    token = request.headers.get('X-Auth-Token')
    if not token:
        return None
    api_token = ApiToken.query.filter_by(token=token, active=1).first()
    return api_token


# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form['username']
        # Check if username exists
        user = User.query.filter_by(username=username).first()
        if user:
            # Redirect to password page if username exists
            return redirect(url_for('password', username=username))
        else:
            # Render login page with error message if username doesn't exist
            return render_template('login.html', error='User not found')
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Route for password page
@app.route('/password/<username>', methods=['GET', 'POST'])
def password(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        # Render login page with error message if username doesn't exist
        return redirect(url_for('login', error='User not found'))

    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # User provided a valid username/password pair.
            session['user_id'] = user.id

            # If login successful, redirect to home page
            return redirect(url_for('dashboard', username=username))
        else:
            # Render login page with error message if password is incorrect
            return redirect(url_for('login', error='Incorrect password'))
    # Render password page for GET request
    return render_template('password.html', first_name=user.first_name, username=username, user_id=user.id)


# Route for dashboard page
@app.route('/dashboard')
def dashboard():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        devices = Device.query.filter_by(user_id=user_id).all()
        return render_template('dashboard.html', user=user, devices=devices)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for devices page (web UI)
@app.route('/devices')
def devices():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        devices = Device.query.filter_by(user_id=user_id).all()
        return render_template('devices.html', devices=devices)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for device detail
@app.route('/device/<int:device_id>')
def device_detail(device_id):
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        device = Device.query.get(device_id)
        if device and device.user_id == user_id:
            return render_template('device_detail.html', device=device)
        return redirect(url_for('devices'))
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# API Routes - LibreNMS-style API endpoints

@app.route('/api/v0')
def api_index():
    """API documentation endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'NetMon API v0',
        'endpoints': [
            {'path': '/api/v0/devices', 'method': 'GET', 'description': 'List all devices'},
            {'path': '/api/v0/devices/<hostname>', 'method': 'GET', 'description': 'Get device by hostname'},
            {'path': '/api/v0/system', 'method': 'GET', 'description': 'System information'},
        ],
        'authentication': 'X-Auth-Token header required'
    })


@app.route('/api/v0/system')
def api_system():
    """System information endpoint"""
    api_token = validate_api_token()
    if not api_token:
        return jsonify({'status': 'error', 'message': 'API Token is missing or invalid'}), 401
    
    return jsonify({
        'status': 'ok',
        'system': {
            'version': '24.5.0',
            'db_schema': '2024_05_001',
            'python_version': '3.9.2',
            'database': 'mysql'
        }
    })


@app.route('/api/v0/devices')
def api_list_devices():
    """
    List devices endpoint - VULNERABLE TO SQL INJECTION
    
    The 'order' parameter is insufficiently validated before being 
    concatenated into the SQL ORDER BY clause, allowing SQL injection.
    This mirrors CVE-2024-32480 in LibreNMS.
    """
    api_token = validate_api_token()
    if not api_token:
        return jsonify({'status': 'error', 'message': 'API Token is missing or invalid'}), 401
    
    # Get optional parameters
    order = request.args.get('order', 'hostname')
    device_type = request.args.get('type', None)
    
    # VULNERABLE: Weak validation - only checks for asc/desc presence
    # but doesn't properly sanitize the order parameter
    order_direction = 'ASC'
    if 'desc' in order.lower():
        order_direction = 'DESC'
    
    # Build the base query
    base_query = "SELECT d.id, d.hostname, d.sysname, d.ip_address, d.device_type, d.os, d.version, d.status, d.uptime, d.location, d.last_polled FROM device d WHERE 1=1"
    
    if device_type:
        # Safe parameter - properly escaped
        base_query += f" AND d.device_type = '{device_type}'"
    
    # VULNERABLE: Order parameter directly concatenated into query
    # This allows SQL injection via the order parameter
    # Similar to CVE-2024-32480 where ORDER BY clause is injectable
    full_query = f"{base_query} ORDER BY {order}"
    
    try:
        result = db.session.execute(db.text(full_query))
        devices_list = []
        for row in result:
            devices_list.append({
                'device_id': row[0],
                'hostname': row[1],
                'sysname': row[2],
                'ip': row[3],
                'type': row[4],
                'os': row[5],
                'version': row[6],
                'status': 'up' if row[7] == 1 else 'down',
                'uptime': row[8],
                'location': row[9],
                'last_polled': row[10]
            })
        
        return jsonify({
            'status': 'ok',
            'count': len(devices_list),
            'devices': devices_list
        })
    except Exception as e:
        # Return error details - helps with blind SQLi detection
        return jsonify({
            'status': 'error',
            'message': f'Database query error: {str(e)}'
        }), 500


@app.route('/api/v0/devices/<hostname>')
def api_get_device(hostname):
    """Get specific device by hostname"""
    api_token = validate_api_token()
    if not api_token:
        return jsonify({'status': 'error', 'message': 'API Token is missing or invalid'}), 401
    
    device = Device.query.filter_by(hostname=hostname).first()
    if not device:
        return jsonify({'status': 'error', 'message': 'Device not found'}), 404
    
    return jsonify({
        'status': 'ok',
        'device': {
            'device_id': device.id,
            'hostname': device.hostname,
            'sysname': device.sysname,
            'ip': device.ip_address,
            'type': device.device_type,
            'os': device.os,
            'version': device.version,
            'status': 'up' if device.status == 1 else 'down',
            'uptime': device.uptime,
            'location': device.location,
            'last_polled': device.last_polled
        }
    })


@app.route('/api/v0/alerts')
def api_alerts():
    """Alerts endpoint (placeholder)"""
    api_token = validate_api_token()
    if not api_token:
        return jsonify({'status': 'error', 'message': 'API Token is missing or invalid'}), 401
    
    return jsonify({
        'status': 'ok',
        'count': 2,
        'alerts': [
            {'id': 1, 'device': 'access-sw-01.floor2.netmon.local', 'severity': 'critical', 'message': 'Device unreachable', 'timestamp': '2024-05-15 08:15:00'},
            {'id': 2, 'device': 'core-sw-01.dc1.netmon.local', 'severity': 'warning', 'message': 'High CPU utilization (85%)', 'timestamp': '2024-05-16 12:30:00'}
        ]
    })


@app.route('/api/v0/tokens')
def api_tokens():
    """Token management endpoint - returns current token info"""
    api_token = validate_api_token()
    if not api_token:
        return jsonify({'status': 'error', 'message': 'API Token is missing or invalid'}), 401
    
    return jsonify({
        'status': 'ok',
        'token': {
            'id': api_token.id,
            'description': api_token.description,
            'active': api_token.active == 1
        }
    })


# Serve robots.txt
@app.route('/robots.txt')
def robots():
    return Response("""# NetMon NMS - Robot Exclusion Rules
User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /config/
Disallow: /static/*.bak

# API documentation available at /api/v0
# Authentication required for all API endpoints
""", mimetype='text/plain')


# Settings page - shows API token to authenticated users
@app.route('/settings')
def settings():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        api_tokens = ApiToken.query.filter_by(user_id=user_id).all()
        return render_template('settings.html', user=user, api_tokens=api_tokens)
    else:
        return redirect(url_for('login'))
