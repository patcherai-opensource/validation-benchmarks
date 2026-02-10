from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import hashlib
import re

from app import app
from app.db import db
from app.models import User


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error='Internal server error'), 500


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == hash_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        if not username or not email or not password or not first_name or not last_name:
            return render_template('register.html', error='All fields are required')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        if len(username) < 3:
            return render_template('register.html', error='Username must be at least 3 characters')
        
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return render_template('register.html', error='Invalid email format')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error='Username already exists')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return render_template('register.html', error='Email already registered')
        
        new_user = User(
            username=username,
            email=email,
            password=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login', error='Registration successful. Please login.'))
    
    return render_template('register.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)


@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)


@app.route('/admin')
def admin_panel():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return render_template('error.html', error='Access denied'), 403
    
    users = User.query.all()
    return render_template('admin.html', user=user, users=users)


@app.route('/admin/system-config')
def system_config():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return render_template('error.html', error='Access denied'), 403
    
    try:
        with open('/flag', 'r') as f:
            system_key = f.read().strip()
    except:
        system_key = 'Configuration not available'
    
    return render_template('system_config.html', user=user, system_key=system_key)
