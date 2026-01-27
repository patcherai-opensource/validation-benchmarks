from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
from sqlalchemy import text

from app import app
from app.db import db
from app.models import User, Device, ApiToken, SystemSecret


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'NetMon NMS v2.4.1'
    return response


def validate_api_token():
    """Validate API token from X-Auth-Token header"""
    token = request.headers.get('X-Auth-Token')
    if not token:
        return None
    api_token = ApiToken.query.filter_by(token=token).first()
    if api_token:
        return api_token.user
    return None


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
        devices = Device.query.all()
        return render_template('dashboard.html', user=user, devices=devices)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for devices page
@app.route('/devices')
def devices():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        devices = Device.query.all()
        return render_template('devices.html', devices=devices, user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# API endpoint for listing devices - VULNERABLE TO SQL INJECTION
# Similar to CVE-2024-32480 in LibreNMS
@app.route('/api/v0/devices', methods=['GET'])
def api_list_devices():
    """
    API endpoint to list network devices.
    Requires X-Auth-Token header for authentication.
    Supports 'order' parameter for sorting results.
    """
    # Validate API token
    user = validate_api_token()
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'API token is missing or invalid'
        }), 401
    
    # Get sorting parameter
    order = request.args.get('order', 'device_id')
    
    # VULNERABLE: The order parameter is directly concatenated into the SQL query
    # without proper validation, similar to CVE-2024-32480 in LibreNMS.
    # This allows SQL injection via the ORDER BY clause.
    # The fix would be to use a whitelist of allowed column names.
    
    # Weak validation - only checks for presence of 'asc' or 'desc' keywords
    # but doesn't prevent SQL injection payloads
    order_lower = order.lower()
    if 'asc' in order_lower or 'desc' in order_lower or order_lower in ['device_id', 'hostname', 'ip', 'status']:
        pass  # Basic validation passes
    
    try:
        # Build query with vulnerable ORDER BY clause
        # The ORDER BY clause is vulnerable to SQL injection - attacker can use
        # techniques like: (SELECT ... FROM ...) or conditional expressions
        query = f"SELECT d.device_id, d.hostname, d.sysname, d.ip, d.status, d.os, d.hardware, d.location, d.uptime FROM device d ORDER BY {order}"
        
        result = db.session.execute(text(query))
        devices = []
        for row in result:
            devices.append({
                'device_id': row[0],
                'hostname': row[1],
                'sysname': row[2],
                'ip': row[3],
                'status': row[4],
                'os': row[5],
                'hardware': row[6],
                'location': row[7],
                'uptime': row[8]
            })
        
        return jsonify({
            'status': 'ok',
            'count': len(devices),
            'devices': devices
        })
    except Exception as e:
        # Return detailed error which helps with SQL injection debugging
        error_msg = str(e)
        return jsonify({
            'status': 'error',
            'message': f'Database query failed',
            'details': error_msg
        }), 500


# API endpoint to get device details
@app.route('/api/v0/devices/<int:device_id>', methods=['GET'])
def api_get_device(device_id):
    """Get details for a specific device"""
    user = validate_api_token()
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'API token is missing or invalid'
        }), 401
    
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return jsonify({
            'status': 'error',
            'message': 'Device not found'
        }), 404
    
    return jsonify({
        'status': 'ok',
        'device': {
            'device_id': device.device_id,
            'hostname': device.hostname,
            'sysname': device.sysname,
            'ip': device.ip,
            'status': device.status,
            'os': device.os,
            'hardware': device.hardware,
            'location': device.location,
            'uptime': device.uptime
        }
    })


# API documentation endpoint
@app.route('/api/v0', methods=['GET'])
def api_docs():
    """API documentation"""
    return jsonify({
        'status': 'ok',
        'version': 'v0',
        'endpoints': [
            {
                'path': '/api/v0/devices',
                'method': 'GET',
                'description': 'List all network devices',
                'parameters': {
                    'order': 'Sort results by column (device_id, hostname, ip, status). Default: device_id'
                },
                'authentication': 'X-Auth-Token header required'
            },
            {
                'path': '/api/v0/devices/<device_id>',
                'method': 'GET',
                'description': 'Get details for a specific device',
                'authentication': 'X-Auth-Token header required'
            }
        ]
    })


# User settings page - shows API token
@app.route('/settings')
def settings():
    """User settings page showing API token"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        api_token = ApiToken.query.filter_by(user_id=user_id).first()
        return render_template('settings.html', user=user, api_token=api_token)
    else:
        return redirect(url_for('login'))
