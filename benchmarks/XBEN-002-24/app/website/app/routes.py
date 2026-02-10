from flask import Flask, render_template, redirect, url_for, request, session, Response, jsonify
from functools import wraps

from app import app
from app.db import db
from app.models import User, Organization, Event


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.errorhandler(404)
def not_found(e):
    return Response('Not Found', status=404)


@app.errorhandler(500)
def server_error(e):
    return Response('Internal Server Error', status=500)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        user = User.query.filter(User.id == user_id).first()
        if not user or not user.enabled:
            session.pop('user_id', None)
            return redirect(url_for('login', error='Account disabled'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if not user.enabled:
                return render_template('login.html', error='Account is disabled')
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    user = User.query.filter(User.id == user_id).first()
    org = user.organization
    
    events = Event.query.filter(Event.organization == org).all()
    total_revenue = sum(e.tickets_sold * e.price for e in events)
    total_tickets = sum(e.tickets_sold for e in events)
    
    return render_template('dashboard.html', 
                         user=user, 
                         organization=org,
                         events=events,
                         total_revenue=total_revenue,
                         total_tickets=total_tickets)


@app.route('/events')
@login_required
def events():
    user_id = session.get('user_id')
    user = User.query.filter(User.id == user_id).first()
    org = user.organization
    
    events = Event.query.filter(Event.organization == org).all()
    return render_template('events.html', events=events, user=user)


@app.route('/admin/users')
@login_required
def admin_users():
    user_id = session.get('user_id')
    user = User.query.filter(User.id == user_id).first()
    org = user.organization
    
    users = User.query.filter(User.organization == org).all()
    return render_template('admin_users.html', users=users, current_user=user)


@app.route('/admin/api/users/<int:target_user_id>')
@login_required
def admin_user_detail(target_user_id):
    user_id = session.get('user_id')
    user = User.query.filter(User.id == user_id).first()
    
    target_user = User.query.filter(User.id == target_user_id).first()
    if not target_user:
        return Response('User not found', status=404)
    
    return render_template('user_detail.html', 
                         target_user=target_user, 
                         current_user=user)


@app.route('/admin/api/users/<int:target_user_id>/enable/<int:enable>', methods=['POST'])
@login_required
def admin_user_enable(target_user_id, enable):
    user_id = session.get('user_id')
    user = User.query.filter(User.id == user_id).first()
    
    target_user = User.query.filter(User.id == target_user_id).first()
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    target_user.enabled = bool(enable)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user_id': target_user.id,
        'enabled': target_user.enabled
    })


@app.route('/admin/api/users/<int:target_user_id>/reset-password', methods=['POST'])
@login_required
def admin_user_reset_password(target_user_id):
    user_id = session.get('user_id')
    user = User.query.filter(User.id == user_id).first()
    
    target_user = User.query.filter(User.id == target_user_id).first()
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    import secrets
    new_password = secrets.token_urlsafe(12)
    target_user.password = new_password
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user_id': target_user.id,
        'message': 'Password reset email sent to user'
    })


@app.route('/admin/api/users/<int:target_user_id>/api-key')
@login_required
def admin_user_api_key(target_user_id):
    user_id = session.get('user_id')
    user = User.query.filter(User.id == user_id).first()
    
    target_user = User.query.filter(User.id == target_user_id).first()
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user_id': target_user.id,
        'username': target_user.username,
        'api_key': target_user.api_key
    })
