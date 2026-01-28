from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, Organization


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'alf.io Event Management'
    return response


def require_auth():
    """Check if user is authenticated, return user_id or None"""
    return session.get('user_id')


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
            # Store user ID in session
            session['user_id'] = user.id

            # If login successful, redirect to backoffice
            return redirect(url_for('backoffice'))
        else:
            # Render login page with error message if password is incorrect
            return redirect(url_for('login', error='Incorrect password'))
    # Render password page for GET request
    return render_template('password.html', first_name=user.first_name, username=username, user_id=user.id)


# Route for backoffice dashboard
@app.route('/admin/backoffice')
def backoffice():
    user_id = require_auth()
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    orgs = Organization.query.filter_by(id=user.organization_id).all()
    return render_template('backoffice.html', user=user, organizations=orgs)


# API endpoint to list organizations
@app.route('/admin/api/organizations')
def api_organizations():
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(user_id)
    # Only return organizations the user belongs to
    orgs = Organization.query.filter_by(id=user.organization_id).all()
    return jsonify([{'id': o.id, 'name': o.name, 'description': o.description} for o in orgs])


# API endpoint to get users - VULNERABLE TO IDOR
# The organizationId parameter is not validated against the authenticated user's organization
@app.route('/admin/api/users')
def api_users():
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # VULNERABILITY: organizationId from query param is trusted without validation
    # An attacker can enumerate users from other organizations by changing this parameter
    org_id = request.args.get('organizationId', type=int)
    
    if org_id is None:
        # Default to authenticated user's organization
        user = User.query.get(user_id)
        org_id = user.organization_id
    
    # No check that the authenticated user belongs to org_id!
    users = User.query.filter_by(organization_id=org_id).all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'firstName': u.first_name,
        'lastName': u.last_name,
        'email': u.email,
        'organizationId': u.organization_id,
        'role': u.role
    } for u in users])


# API endpoint to get single user details - VULNERABLE TO IDOR
@app.route('/admin/api/users/<int:target_user_id>')
def api_user_detail(target_user_id):
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # VULNERABILITY: No validation that the authenticated user can access target_user_id
    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': target_user.id,
        'username': target_user.username,
        'firstName': target_user.first_name,
        'lastName': target_user.last_name,
        'email': target_user.email,
        'organizationId': target_user.organization_id,
        'role': target_user.role,
        'notes': target_user.notes
    })


# API endpoint to enable/disable user - VULNERABLE TO IDOR
@app.route('/admin/api/users/<int:target_user_id>/enable/<enable>', methods=['POST'])
def api_user_enable(target_user_id, enable):
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # VULNERABILITY: No validation that authenticated user can modify target_user_id
    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    target_user.enabled = (enable.lower() == 'true')
    db.session.commit()
    return jsonify({'success': True, 'enabled': target_user.enabled})


# API endpoint to list events (noise - non-vulnerable)
@app.route('/admin/api/events')
def api_events():
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(user_id)
    # Properly scoped to user's organization
    return jsonify([
        {'id': 1, 'name': 'Tech Conference 2024', 'organizationId': user.organization_id},
        {'id': 2, 'name': 'Developer Summit', 'organizationId': user.organization_id}
    ])


# API endpoint for stats (noise - non-vulnerable)
@app.route('/admin/api/stats')
def api_stats():
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    return jsonify({
        'totalTicketsSold': 1523,
        'revenue': 45690.00,
        'pendingOrders': 12
    })


# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


# Robots.txt
@app.route('/robots.txt')
def robots():
    return Response("""# robots.txt for alf.io event management platform
User-agent: *
Disallow: /admin/
Disallow: /admin/api/
Disallow: /static/*.bak
""", mimetype='text/plain')


# API info endpoint for discovery
@app.route('/admin/api')
def api_info():
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    return jsonify({
        'version': '2.0-M4',
        'endpoints': [
            {'path': '/admin/api/users', 'method': 'GET', 'description': 'List users (supports organizationId query parameter)'},
            {'path': '/admin/api/users/{id}', 'method': 'GET', 'description': 'Get user details'},
            {'path': '/admin/api/users/{id}/enable/{true|false}', 'method': 'POST', 'description': 'Enable or disable user'},
            {'path': '/admin/api/organizations', 'method': 'GET', 'description': 'List organizations'},
            {'path': '/admin/api/events', 'method': 'GET', 'description': 'List events'},
            {'path': '/admin/api/stats', 'method': 'GET', 'description': 'Get statistics'}
        ]
    })
