from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
from sqlalchemy import or_

from app import app
from app.db import db
from app.models import User, Organization


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def get_current_user():
    """Helper to get current authenticated user"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.filter(User.id == user_id).first()
    return None


def require_login(f):
    """Decorator to require login for routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Route for login page - Backoffice Admin Interface
@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            if not user.enabled:
                return render_template('login.html', error='Account is disabled. Contact administrator.')
            return redirect(url_for('password', username=username))
        else:
            return render_template('login.html', error='User not found')
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('organization_id', None)
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
            session['organization_id'] = user.organization_fk
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login', error='Incorrect password'))
    return render_template('password.html', first_name=user.first_name, username=username, user_id=user.id)


# Route for dashboard page - Backoffice main page
@app.route('/dashboard')
@require_login
def dashboard():
    user = get_current_user()
    org = Organization.query.filter(Organization.id == user.organization_fk).first()
    # Count users in current organization for dashboard stats
    user_count = User.query.filter(User.organization_fk == user.organization_fk).count()
    return render_template('dashboard.html', user=user, organization=org, user_count=user_count)


# Route for listing users in the organization - Backoffice User Management
@app.route('/admin/api/users')
@require_login
def list_users():
    """List users in the current user's organization"""
    user = get_current_user()
    # Correctly filtered to only show users from the same organization
    org_users = User.query.filter(User.organization_fk == user.organization_fk).all()
    return render_template('users.html', users=org_users, current_user=user)


# VULNERABLE ENDPOINT - IDOR vulnerability similar to CVE-2023-2260
# This endpoint allows viewing user details by userId parameter
# but FAILS TO VERIFY that the target user belongs to the same organization
# as the requesting user (missing principal-based access check)
@app.route('/admin/api/users/<int:user_id>')
@require_login
def get_user_details(user_id):
    """
    View user details - VULNERABLE TO IDOR
    
    The vulnerability: This endpoint retrieves user details based on the
    user_id parameter without verifying that the requesting user has
    authorization to view this user's data (i.e., that the target user
    belongs to the same organization as the requester).
    
    This mirrors CVE-2023-2260 where the fix added Principal-based access
    checks like checkAccessToUserId() to verify organization membership.
    """
    current_user = get_current_user()
    
    # VULNERABLE: No organization check - directly fetching user by ID
    # A proper implementation would check:
    # target_user = User.query.filter(User.id == user_id, 
    #                                  User.organization_fk == current_user.organization_fk).first()
    target_user = User.query.filter(User.id == user_id).first()
    
    if not target_user:
        return Response('User not found', status=404)
    
    # Returns sensitive data including secret_notes which may contain credentials
    return render_template('user_details.html', target_user=target_user, current_user=current_user)


# VULNERABLE ENDPOINT - Enable/disable user without proper authorization
@app.route('/admin/api/users/<int:user_id>/enable/<enable>')
@require_login
def enable_user(user_id, enable):
    """
    Enable or disable a user account - VULNERABLE TO IDOR
    
    Similar to the enable() method in alf.io's UserManager that was
    vulnerable before the fix. No verification that the current user
    has rights over the target userId.
    """
    current_user = get_current_user()
    
    # VULNERABLE: No organization membership check
    target_user = User.query.filter(User.id == user_id).first()
    
    if not target_user:
        return Response('User not found', status=404)
    
    # Update enabled status without authorization check
    target_user.enabled = (enable.lower() == 'true')
    db.session.commit()
    
    return redirect(url_for('get_user_details', user_id=user_id))


# VULNERABLE ENDPOINT - Reset password without proper authorization  
@app.route('/admin/api/users/<int:user_id>/reset-password', methods=['POST'])
@require_login
def reset_password(user_id):
    """
    Reset user password - VULNERABLE TO IDOR
    
    Similar to the resetPassword() method in alf.io's UserManager.
    No verification that the current user has rights over the target userId.
    """
    current_user = get_current_user()
    
    # VULNERABLE: No organization membership check
    target_user = User.query.filter(User.id == user_id).first()
    
    if not target_user:
        return Response('User not found', status=404)
    
    # Generate new password (in production this would send email)
    import secrets
    new_password = secrets.token_urlsafe(12)
    target_user.password = new_password
    db.session.commit()
    
    # Return the new password (simulating email send or showing in UI)
    return render_template('password_reset_result.html', 
                          target_user=target_user, 
                          new_password=new_password,
                          current_user=current_user)


# List all organizations (for display purposes)
@app.route('/admin/api/organizations')
@require_login
def list_organizations():
    """List all organizations - for navigation/context"""
    user = get_current_user()
    orgs = Organization.query.all()
    return render_template('organizations.html', organizations=orgs, current_user=user)


# API endpoint for JSON user data (alternative attack surface)
@app.route('/api/v1/admin/users/<int:user_id>')
@require_login  
def api_get_user(user_id):
    """
    JSON API endpoint for user data - VULNERABLE TO IDOR
    
    This mirrors the REST API endpoints in alf.io's UsersApiController
    that were vulnerable to IDOR attacks.
    """
    current_user = get_current_user()
    
    # VULNERABLE: No organization check
    target_user = User.query.filter(User.id == user_id).first()
    
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': target_user.id,
        'username': target_user.username,
        'firstName': target_user.first_name,
        'lastName': target_user.last_name,
        'email': target_user.email,
        'role': target_user.role,
        'enabled': target_user.enabled,
        'organizationId': target_user.organization_fk,
        'secretNotes': target_user.secret_notes  # Sensitive data exposed
    })
