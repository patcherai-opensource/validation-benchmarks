from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
from sqlalchemy import or_

from app import app
from app.db import db
from app.models import User, VirtualServer


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
            return render_template('login.html', error='Account not found. Please check your username.')
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
        return redirect(url_for('login', error='Account not found'))

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
            return redirect(url_for('login', error='Authentication failed'))
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


# Route for virtual servers list
@app.route('/servers')
def servers():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        my_servers = VirtualServer.query.filter(VirtualServer.owner == user).filter(VirtualServer.transferred == False).all()
        return render_template('servers.html', servers=my_servers)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for server credentials (view root password)
@app.route('/server/<int:vserverid>/credentials')
def server_credentials(vserverid):
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        server = VirtualServer.query.filter(VirtualServer.id == vserverid).filter(or_(VirtualServer.owner == user, VirtualServer.manager == user)).first()
        if server:
            return render_template('credentials.html', server=server)
        else:
            return Response('Access denied. You do not have permission to view credentials for this server.', status=403)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for managed/transferred servers page
@app.route('/servers/managed')
def managed_servers():
    db.session.expire_all()
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        transferred_servers = VirtualServer.query.filter(VirtualServer.manager == user).all()
        return render_template('managed_servers.html', servers=transferred_servers)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route to transfer server management
@app.route('/server/<int:vserverid>/transfer')
def server_transfer(vserverid):
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()

        # VULNERABILITY: The server is retrieved from the DB using the vserverid supplied
        # by the user, without checking if the user actually owns this server.
        # This allows any authenticated user to transfer arbitrary servers to themselves.
        server = VirtualServer.query.filter(VirtualServer.id == vserverid).first_or_404()
        server.manager = user
        server.transferred = True
        db.session.commit()
        
        my_servers = VirtualServer.query.filter(VirtualServer.owner == user).filter(VirtualServer.transferred == False).all()
        return render_template('servers.html', servers=my_servers)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# API endpoint for server status - noise endpoint
@app.route('/api/v1/server/<int:vserverid>/status')
def api_server_status(vserverid):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.filter(User.id == user_id).first()
    server = VirtualServer.query.filter(VirtualServer.id == vserverid).filter(or_(VirtualServer.owner == user, VirtualServer.manager == user)).first()
    if server:
        return jsonify({
            'vserverid': server.id,
            'hostname': server.hostname,
            'status': server.status,
            'uptime': '14d 6h 32m' if server.status == 'running' else '0'
        })
    return jsonify({'error': 'Server not found or access denied'}), 404


# API endpoint for system info - noise endpoint
@app.route('/api/v1/system/info')
def api_system_info():
    return jsonify({
        'version': '4.1.2',
        'product': 'CloudVPS Control Panel',
        'api_version': 'v1',
        'maintenance_mode': False
    })


# Noise endpoint - support tickets (placeholder)
@app.route('/support')
def support():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    return render_template('support.html')


# Noise endpoint - billing (placeholder)
@app.route('/billing')
def billing():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    return render_template('billing.html')


# Serve robots.txt
@app.route('/robots.txt')
def robots_txt():
    return app.send_static_file('robots.txt')
