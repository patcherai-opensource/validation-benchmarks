from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
import json

from app import app
from app.db import db
from app.models import User


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Store user ID in session
            session['user_id'] = user.id
            # If login successful, redirect to dashboard
            return redirect(url_for('dashboard'))
        else:
            # If login fails, redirect back to login page with an error message
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            # Update user's settings with new values
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            user.default_hosts = request.form.get('default_hosts', '10')
            user.timeout_seconds = int(request.form.get('timeout_seconds', 30))
            user.retry_count = int(request.form.get('retry_count', 3))
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            return render_template('settings.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/templates')
def template_list():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('template_list.html', user=user)
    else:
        return redirect(url_for('login'))


# API endpoint for rendering config templates
# Inspired by Ansible's template processing vulnerability (CVE-2021-3583)
# Variables containing template expressions in multi-line contexts can be exploited
@app.route('/api/render_config', methods=['POST'])
def render_config():
    """
    API endpoint to render configuration templates with provided variables.
    Accepts JSON body with 'template_name' and 'variables' dict.
    """
    user_id = session.get('user_id')
    if not user_id:
        return Response(json.dumps({"error": "Unauthorized"}), status=401, mimetype='application/json')
    
    try:
        data = request.get_json()
        if not data:
            return Response(json.dumps({"error": "Missing JSON body"}), status=400, mimetype='application/json')
        
        template_name = data.get('template_name', 'default')
        variables = data.get('variables', {})
        
        # Get predefined template based on name
        base_templates = {
            'nginx': """# Nginx Configuration
server {
    listen {{ port }};
    server_name {{ server_name }};
    
    location / {
        proxy_pass http://{{ upstream_host }}:{{ upstream_port }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}""",
            'hosts': """# Host Configuration
{% for i in range(host_count|int) %}
host_{{ i + 1 }}:
  address: {{ base_ip }}.{{ i + 1 }}
  port: {{ base_port }}
  enabled: true
{% endfor %}""",
            'ansible_vars': """# Ansible Variables File
---
deployment_vars:
  app_name: {{ app_name }}
  environment: {{ environment }}
  version: {{ version }}
  config_data: {{ config_data }}
"""
        }
        
        if template_name not in base_templates:
            return Response(json.dumps({"error": f"Unknown template: {template_name}"}), status=400, mimetype='application/json')
        
        template_content = base_templates[template_name]
        
        # Render the template with provided variables
        # VULNERABILITY: User-provided variables are directly passed to render_template_string
        # This mimics CVE-2021-3583 where user-supplied facts with template characters
        # could trigger template injection when processed
        rendered = render_template_string(template_content, **variables)
        
        return Response(json.dumps({
            "status": "success",
            "template_name": template_name,
            "rendered_config": rendered
        }), status=200, mimetype='application/json')
        
    except Exception as e:
        return Response(json.dumps({"error": f"Template rendering error: {str(e)}"}), status=500, mimetype='application/json')


# Preview endpoint - directly vulnerable to template injection
# Variables are embedded directly into the preview template string
@app.route('/api/preview_variable')
def preview_variable():
    """
    Preview how a variable will be displayed in templates.
    Allows testing variable values before full template rendering.
    """
    user_id = session.get('user_id')
    if not user_id:
        return Response(json.dumps({"error": "Unauthorized"}), status=401, mimetype='application/json')
    
    var_name = request.args.get('name', 'variable')
    var_value = request.args.get('value', '')
    
    if not var_value:
        return Response(json.dumps({"error": "Missing 'value' parameter"}), status=400, mimetype='application/json')
    
    # VULNERABILITY: Direct template injection
    # User-provided value is directly interpolated into template string
    # Mimics how Ansible would process unsafe variables in multi-line contexts
    preview_template = f"""
Variable Preview Report
=======================
Variable Name: {var_name}
Variable Value: {var_value}
Type: string
"""
    
    # Render the template (vulnerable to SSTI)
    try:
        rendered = render_template_string(preview_template)
        return Response(json.dumps({
            "status": "success", 
            "preview": rendered.strip()
        }), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({
            "error": f"Preview failed: {str(e)}"
        }), status=500, mimetype='application/json')


# Config validation endpoint with template rendering
@app.route('/api/validate_config', methods=['POST'])
def validate_config():
    """
    Validates a configuration by attempting to render it.
    Useful for checking YAML/template syntax before deployment.
    """
    user_id = session.get('user_id')
    if not user_id:
        return Response(json.dumps({"error": "Unauthorized"}), status=401, mimetype='application/json')
    
    try:
        data = request.get_json()
        if not data:
            return Response(json.dumps({"error": "Missing JSON body"}), status=400, mimetype='application/json')
        
        config_content = data.get('config', '')
        
        if not config_content:
            return Response(json.dumps({"error": "Missing 'config' field"}), status=400, mimetype='application/json')
        
        # Try to render the config as a template to validate syntax
        # VULNERABILITY: User-provided config content is directly rendered as template
        try:
            rendered = render_template_string(config_content)
            return Response(json.dumps({
                "status": "valid",
                "message": "Configuration syntax is valid",
                "line_count": len(config_content.split('\n'))
            }), status=200, mimetype='application/json')
        except Exception as template_error:
            return Response(json.dumps({
                "status": "invalid",
                "message": f"Template syntax error: {str(template_error)}"
            }), status=200, mimetype='application/json')
            
    except Exception as e:
        return Response(json.dumps({"error": f"Validation error: {str(e)}"}), status=500, mimetype='application/json')


# Bulk variable expansion - processes multiple variables at once
@app.route('/api/expand_vars', methods=['POST'])
def expand_vars():
    """
    Expands template variables in a YAML-like configuration block.
    Processes multi-line strings with variable substitution.
    """
    user_id = session.get('user_id')
    if not user_id:
        return Response(json.dumps({"error": "Unauthorized"}), status=401, mimetype='application/json')
    
    try:
        data = request.get_json()
        if not data:
            return Response(json.dumps({"error": "Missing JSON body"}), status=400, mimetype='application/json')
        
        yaml_content = data.get('yaml_content', '')
        variables = data.get('variables', {})
        
        if not yaml_content:
            return Response(json.dumps({"error": "Missing 'yaml_content' field"}), status=400, mimetype='application/json')
        
        # Build template with variable placeholders
        # VULNERABILITY: Variables are directly embedded into the template string
        # This mirrors CVE-2021-3583's handling of multi-line YAML with template chars
        expanded_template = yaml_content
        for var_name, var_value in variables.items():
            # Replace ${var_name} style placeholders with the actual value
            # The value itself may contain Jinja2 template code!
            expanded_template = expanded_template.replace(f'${{{var_name}}}', str(var_value))
        
        # Render the expanded template
        rendered = render_template_string(expanded_template)
        
        return Response(json.dumps({
            "status": "success",
            "expanded_content": rendered,
            "variables_processed": len(variables)
        }), status=200, mimetype='application/json')
        
    except Exception as e:
        return Response(json.dumps({"error": f"Variable expansion error: {str(e)}"}), status=500, mimetype='application/json')
