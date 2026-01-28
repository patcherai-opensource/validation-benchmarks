from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, ConfigStore

import json
import copy


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


# Keywords that should be denied in config updates for security
KEYWORD_DENYLIST = ['secret_data', 'admin_key', 'internal_flag', '__proto__', 'constructor', 'is_admin']


def contains_denied_keyword(obj):
    """Check if object contains denied keywords - ONLY checks top-level keys"""
    if isinstance(obj, dict):
        for key in obj.keys():
            if key in KEYWORD_DENYLIST:
                return True
    return False


def deep_merge(base, updates):
    """
    Recursively merge updates into base dictionary.
    VULNERABLE: This merges nested objects without checking denylist recursively.
    Similar to prototype pollution in JavaScript where __proto__ can bypass checks.
    """
    result = copy.deepcopy(base)
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# Route for main page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))


# Route for dashboard page
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    configs = ConfigStore.query.filter_by(owner_id=user_id).all()
    return render_template('dashboard.html', user=user, configs=configs)


# API: List available config schemas
@app.route('/api/schemas', methods=['GET'])
def list_schemas():
    return jsonify({
        'schemas': [
            {'name': 'app_settings', 'description': 'Application settings configuration'},
            {'name': 'network_config', 'description': 'Network and connectivity settings'},
            {'name': 'user_preferences', 'description': 'User preference configuration'},
            {'name': 'storage_config', 'description': 'Storage and backup settings'}
        ]
    })


# API: Get user's config
@app.route('/api/config/<config_name>', methods=['GET'])
def get_config(config_name):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    config = ConfigStore.query.filter_by(owner_id=user_id, config_name=config_name).first()
    if not config:
        return jsonify({'error': 'Config not found'}), 404
    
    return jsonify({'config_name': config_name, 'data': json.loads(config.config_data)})


# API: Update config with merge operation
@app.route('/api/config/<config_name>/merge', methods=['POST'])
def merge_config(config_name):
    """
    Merge provided JSON data into existing configuration.
    Uses keyword denylist to prevent setting sensitive fields.
    
    VULNERABILITY: The denylist only checks top-level keys.
    Attackers can bypass it by nesting denied keys inside objects,
    similar to JavaScript prototype pollution where __proto__ can 
    be nested to bypass security checks.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        updates = request.get_json()
        if not updates:
            return jsonify({'error': 'No JSON data provided'}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format'}), 400
    
    # Security check: deny certain keywords (FLAWED - only checks top-level)
    if contains_denied_keyword(updates):
        return jsonify({'error': 'Denied keyword detected in configuration update'}), 403
    
    config = ConfigStore.query.filter_by(owner_id=user_id, config_name=config_name).first()
    if not config:
        return jsonify({'error': 'Config not found'}), 404
    
    current_data = json.loads(config.config_data)
    
    # Perform deep merge (VULNERABLE: nested keys bypass the denylist check)
    merged_data = deep_merge(current_data, updates)
    
    config.config_data = json.dumps(merged_data)
    db.session.commit()
    
    return jsonify({'status': 'success', 'config_name': config_name, 'data': merged_data})


# API: Create new config
@app.route('/api/config', methods=['POST'])
def create_config():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        config_name = data.get('config_name')
        config_data = data.get('data', {})
    except:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    if not config_name:
        return jsonify({'error': 'config_name is required'}), 400
    
    if contains_denied_keyword(config_data):
        return jsonify({'error': 'Denied keyword detected'}), 403
    
    existing = ConfigStore.query.filter_by(owner_id=user_id, config_name=config_name).first()
    if existing:
        return jsonify({'error': 'Config already exists'}), 409
    
    new_config = ConfigStore(
        owner_id=user_id,
        config_name=config_name,
        config_data=json.dumps(config_data)
    )
    db.session.add(new_config)
    db.session.commit()
    
    return jsonify({'status': 'created', 'config_name': config_name}), 201


# API: View system info (debug endpoint, limited access)
@app.route('/api/system/info', methods=['GET'])
def system_info():
    return jsonify({
        'version': '2.4.1',
        'api_version': 'v1',
        'features': ['config_merge', 'schema_validation', 'audit_logging'],
        'documentation': '/docs'
    })


# API: Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'database': 'connected'})


# API: Get admin secrets - requires is_admin flag in user's config
@app.route('/api/admin/secrets', methods=['GET'])
def admin_secrets():
    """
    Admin-only endpoint to retrieve system secrets.
    Checks for is_admin flag in user's app_settings config.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check if user has admin privileges by looking at their app_settings
    user_config = ConfigStore.query.filter_by(owner_id=user_id, config_name='app_settings').first()
    if not user_config:
        return jsonify({'error': 'User configuration not found'}), 404
    
    config_data = json.loads(user_config.config_data)
    
    # Check for admin privileges - look for is_admin in settings or permissions
    is_admin = False
    if config_data.get('is_admin') == True:
        is_admin = True
    elif config_data.get('settings', {}).get('is_admin') == True:
        is_admin = True
    elif config_data.get('permissions', {}).get('is_admin') == True:
        is_admin = True
    elif config_data.get('user', {}).get('is_admin') == True:
        is_admin = True
    
    if not is_admin:
        return jsonify({'error': 'Admin privileges required', 'hint': 'is_admin flag must be set'}), 403
    
    # User has admin privileges - return the flag
    system_config = ConfigStore.query.filter_by(config_name='system_secrets').first()
    if system_config:
        secrets = json.loads(system_config.config_data)
        return jsonify({
            'status': 'success',
            'secrets': {
                'internal_flag': secrets.get('internal_flag', 'N/A')
            }
        })
    
    return jsonify({'error': 'System secrets not configured'}), 500


# API: List all configs (admin only)
@app.route('/api/admin/configs', methods=['GET'])
def list_all_configs():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_config = ConfigStore.query.filter_by(owner_id=user_id, config_name='app_settings').first()
    if not user_config:
        return jsonify({'error': 'Access denied'}), 403
    
    config_data = json.loads(user_config.config_data)
    is_admin = (config_data.get('is_admin') == True or 
                config_data.get('settings', {}).get('is_admin') == True or
                config_data.get('permissions', {}).get('is_admin') == True or
                config_data.get('user', {}).get('is_admin') == True)
    
    if not is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    configs = ConfigStore.query.all()
    return jsonify({
        'configs': [{'id': c.id, 'owner_id': c.owner_id, 'name': c.config_name} for c in configs]
    })


# Documentation page
@app.route('/docs')
def docs():
    return render_template('docs.html')


# Serve robots.txt
@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')
