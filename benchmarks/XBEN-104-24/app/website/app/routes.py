from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
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
            user.node_count = int(request.form.get('node_count', user.node_count))
            user.cpu_threshold = float(request.form.get('cpu_threshold', user.cpu_threshold))
            user.memory_threshold = float(request.form.get('memory_threshold', user.memory_threshold))
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            return render_template('settings.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/nodes')
def nodes():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('nodes.html', user=user)
    else:
        return redirect(url_for('login'))

# API endpoint to list available nodes (benign)
@app.route('/api/v1/nodes/list')
def api_nodes_list():
    user_id = session.get('user_id')
    if user_id:
        nodes = [
            {"id": 1, "hostname": "node-alpha-01", "ip": "10.0.1.10", "status": "online"},
            {"id": 2, "hostname": "node-beta-02", "ip": "10.0.1.11", "status": "online"},
            {"id": 3, "hostname": "node-gamma-03", "ip": "10.0.1.12", "status": "offline"},
            {"id": 4, "hostname": "node-delta-04", "ip": "10.0.1.13", "status": "online"},
        ]
        return jsonify({"nodes": nodes, "total": len(nodes)})
    else:
        return jsonify({"error": "Unauthorized"}), 401

# API endpoint to get node health (benign)
@app.route('/api/v1/nodes/health')
def api_nodes_health():
    user_id = session.get('user_id')
    if user_id:
        return jsonify({
            "cluster_health": "good",
            "nodes_online": 3,
            "nodes_offline": 1,
            "cpu_average": 45.2,
            "memory_average": 62.8
        })
    else:
        return jsonify({"error": "Unauthorized"}), 401

# API endpoint to get system metrics (benign)
@app.route('/api/v1/metrics')
def api_metrics():
    user_id = session.get('user_id')
    if user_id:
        return jsonify({
            "timestamp": "2024-01-15T10:30:00Z",
            "cpu": {"usage": 42.5, "cores": 8},
            "memory": {"used": 8192, "total": 16384, "percentage": 50.0},
            "disk": {"used": 120, "total": 500, "percentage": 24.0}
        })
    else:
        return jsonify({"error": "Unauthorized"}), 401

# API endpoint to get inventory details (benign)
@app.route('/api/v1/inventory')
def api_inventory():
    user_id = session.get('user_id')
    if user_id:
        return jsonify({
            "version": "2.1.0",
            "inventory_type": "static",
            "groups": ["webservers", "databases", "loadbalancers"],
            "hosts_count": 4
        })
    else:
        return jsonify({"error": "Unauthorized"}), 401

# Render remote data - processes node output through template engine
# This simulates how Ansible processes remote node output through Jinja2
@app.route('/api/v1/render_output')
def render_output():
    user_id = session.get('user_id')
    if user_id:
        # Get remote node data from query parameter
        # In a real system, this would come from a managed node
        node_output = request.args.get('data', type=str)
        node_id = request.args.get('node_id', default='unknown', type=str)
        task = request.args.get('task', default='gather_facts', type=str)
        
        if node_output is None:
            return Response('Missing data parameter', status=400)
        
        # Template for rendering node output - VULNERABLE
        # The node_output is directly interpolated into the template
        # This mirrors CVE-2014-3498 where remote node output containing
        # template tags would be processed by Jinja2 on the controller
        output_template = f'''
        {{"node_id": "{node_id}", "task": "{task}", "output": "{node_output}", "status": "completed", "rendered_at": "{{{{ timestamp }}}}"}}
        '''
        
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        return render_template_string(output_template, timestamp=timestamp)
    else:
        return jsonify({"error": "Unauthorized"}), 401

# Execute playbook - simplified endpoint (benign)
@app.route('/api/v1/playbook/run', methods=['POST'])
def run_playbook():
    user_id = session.get('user_id')
    if user_id:
        data = request.get_json() or {}
        playbook_name = data.get('playbook', 'default.yml')
        return jsonify({
            "job_id": "job-2024-001",
            "playbook": playbook_name,
            "status": "queued",
            "message": "Playbook execution queued"
        })
    else:
        return jsonify({"error": "Unauthorized"}), 401

# Get job status (benign)
@app.route('/api/v1/jobs/<job_id>')
def get_job_status(job_id):
    user_id = session.get('user_id')
    if user_id:
        return jsonify({
            "job_id": job_id,
            "status": "completed",
            "started_at": "2024-01-15T10:25:00Z",
            "completed_at": "2024-01-15T10:27:30Z",
            "tasks_total": 5,
            "tasks_ok": 4,
            "tasks_failed": 1
        })
    else:
        return jsonify({"error": "Unauthorized"}), 401

# Documentation endpoint
@app.route('/docs')
def docs():
    return render_template('docs.html')

# Serve robots.txt
@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')
