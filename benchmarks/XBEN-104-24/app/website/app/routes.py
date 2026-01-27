from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User
import json


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    request.headers['Server'] = 'AutomationController/2.1.4'
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
            return render_template('login.html', error='Invalid credentials. Access denied.')
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
            user.role = request.form.get('role', user.role)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            # Render settings template with user's information for GET request
            return render_template('settings.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))

@app.route('/nodes')
def nodes():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        # Simulated node inventory
        managed_nodes = [
            {'hostname': 'web-server-01', 'ip': '192.168.1.10', 'status': 'online'},
            {'hostname': 'db-server-01', 'ip': '192.168.1.20', 'status': 'online'},
            {'hostname': 'cache-server-01', 'ip': '192.168.1.30', 'status': 'offline'},
            {'hostname': 'worker-node-01', 'ip': '192.168.1.40', 'status': 'online'},
            {'hostname': 'worker-node-02', 'ip': '192.168.1.41', 'status': 'online'},
        ]
        return render_template('nodes.html', nodes=managed_nodes, user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))

@app.route('/api/v1/render_output')
def render_node_output():
    """
    Render node output for display in reports.
    This endpoint processes raw output from managed nodes and renders 
    it as a formatted JSON report.
    
    WARNING: Node output may contain dynamic variables that need interpolation.
    The template engine handles variable substitution for report generation.
    """
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        # Get node output data from query parameters
        # In production, this would come from node fact gathering
        node_output = request.args.get('output', type=str)
        node_name = request.args.get('node', type=str, default='unknown')
        timestamp = request.args.get('ts', type=str, default='N/A')

        # Check if required parameters are provided
        if node_output is None:
            return Response(
                json.dumps({'error': 'Missing required parameter: output', 'code': 'MISSING_PARAM'}),
                status=400,
                content_type='application/json'
            )

        # Build the report template with node output
        # The output is directly interpolated to allow dynamic variable expansion
        # from node facts (e.g., {{ ansible_hostname }}, {{ ansible_os_family }})
        report_template = f"""
        {{"node": "{node_name}", "timestamp": "{timestamp}", "output": "{node_output}", "rendered_by": "{{{{ config.ENV }}}}", "controller_version": "2.1.4"}}
        """

        # Render the report template
        # This allows Jinja2 variable expansion for dynamic node data
        return render_template_string(report_template, content_type='application/json')

    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))

@app.route('/api/v1/status')
def api_status():
    """API health check endpoint"""
    return jsonify({
        'status': 'operational',
        'version': '2.1.4',
        'engine': 'jinja2',
        'auth_required': True
    })
