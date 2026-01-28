from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
from sqlalchemy import text
import pymysql

from app import app
from app.db import db
from app.models import User, Device, SystemConfig


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request



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
        user = User.query.filter(User.id == user_id).first()
        # Get device stats
        total_devices = Device.query.count()
        active_devices = Device.query.filter_by(status='active').count()
        inactive_devices = Device.query.filter_by(status='inactive').count()
        
        stats = {
            'total': total_devices,
            'active': active_devices,
            'inactive': inactive_devices
        }
        
        return render_template('dashboard.html', user=user, stats=stats)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for device list page
@app.route('/devices')
def devices():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        # Show all devices for admin, only owned devices for regular users
        if user.role == 'admin':
            device_list = Device.query.all()
        else:
            device_list = Device.query.filter(Device.owner == user).all()
        return render_template('devices.html', devices=device_list, user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for device details
@app.route('/device/<int:device_id>')
def device_details(device_id):
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        device = Device.query.filter(Device.id == device_id).first()
        if device:
            # Check if user has permission to view this device
            if user.role == 'admin' or device.owner == user:
                return render_template('device_details.html', device=device, user=user)
            else:
                return Response('Access denied: You do not have permission to view this device.', status=403)
        else:
            return Response('Device not found.', status=404)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for MAC address search page
@app.route('/search/mac')
def search_mac_page():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        return render_template('search_mac.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# VULNERABLE ENDPOINT: SQL Injection in MAC address search
# This endpoint is vulnerable to SQL injection through the 'address' parameter
@app.route('/api/search/mac', methods=['GET', 'POST'])
def api_search_mac():
    # Retrieve user from session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.filter(User.id == user_id).first()
    
    # Get the MAC address from request (GET or POST)
    if request.method == 'POST':
        mac_input = request.form.get('address', '')
    else:
        mac_input = request.args.get('address', '')
    
    if not mac_input:
        return jsonify({'error': 'No MAC address provided'}), 400
    
    # Clean the MAC address by removing common MAC separators
    # This mimics the LibreNMS vulnerability pattern but preserves spaces for SQL syntax
    cleaned_mac = mac_input.replace(':', '').replace('-', '').replace('.', '').replace('0x', '')
    
    try:
        # VULNERABLE: Direct string interpolation into SQL query
        # This is the SQL injection vulnerability similar to CVE-2023-5591
        sql = f"SELECT * FROM device WHERE mac_address LIKE '%{cleaned_mac}%'"
        
        # Execute the raw SQL query
        result = db.session.execute(text(sql))
        
        # Fetch results
        devices = []
        for row in result:
            devices.append({
                'id': row[0],
                'hostname': row[1],
                'ip_address': row[2],
                'mac_address': row[3],
                'device_type': row[4],
                'status': row[5],
                'location': row[6],
                'last_seen': row[7]
            })
        
        return jsonify({'results': devices, 'count': len(devices)})
        
    except Exception as e:
        # Return SQL error messages (helps with error-based SQL injection)
        return jsonify({'error': str(e)}), 500


# Route for system configuration (admin only)
@app.route('/admin/config')
def admin_config():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user.role == 'admin':
            configs = SystemConfig.query.all()
            return render_template('admin_config.html', configs=configs, user=user)
        else:
            return Response('Access denied: Admin privileges required.', status=403)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for robots.txt
@app.route('/robots.txt')
def robots():
    return Response("""User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /backup/
Disallow: /config.bak
""", mimetype='text/plain')


# Route for API info
@app.route('/api')
def api_info():
    return jsonify({
        'application': 'NetMon Pro API',
        'version': '2.3.1',
        'endpoints': {
            'search': '/api/search/mac',
            'status': '/api/status'
        },
        'auth_required': True
    })


# Route for API status
@app.route('/api/status')
def api_status():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({
        'status': 'operational',
        'database': 'connected',
        'uptime': '14d 3h 27m'
    })


# Accidental backup file left by admin (realistic information leak)
@app.route('/config.bak')
def config_bak():
    return Response("""# NetMon Pro Configuration Backup
# Last updated: 2024-05-10
# NOTE: This file is a backup and may contain outdated information

[database]
host = 127.0.0.1
port = 3306
name = database

[users]
# Default operator account for device monitoring
# Password should be changed in production
operator = operator123

[snmp]
community = public
version = 2c
""", mimetype='text/plain')
