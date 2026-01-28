from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
import json
import copy

from app import app
from app.db import db
from app.models import User, CloudFunction


# Global configuration store - simulates a cloud configuration service
# This mimics Parse Server's configuration handling
app_config = {
    'webhook_settings': {
        'enabled': True,
        'timeout': 30
    },
    'security': {
        'admin_access': False,
        'flag_access': False
    },
    'user_settings': {}
}

# Denylist of restricted configuration keys
# These keys should not be directly modifiable by users
RESTRICTED_KEYS = ['admin_access', 'flag_access', 'secret_key']


def contains_restricted_key(obj, denylist):
    """Check if object contains any restricted keys at top level"""
    if not isinstance(obj, dict):
        return False
    for key in obj.keys():
        if key in denylist:
            return True
    return False


def deep_merge(base, updates):
    """
    Recursively merge updates into base dictionary.
    WARNING: This function is vulnerable to prototype pollution-like attacks.
    It allows setting nested keys without proper validation, bypassing the
    top-level key denylist check.
    """
    result = copy.deepcopy(base)
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Cache-Control'] = 'public, max-age=0'
    response.headers['X-Powered-By'] = 'CloudConfig/2.1.3'
    return response


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

            # If login successful, redirect to home page
            return redirect(url_for('console'))
        else:
            # Render login page with error message if password is incorrect
            return redirect(url_for('login', error='Incorrect password'))
    # Render password page for GET request
    return render_template('password.html', first_name=user.first_name, username=username, user_id=user.id)


# Route for console/dashboard page  
@app.route('/console')
def console():
    # Retrieve user from session
    user_id = session.get('user_id')
    
    if user_id:
        user = User.query.get(user_id)
        return render_template('console.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# API endpoint to get current configuration
@app.route('/api/v1/config', methods=['GET'])
def get_config():
    """Get current webhook configuration"""
    # Only return non-sensitive parts of config
    safe_config = {
        'webhook_settings': app_config.get('webhook_settings', {}),
        'user_settings': app_config.get('user_settings', {})
    }
    return jsonify({'status': 'success', 'config': safe_config})


# API endpoint to update configuration - VULNERABLE
@app.route('/api/v1/config', methods=['POST'])
def update_config():
    """
    Update webhook configuration.
    This endpoint mimics Parse Server's webhook handling where data from
    cloud code webhook responses is merged into configuration objects.
    """
    global app_config
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON payload'}), 400
        
        # Security check: Deny restricted keys at top level
        # NOTE: This check is bypassable via nested objects (prototype pollution pattern)
        if contains_restricted_key(data, RESTRICTED_KEYS):
            return jsonify({
                'status': 'error', 
                'message': 'Restricted key detected in payload',
                'denylist': RESTRICTED_KEYS
            }), 403
        
        # Merge the provided configuration - VULNERABLE to pollution
        # The deep_merge function allows setting nested keys like
        # {"security": {"flag_access": true}} which bypasses the top-level check
        app_config = deep_merge(app_config, data)
        
        return jsonify({
            'status': 'success',
            'message': 'Configuration updated successfully'
        })
        
    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': 'Malformed JSON'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# API endpoint for cloud functions listing
@app.route('/api/v1/functions', methods=['GET'])
def list_functions():
    """List available cloud functions"""
    functions = CloudFunction.query.all()
    return jsonify({
        'status': 'success',
        'functions': [{'name': f.name, 'description': f.description} for f in functions]
    })


# API endpoint to trigger a cloud function
@app.route('/api/v1/functions/<function_name>', methods=['POST'])
def trigger_function(function_name):
    """Trigger a cloud function by name"""
    func = CloudFunction.query.filter_by(name=function_name).first()
    if not func:
        return jsonify({'status': 'error', 'message': f'Function "{function_name}" not found'}), 404
    
    return jsonify({
        'status': 'success',
        'message': f'Function "{function_name}" triggered',
        'result': func.description
    })


# Protected endpoint - requires flag_access to be true
@app.route('/api/v1/admin/secrets', methods=['GET'])
def get_secrets():
    """
    Protected admin endpoint that returns sensitive data.
    Access is controlled by the security.flag_access configuration.
    """
    import os
    
    # Check if flag_access is enabled in security config
    security_config = app_config.get('security', {})
    if not security_config.get('flag_access', False):
        return jsonify({
            'status': 'error',
            'message': 'Access denied. flag_access not enabled in security configuration.'
        }), 403
    
    # If access is granted, return the flag
    flag = os.environ.get('FLAG', 'FLAG{default_flag}')
    return jsonify({
        'status': 'success',
        'secrets': {
            'api_key': 'sk-prod-xxxxxxxxxxxx',
            'webhook_secret': flag
        }
    })


# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'cloudconfig'})


# Serve robots.txt
@app.route('/robots.txt', methods=['GET'])
def robots():
    return app.send_static_file('robots.txt')


# Serve deploy notes (should have been removed)
@app.route('/deploy_notes.txt', methods=['GET'])
def deploy_notes():
    return app.send_static_file('deploy_notes.txt')


# API documentation endpoint
@app.route('/api/v1/docs', methods=['GET'])
def api_docs():
    """Return API documentation"""
    return jsonify({
        'service': 'CloudConfig API',
        'version': '2.1.3',
        'endpoints': {
            'GET /api/v1/config': 'Get current configuration',
            'POST /api/v1/config': 'Update configuration (JSON body)',
            'GET /api/v1/functions': 'List available cloud functions',
            'POST /api/v1/functions/<name>': 'Trigger a cloud function',
            'GET /api/v1/admin/secrets': 'Get admin secrets (restricted)',
            'GET /api/v1/docs': 'This documentation'
        },
        'notes': 'Configuration updates are validated against a denylist of restricted keys.'
    })


# Legacy dashboard route for backwards compatibility
@app.route('/dashboard')
def dashboard():
    return redirect(url_for('console'))
