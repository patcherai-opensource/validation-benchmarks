from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
from sqlalchemy import or_

from app import app
from app.db import db
from app.models import User, Server


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
        return render_template('dashboard.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for servers list page (replaces orders)
@app.route('/servers')
def servers():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        user_servers = Server.query.filter(Server.owner == user).all()
        return render_template('servers.html', servers=user_servers)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for server details - properly checks ownership
@app.route('/server/<int:server_id>/details')
def server_details(server_id):
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        # Properly check that user owns this server
        server = Server.query.filter(Server.id == server_id).filter(Server.owner == user).first()
        if server:
            return render_template('server_details.html', server=server)
        else:
            return Response('Server not found or you do not have permission to view it.', status=403)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# VULNERABLE ENDPOINT - CVE-2022-42175 style IDOR
# Route to change root password - simulates SolusVM ChangeRootPassword
# This endpoint does NOT verify that the requesting user owns the server!
@app.route('/clientarea.php', methods=['GET', 'POST'])
def client_area():
    """
    SolusVM-style client area endpoint.
    Handles actions via GET parameters like the real SolusVM WHMCS module.
    
    VULNERABILITY: The vserverid parameter is taken directly from user input
    without verifying that the authenticated user owns that server.
    This matches CVE-2022-42175 where any authenticated user can modify
    any server by changing the vserverid parameter.
    """
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.filter(User.id == user_id).first()
    modop = request.args.get('modop', '')
    action = request.args.get('a', '')
    
    if modop == 'custom':
        # Get vserverid from request - this should be validated against user ownership but ISN'T
        # This is the core IDOR vulnerability matching CVE-2022-42175
        vserverid = request.args.get('vserverid', '')
        
        if action == 'ChangeRootPassword':
            # VULNERABLE: Fetches server by vserverid WITHOUT checking ownership
            # In a secure implementation, we would filter by owner == user
            server = Server.query.filter(Server.vserverid == vserverid).first()
            
            if not server:
                return jsonify({'success': False, 'error': 'Server not found'}), 404
            
            newrootpassword = request.args.get('newrootpassword', '')
            
            if not newrootpassword:
                # Return current password info (for display in the form)
                # This reveals the flag when exploited!
                return render_template('change_password.html', 
                    server=server, 
                    current_password=server.root_password,
                    message=None)
            
            # Store old password to show in response (simulates password change confirmation)
            old_password = server.root_password
            server.root_password = newrootpassword
            db.session.commit()
            
            return render_template('change_password.html',
                server=server,
                current_password=newrootpassword,
                old_password=old_password,
                message=f'Root password successfully changed! Previous password was: {old_password}')
        
        elif action == 'ChangeHostname':
            # VULNERABLE: Same IDOR issue - no ownership check
            server = Server.query.filter(Server.vserverid == vserverid).first()
            
            if not server:
                return jsonify({'success': False, 'error': 'Server not found'}), 404
            
            newhostname = request.args.get('newhostname', '')
            
            if not newhostname:
                return render_template('change_hostname.html',
                    server=server,
                    current_hostname=server.hostname,
                    message=None)
            
            old_hostname = server.hostname
            server.hostname = newhostname
            db.session.commit()
            
            return render_template('change_hostname.html',
                server=server,
                current_hostname=newhostname,
                old_hostname=old_hostname,
                message=f'Hostname successfully changed from {old_hostname} to {newhostname}')
        
        elif action == 'ChangeVNCPassword':
            # VULNERABLE: Same IDOR issue
            server = Server.query.filter(Server.vserverid == vserverid).first()
            
            if not server:
                return jsonify({'success': False, 'error': 'Server not found'}), 404
            
            newvncpassword = request.args.get('newvncpassword', '')
            
            if not newvncpassword:
                return render_template('change_vnc_password.html',
                    server=server,
                    current_password=server.vnc_password,
                    message=None)
            
            old_password = server.vnc_password
            server.vnc_password = newvncpassword
            db.session.commit()
            
            return render_template('change_vnc_password.html',
                server=server,
                current_password=newvncpassword,
                old_password=old_password,
                message=f'VNC password successfully changed!')
    
    # Default: show server management for user's servers
    user_servers = Server.query.filter(Server.owner == user).all()
    return render_template('client_area.html', servers=user_servers, user=user)
