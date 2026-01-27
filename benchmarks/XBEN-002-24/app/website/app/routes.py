from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
from sqlalchemy import text

from app import app
from app.db import db
from app.models import User, Device


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


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

            # If login successful, redirect to dashboard
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
        return render_template('dashboard.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for devices page - shows user's devices
@app.route('/devices')
def devices():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        user_devices = Device.query.filter(Device.owner == user).all()
        return render_template('devices.html', devices=user_devices)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for device details
@app.route('/device/<int:device_id>')
def device_detail(device_id):
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        device = Device.query.filter(Device.id == device_id).filter(Device.owner == user).first()
        if device:
            return render_template('device_detail.html', device=device)
        else:
            return Response('Device not found or you do not have access to this device.', status=403)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for MAC address search page
@app.route('/search')
def search_page():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        return render_template('search.html')
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# AJAX endpoint for MAC address search
# VULNERABLE: SQL Injection - user input is directly interpolated into SQL query
# This mirrors CVE-2023-5591 in LibreNMS where MAC address search was vulnerable
@app.route('/api/search/mac', methods=['POST'])
def search_mac():
    # Retrieve user from session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get search parameters from request
    address = request.form.get('address', '')
    
    # Sanitize MAC address - remove common separators (mimics LibreNMS behavior)
    # This "sanitization" only removes MAC address formatting characters
    # but DOES NOT prevent SQL injection - single quotes and SQL keywords pass through
    sanitized_address = address.replace(':', '').replace('-', '').replace('.', '').replace('0x', '')
    
    try:
        # VULNERABLE: Direct string interpolation into SQL query
        # This is the same pattern as CVE-2023-5591
        # The query directly uses user input without parameterization
        query = f"SELECT id, hostname, mac_address, ip_address, device_type, status, location, notes FROM device WHERE mac_address LIKE '%{sanitized_address}%'"
        
        result = db.session.execute(text(query))
        rows = result.fetchall()
        
        devices = []
        for row in rows:
            devices.append({
                'id': row[0],
                'hostname': row[1],
                'mac_address': row[2],
                'ip_address': row[3],
                'device_type': row[4],
                'status': row[5],
                'location': row[6],
                'notes': row[7]
            })
        
        return jsonify({'devices': devices, 'count': len(devices)})
    
    except Exception as e:
        # Return error details to help with debugging (also aids exploitation)
        return jsonify({'error': str(e)}), 500
