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


def get_current_user():
    """Get the currently authenticated user from session"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


# Route for login page - Backoffice authentication
@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form['username']
        # Check if username exists
        user = User.query.filter_by(username=username).first()
        if user:
            if not user.enabled:
                return render_template('login.html', error='Account is disabled')
            # Redirect to password page if username exists
            return redirect(url_for('password', username=username))
        else:
            # Render login page with error message if username doesn't exist
            return render_template('login.html', error='User not found')
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Route for password page
@app.route('/password/<username>', methods=['GET', 'POST'])
def password(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('login', error='User not found'))

    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login', error='Incorrect password'))
    return render_template('password.html', first_name=user.first_name, username=username, user_id=user.id)


# Route for dashboard/backoffice main page
@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    org = Organization.query.get(user.organization_id)
    return render_template('dashboard.html', user=user, organization=org)


# Admin API - List organizations (requires authentication)
@app.route('/admin/api/organizations')
def list_organizations():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Only return organizations the user has access to
    orgs = Organization.query.all()
    return jsonify({
        'organizations': [{'id': o.id, 'name': o.name} for o in orgs]
    })


# Admin API - Get organization details
# VULNERABILITY: This endpoint does not validate that the requesting user
# has access to the specified organization. Any authenticated user can
# access any organization's details by manipulating the organizationId parameter.
@app.route('/admin/api/organization')
def get_organization():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    org_id = request.args.get('organizationId')
    if not org_id:
        # Default to user's organization if not specified
        org_id = user.organization_id
    
    # IDOR VULNERABILITY: No authorization check to verify user belongs to this organization
    # The application should verify: user.organization_id == org_id
    # But it doesn't, allowing access to any organization's data
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify({
        'id': org.id,
        'name': org.name,
        'description': org.description,
        'apiKey': org.api_key,
        'userCount': len(org.users)
    })


# Admin API - List users in an organization
# VULNERABILITY: Same IDOR issue - no authorization check
@app.route('/admin/api/users')
def list_users():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    org_id = request.args.get('organizationId')
    if not org_id:
        org_id = user.organization_id
    
    # IDOR VULNERABILITY: No check that user belongs to the requested organization
    users = User.query.filter_by(organization_id=org_id).all()
    return jsonify({
        'users': [{
            'id': u.id,
            'username': u.username,
            'firstName': u.first_name,
            'lastName': u.last_name,
            'email': u.email,
            'role': u.role,
            'enabled': u.enabled
        } for u in users]
    })


# Admin API - Get user details
@app.route('/admin/api/users/<int:user_id>')
def get_user(user_id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # IDOR VULNERABILITY: No authorization check
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': target_user.id,
        'username': target_user.username,
        'firstName': target_user.first_name,
        'lastName': target_user.last_name,
        'email': target_user.email,
        'role': target_user.role,
        'organizationId': target_user.organization_id,
        'enabled': target_user.enabled
    })


# Admin API - Enable/disable user
@app.route('/admin/api/users/<int:user_id>/enable/<enable>', methods=['POST'])
def enable_user(user_id, enable):
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # IDOR VULNERABILITY: No authorization check before enabling/disabling
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    target_user.enabled = (enable.lower() == 'true')
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'User {user_id} enabled status set to {enable}'})


# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'alf.io-backoffice'})
