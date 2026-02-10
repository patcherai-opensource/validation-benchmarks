"""
Multi-tenant Admin Backoffice API
Simulates alf.io's administrative interface with IDOR vulnerability (CVE-2023-2260)

The vulnerability: Authenticated users can access/modify users from other organizations
by tampering with userId parameter in API requests. The backend fails to verify
organization membership before performing operations.
"""
from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, Organization
from functools import wraps


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'alf.io-backoffice/2.0-M4'
    return response


def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get the currently authenticated user"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


# ==================== WEB UI ROUTES ====================

@app.route('/', methods=['GET', 'POST'])
def login():
    """Login page for the backoffice"""
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if not user.enabled:
                return render_template('login.html', error='Account is disabled')
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """Logout and clear session"""
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    """Main dashboard showing user's organization"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # Get users from the current user's organization
    org_users = User.query.filter_by(organization_id=user.organization_id).all()
    
    return render_template('dashboard.html', user=user, org_users=org_users)


# ==================== ADMIN API ROUTES ====================
# These routes simulate alf.io's UsersApiController
# VULNERABILITY: No organization-based access control check on userId parameter


@app.route('/admin/api/users', methods=['GET'])
@login_required
def list_users():
    """
    List all users (properly filtered by organization)
    GET /admin/api/users
    """
    current_user = get_current_user()
    users = User.query.filter_by(organization_id=current_user.organization_id).all()
    
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'firstName': u.first_name,
        'lastName': u.last_name,
        'email': u.email,
        'role': u.role,
        'enabled': u.enabled,
        'organizationId': u.organization_id
    } for u in users])


@app.route('/admin/api/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """
    Get user details by ID
    GET /admin/api/users/{id}
    
    VULNERABILITY: No check that user_id belongs to the current user's organization!
    This allows cross-tenant data access (IDOR).
    """
    # VULNERABLE: Directly fetches user without organization check
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Returns full user details including sensitive 'notes' field
    return jsonify({
        'id': user.id,
        'username': user.username,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'email': user.email,
        'role': user.role,
        'enabled': user.enabled,
        'organizationId': user.organization_id,
        'notes': user.notes  # Sensitive field containing flag for admin user
    })


@app.route('/admin/api/users/<int:user_id>/enable/<enable>', methods=['POST'])
@login_required
def enable_user(user_id, enable):
    """
    Enable or disable a user account
    POST /admin/api/users/{id}/enable/{enable}
    
    VULNERABILITY: No check that user_id belongs to the current user's organization!
    Allows enabling/disabling users from other organizations.
    """
    # VULNERABLE: Directly modifies user without organization check
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.enabled = (enable.lower() == 'true')
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'User {user.username} {"enabled" if user.enabled else "disabled"}'
    })


@app.route('/admin/api/users/<int:user_id>/reset-password', methods=['PUT'])
@login_required
def reset_password(user_id):
    """
    Reset a user's password (returns temporary password)
    PUT /admin/api/users/{id}/reset-password
    
    VULNERABILITY: No check that user_id belongs to the current user's organization!
    Allows password reset for users in other organizations.
    """
    import random
    import string
    
    # VULNERABLE: Directly modifies user without organization check
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Generate temporary password
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    user.password = temp_password
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Password reset for {user.username}',
        'temporaryPassword': temp_password
    })


@app.route('/admin/api/organizations', methods=['GET'])
@login_required
def list_organizations():
    """
    List all organizations (reveals organization structure)
    GET /admin/api/organizations
    """
    orgs = Organization.query.all()
    
    return jsonify([{
        'id': o.id,
        'name': o.name,
        'description': o.description
    } for o in orgs])


@app.route('/admin/api/organizations/<int:org_id>/users', methods=['GET'])
@login_required
def list_org_users(org_id):
    """
    List users in a specific organization
    GET /admin/api/organizations/{organizationId}/users
    
    VULNERABILITY: No check that current user belongs to the requested organization!
    Allows enumeration of users in other organizations.
    """
    # VULNERABLE: Returns users from any organization without access check
    users = User.query.filter_by(organization_id=org_id).all()
    
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'firstName': u.first_name,
        'lastName': u.last_name,
        'email': u.email,
        'role': u.role,
        'enabled': u.enabled
    } for u in users])


@app.route('/admin/api/check-user/<int:user_id>', methods=['GET'])
@login_required  
def check_user_access(user_id):
    """
    Debug endpoint to check if current user has access to target user
    (In a secure implementation, this would verify organization membership)
    """
    current_user = get_current_user()
    target_user = User.query.get(user_id)
    
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Note: This check exists but is NOT applied in the actual API endpoints above
    same_org = (current_user.organization_id == target_user.organization_id)
    
    return jsonify({
        'currentUser': current_user.username,
        'currentOrganization': current_user.organization_id,
        'targetUser': target_user.username,
        'targetOrganization': target_user.organization_id,
        'sameOrganization': same_org,
        'accessAllowed': same_org  # Shows what SHOULD be enforced
    })
