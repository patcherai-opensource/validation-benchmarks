from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
from sqlalchemy import or_

from app import app
from app.db import db
from app.models import Organization, User, Event


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


def get_current_user():
    """Helper to get the current authenticated user"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.filter(User.id == user_id).first()
    return None


def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if not user.enabled:
                return render_template('login.html', error='Account is disabled. Contact your administrator.')
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Route for dashboard page
@app.route('/admin/dashboard')
@require_auth
def dashboard():
    user = get_current_user()
    # Get events for user's organization
    events = Event.query.filter(Event.organization_fk == user.organization_fk).all()
    return render_template('dashboard.html', user=user, events=events)


# Route for events list
@app.route('/admin/events')
@require_auth
def events_list():
    user = get_current_user()
    events = Event.query.filter(Event.organization_fk == user.organization_fk).all()
    return render_template('events.html', user=user, events=events)


# Route for event details
@app.route('/admin/event/<int:event_id>')
@require_auth
def event_detail(event_id):
    user = get_current_user()
    event = Event.query.filter(Event.id == event_id).filter(Event.organization_fk == user.organization_fk).first()
    if not event:
        return Response('Event not found or access denied.', status=404)
    return render_template('event_detail.html', user=user, event=event)


# Route for users management (organization users)
@app.route('/admin/users')
@require_auth
def users_list():
    user = get_current_user()
    # List users in current user's organization
    org_users = User.query.filter(User.organization_fk == user.organization_fk).all()
    return render_template('users.html', user=user, users=org_users)


# VULNERABLE ENDPOINT: View user details - missing organization check
@app.route('/admin/api/users/<int:user_id>')
@require_auth
def api_user_detail(user_id):
    """
    API endpoint to get user details.
    VULNERABILITY: Does not verify that the target user belongs to the same 
    organization as the authenticated user. This allows viewing users from 
    other organizations by simply changing the user_id parameter.
    """
    current_user = get_current_user()
    
    # INSECURE: No check that target_user.organization_fk == current_user.organization_fk
    target_user = User.query.filter(User.id == user_id).first()
    
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Return user details including sensitive api_key field
    return jsonify({
        'id': target_user.id,
        'username': target_user.username,
        'first_name': target_user.first_name,
        'last_name': target_user.last_name,
        'email': target_user.email,
        'role': target_user.role,
        'enabled': target_user.enabled,
        'api_key': target_user.api_key,
        'organization_id': target_user.organization_fk
    })


# VULNERABLE ENDPOINT: Enable/disable user - missing organization check
@app.route('/admin/api/users/<int:user_id>/enable/<int:enable>', methods=['POST'])
@require_auth
def api_user_enable(user_id, enable):
    """
    API endpoint to enable or disable a user account.
    VULNERABILITY: Does not verify that the target user belongs to the same 
    organization as the authenticated user.
    """
    current_user = get_current_user()
    
    # Only admins and operators can enable/disable users
    if current_user.role not in ['admin', 'operator']:
        return jsonify({'error': 'Insufficient privileges'}), 403
    
    # INSECURE: No organization membership check
    target_user = User.query.filter(User.id == user_id).first()
    
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    target_user.enabled = bool(enable)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'User {target_user.username} has been {"enabled" if enable else "disabled"}'
    })


# Secure endpoint for comparison - properly checks organization
@app.route('/admin/api/events/<int:event_id>')
@require_auth
def api_event_detail(event_id):
    """
    API endpoint to get event details.
    SECURE: Properly checks organization membership.
    """
    current_user = get_current_user()
    
    # SECURE: Checks that event belongs to user's organization
    event = Event.query.filter(Event.id == event_id).filter(Event.organization_fk == current_user.organization_fk).first()
    
    if not event:
        return jsonify({'error': 'Event not found or access denied'}), 404
    
    return jsonify({
        'id': event.id,
        'name': event.name,
        'description': event.description,
        'date': event.date,
        'location': event.location,
        'capacity': event.capacity,
        'tickets_sold': event.tickets_sold
    })


# Organization info endpoint
@app.route('/admin/api/organization')
@require_auth
def api_organization():
    """Get current user's organization info"""
    current_user = get_current_user()
    org = Organization.query.filter(Organization.id == current_user.organization_fk).first()
    
    return jsonify({
        'id': org.id,
        'name': org.name,
        'description': org.description
    })


# List all users endpoint (for admin interface)
@app.route('/admin/api/users')
@require_auth
def api_users_list():
    """List users in current organization"""
    current_user = get_current_user()
    
    # SECURE: Only lists users from current user's organization
    users = User.query.filter(User.organization_fk == current_user.organization_fk).all()
    
    return jsonify({
        'users': [{
            'id': u.id,
            'username': u.username,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'role': u.role,
            'enabled': u.enabled
        } for u in users]
    })


# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


# Robots.txt - hints at API docs
@app.route('/robots.txt')
def robots():
    return Response("""User-agent: *
Disallow: /admin/
Disallow: /api-docs/
Disallow: /internal/
""", mimetype='text/plain')


# API documentation - contains test credentials (realistic leak)
@app.route('/api-docs/')
def api_docs():
    return render_template('api_docs.html')
