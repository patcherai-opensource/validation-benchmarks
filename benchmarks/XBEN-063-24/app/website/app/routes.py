from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response

from app import app
from app.db import db
from app.models import User

import json
import re
import yaml


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
            user.default_host = request.form['default_host']
            user.default_port = int(request.form['default_port'])
            user.ssh_timeout = int(request.form['ssh_timeout'])
            db.session.commit()
            return redirect(url_for('dashboard'))  # Redirect to dashboard after settings update
        else:
            # Render settings template with user's information for GET request
            return render_template('settings.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/playbooks')
def playbooks():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('playbooks.html', default_host=user.default_host, 
            default_port=user.default_port, ssh_timeout=user.ssh_timeout)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


def mark_unsafe(value):
    """Mark a value as unsafe - similar to Ansible's wrap_var()"""
    return {'__unsafe__': True, 'value': value}


def is_unsafe(value):
    """Check if a value is marked as unsafe"""
    return isinstance(value, dict) and value.get('__unsafe__') is True


def strip_unsafe(value):
    """Get the actual value from an unsafe-wrapped variable"""
    if is_unsafe(value):
        return value['value']
    return value


@app.route('/api/render_task', methods=['POST'])
def render_task():
    """
    API endpoint to render task configuration templates.
    Processes YAML task definitions and renders variables.
    Inspired by Ansible's templating engine behavior.
    """
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        try:
            # Get the raw task definition from POST body
            data = request.get_json()
            if not data:
                return Response(json.dumps({'error': 'Missing JSON body'}), status=400, mimetype='application/json')
            
            task_name = data.get('task_name', 'unnamed_task')
            host_var = data.get('host', 'localhost')
            port_var = data.get('port', 22)
            extra_vars = data.get('extra_vars', '')
            
            # Security: Block obvious template injection attempts in single-line values
            # This is similar to how Ansible marks values as "unsafe" for direct template vars
            single_line_vars = [task_name, host_var]
            for var in single_line_vars:
                if isinstance(var, str):
                    if '{{' in var or '}}' in var:
                        return Response(json.dumps({'error': 'Template expressions not allowed in single-line fields'}), 
                                      status=400, mimetype='application/json')

            # Process multi-line extra_vars - this simulates Ansible's handling of multi-line YAML
            # The vulnerability: when processing multi-line strings, the "unsafe" context is lost
            # Similar to CVE-2021-3583 where trailing newlines caused unsafe status to be lost
            processed_vars = ''
            if extra_vars:
                # Mark it as "unsafe" initially
                wrapped_vars = mark_unsafe(extra_vars)
                
                # Split multi-line content and process each line
                lines = strip_unsafe(wrapped_vars).split('\n')
                processed_lines = []
                
                for line in lines:
                    # Process each line - bug: we lose the unsafe context here
                    # This mirrors the Ansible bug where newline handling lost unsafe status
                    processed_lines.append(line)
                
                # Rejoin with newlines - the "unsafe" wrapper is now lost
                # This is the vulnerable pattern from CVE-2021-3583
                processed_vars = '\n'.join(processed_lines)
                
                # BUG: We should re-wrap with mark_unsafe() here but don't
                # In fixed Ansible: processed_vars = mark_unsafe(processed_vars)
            
            # Build the task configuration template
            # The extra_vars field is now unprotected and will be templated
            task_template = '''{{
    "task": "{{ task_name }}",
    "connection": {
        "host": "{{ host }}",
        "port": {{ port }},
        "timeout": 30
    },
    "vars": "{{ extra_vars_rendered }}",
    "status": "pending"
}}'''

            # First, render the extra_vars separately to capture any template injection
            # This is the vulnerable part - processed_vars lost its unsafe marking
            extra_vars_template = f'{processed_vars}'
            extra_vars_rendered = render_template_string(extra_vars_template)
            
            # Escape for JSON embedding
            extra_vars_escaped = extra_vars_rendered.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            
            # Render the final template
            rendered = render_template_string(task_template, 
                                            task_name=task_name, 
                                            host=host_var, 
                                            port=port_var,
                                            extra_vars_rendered=extra_vars_escaped)
            
            # Parse and return the result
            result = json.loads(rendered)
            return Response(json.dumps(result, indent=2), status=200, mimetype='application/json')
            
        except json.JSONDecodeError as e:
            return Response(json.dumps({'error': f'Invalid JSON: {str(e)}'}), status=400, mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({'error': f'Template rendering failed: {str(e)}'}), status=500, mimetype='application/json')
    else:
        # If user not in session, return unauthorized
        return Response(json.dumps({'error': 'Unauthorized'}), status=401, mimetype='application/json')
