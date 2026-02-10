from flask import Flask, render_template, redirect, url_for, request, session, jsonify, Response

from app import app
from app.db import db
from app.models import User, Organization
from functools import wraps


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'operator']:
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            if not user.enabled:
                return render_template('login.html', error='Account disabled')
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    org_users = User.query.filter_by(organization_id=user.organization_id).all()
    return render_template('dashboard.html', user=user, org_users=org_users)


@app.route('/admin')
@admin_required
def admin_panel():
    user = User.query.get(session['user_id'])
    org_users = User.query.filter_by(organization_id=user.organization_id).all()
    return render_template('admin.html', user=user, users=org_users)


@app.route('/admin/api/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': target_user.id,
        'username': target_user.username,
        'first_name': target_user.first_name,
        'last_name': target_user.last_name,
        'email': target_user.email,
        'role': target_user.role,
        'enabled': target_user.enabled,
        'organization_id': target_user.organization_id,
        'notes': target_user.notes
    })


@app.route('/admin/api/users/<int:user_id>/enable/<int:enable>', methods=['POST'])
@admin_required
def enable_user(user_id, enable):
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    target_user.enabled = bool(enable)
    db.session.commit()
    return jsonify({'success': True, 'enabled': target_user.enabled})


@app.route('/admin/api/users/<int:user_id>/reset-password', methods=['PUT'])
@admin_required  
def reset_password(user_id):
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    import random
    import string
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    target_user.password = new_password
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password reset successfully', 'temporary_password': new_password})
