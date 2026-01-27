from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
import json
import copy

from app import app
from app.db import db
from app.models import User


# Global configuration store - simulates a shared config object
# This mimics how Parse Server stores configuration that can be polluted
app_config = {
    'user_settings': {},
    'system': {
        'debug': False,
        'version': '1.2.0'
    },
    'access_level': 'user'
}


def deep_merge(base, updates, path=""):
    """
    Recursively merge updates into base dict.
    VULNERABLE: Does not properly validate keys, allowing prototype-like pollution.
    This mimics JavaScript's vulnerable object merging that allows __proto__ pollution.
    """
    if not isinstance(updates, dict):
        return updates
    
    result = copy.copy(base) if isinstance(base, dict) else {}
    
    for key, value in updates.items():
        # VULNERABLE: Allow special keys that can pollute parent objects
        # This is analogous to JavaScript prototype pollution via __proto__
        if key == '__parent__':
            # Pollution vector: merge into parent scope
            if isinstance(value, dict):
                for pkey, pval in value.items():
                    result[pkey] = pval
        elif key == '__override__':
            # Pollution vector: direct override of restricted keys
            if isinstance(value, dict):
                result.update(value)
        elif isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = deep_merge(result[key], value, f"{path}.{key}")
        else:
            result[key] = value
    
    return result


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'CloudConfig/1.2.0'
    return response


# Landing page
@app.route('/')
def index():
    return render_template('index.html')


# API documentation endpoint
@app.route('/api')
def api_docs():
    return render_template('api_docs.html')


# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('console'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Main console/dashboard
@app.route('/console')
def console():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('console.html', user=user, config=app_config)


# API: Get current configuration
@app.route('/api/config', methods=['GET'])
def get_config():
    """Returns the current configuration (excluding sensitive data)"""
    # Check if user has admin access via the config
    if app_config.get('access_level') == 'admin':
        return jsonify({
            'status': 'success',
            'config': app_config,
            'admin_data': app_config.get('admin_secrets', {})
        })
    
    # Regular users only see safe config
    safe_config = {
        'user_settings': app_config.get('user_settings', {}),
        'system': app_config.get('system', {}),
        'access_level': app_config.get('access_level', 'user')
    }
    return jsonify({
        'status': 'success',
        'config': safe_config
    })


# API: Update configuration - VULNERABLE ENDPOINT
@app.route('/api/config', methods=['POST'])
def update_config():
    """
    Update user configuration.
    
    Expected JSON format:
    {
        "user_settings": {
            "theme": "dark",
            "notifications": true
        }
    }
    
    Note: System settings and admin areas are protected.
    """
    global app_config
    
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Content-Type must be application/json'
        }), 400
    
    try:
        updates = request.get_json()
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': f'Invalid JSON: {str(e)}'
        }), 400
    
    if not isinstance(updates, dict):
        return jsonify({
            'status': 'error',
            'message': 'Request body must be a JSON object'
        }), 400
    
    # VULNERABLE: The denylist check can be bypassed via __parent__ or __override__ keys
    # This mimics the Parse Server vulnerability where prototype pollution bypasses keyword denylist
    denylist = ['admin_secrets', 'access_level', 'system']
    
    for key in updates.keys():
        if key in denylist:
            return jsonify({
                'status': 'error',
                'message': f'Cannot modify restricted key: {key}'
            }), 403
    
    # VULNERABLE: deep_merge allows pollution via __parent__ and __override__
    # Similar to how Parse Server's _expandResultOnKeyPath was vulnerable
    app_config = deep_merge(app_config, updates)
    
    return jsonify({
        'status': 'success',
        'message': 'Configuration updated',
        'config': {
            'user_settings': app_config.get('user_settings', {}),
            'system': app_config.get('system', {})
        }
    })


# API: Check access level
@app.route('/api/access')
def check_access():
    """Check current access level"""
    level = app_config.get('access_level', 'user')
    return jsonify({
        'status': 'success',
        'access_level': level,
        'is_admin': level == 'admin'
    })


# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})
