from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, Order, Device, ApiToken, Secret
from functools import wraps
import hashlib


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


def check_api_token():
    """Check API token from X-Auth-Token header"""
    token = request.headers.get('X-Auth-Token')
    if not token:
        return None
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    api_token = ApiToken.query.filter_by(token_hash=token_hash, disabled=0).first()
    
    if api_token:
        return api_token.user
    return None


def api_auth_required(f):
    """Decorator to require API authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = check_api_token()
        if user is None:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or missing API token. Use X-Auth-Token header.'
            }), 401
        return f(user, *args, **kwargs)
    return decorated_function


# ============================================================================
# API v0 Routes - LibreNMS-style API
# ============================================================================

@app.route('/api/v0')
def api_info():
    """API information endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'LibreNMS-style Network Monitoring API',
        'version': 'v0',
        'endpoints': [
            '/api/v0/devices - List all devices (requires X-Auth-Token)',
            '/api/v0/devices?order=<column> - Sort devices by column',
        ],
        'authentication': 'Use X-Auth-Token header with your API token',
        'hint': 'Default API token for testing: librenms_api_token_12345'
    })


@app.route('/api/v0/devices')
@api_auth_required
def list_devices(user):
    """
    List all devices in the monitoring system.
    
    CVE-2024-32480 Vulnerable Implementation:
    The 'order' parameter is taken directly from user input and insufficiently 
    validated before being concatenated into the SQL ORDER BY clause. This allows
    an attacker with a valid API token to perform SQL injection.
    
    The weak validation only checks for presence of 'asc' or 'desc' keywords,
    but does not properly sanitize the order parameter.
    """
    # Get order parameter from request (vulnerable to SQL injection)
    order = request.args.get('order', 'device_id')
    
    # Weak validation - only checks for asc/desc presence
    # This matches the vulnerable pattern from CVE-2024-32480
    order_lower = order.lower()
    if 'asc' not in order_lower and 'desc' not in order_lower:
        # If neither asc nor desc, append default
        order = order + ' ASC'
    
    # Build the query with direct string concatenation (VULNERABLE!)
    # This mirrors the vulnerable code from includes/html/api_functions.inc.php
    # $dev_query = "SELECT ... ORDER BY $order";
    try:
        query = f"SELECT device_id, hostname, sysname, ip, status, os, location, uptime FROM device ORDER BY {order}"
        
        # Execute raw SQL query
        result = db.session.execute(db.text(query))
        devices = []
        for row in result:
            devices.append({
                'device_id': row[0],
                'hostname': row[1],
                'sysname': row[2],
                'ip': row[3],
                'status': 'up' if row[4] == 1 else 'down',
                'os': row[5],
                'location': row[6],
                'uptime': row[7]
            })
        
        return jsonify({
            'status': 'ok',
            'count': len(devices),
            'devices': devices
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Query error: {str(e)}'
        }), 500


# ============================================================================
# Web UI Routes (kept for reference but not the main vulnerability)
# ============================================================================

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
        return render_template('dashboard.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for orders page
@app.route('/orders')
def orders():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('orders.html', orders=user.orders)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))
