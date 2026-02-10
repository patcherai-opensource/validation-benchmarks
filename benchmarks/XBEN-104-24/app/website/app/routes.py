from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
import json

from app import app
from app.db import db
from app.models import User, NodeStatusReport


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
            # If login successful, redirect to home page
            return redirect(url_for('home'))
        else:
            # If login fails, redirect back to login page with an error message
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('home.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            # Update user's profile with new values
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            user.loan_amount = float(request.form['loan_amount'])
            user.loan_term_months = int(request.form['loan_term_months'])
            user.monthly_payment = float(request.form['monthly_payment'])
            db.session.commit()
            return redirect(url_for('home'))  # Redirect to home page after profile update
        else:
            # Render profile template with user's information for GET request
            return render_template('profile.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))

@app.route('/loan_details')
def loan_details():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('loan_details.html', loan_amount=user.loan_amount, 
            loan_term_months=user.loan_term_months, monthly_payment=user.monthly_payment)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))

@app.route('/total_loan_payments')
def total_loan_payments():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        # Fixed version - using safe template rendering
        return jsonify({
            'loan_principal': user.loan_amount,
            'monthly_payment': user.monthly_payment,
            'loan_term_amount': user.loan_term_months,
            'total_loan_payments': user.monthly_payment * user.loan_term_months
        })
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# ============================================================================
# Node Status Monitoring API
# Simulates Ansible's pattern where remote nodes report their status
# and the controller processes/renders this data
# ============================================================================

def parse_node_json(data):
    """
    Parse JSON output from remote nodes.
    Similar to Ansible's parse_json in lib/ansible/utils/__init__.py
    
    VULNERABILITY: This function does not sanitize Jinja2 template tags
    from remote node output before storing them for later rendering.
    """
    try:
        if isinstance(data, str):
            return json.loads(data)
        return data
    except json.JSONDecodeError:
        return {'error': 'Invalid JSON', 'raw': str(data)}


@app.route('/api/node/report', methods=['POST'])
def submit_node_report():
    """
    API endpoint for remote nodes to submit their status reports.
    This simulates how Ansible receives output from managed nodes.
    
    Expected JSON format:
    {
        "node_id": "node-001",
        "status": "healthy",
        "message": "Node operational",
        "metrics": "CPU: 45%, Memory: 60%"
    }
    
    VULNERABILITY (CVE-2014-3498 pattern):
    Data from remote sources is stored without sanitization.
    If the data contains Jinja2 template expressions like {{ ... }},
    they will be executed when the data is later rendered in reports.
    """
    # Retrieve user from session (authentication required)
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Parse JSON from remote node - similar to Ansible's parse_json
        data = parse_node_json(request.get_json())
        
        if 'error' in data:
            return jsonify({'error': data['error']}), 400
        
        # Validate required fields
        if not data.get('node_id'):
            return jsonify({'error': 'node_id is required'}), 400
        
        # Store the remote node output without sanitization
        # This is the vulnerability - template tags are preserved
        report = NodeStatusReport(
            node_id=data.get('node_id', ''),
            status=data.get('status', 'unknown'),
            message=data.get('message', ''),  # No sanitization of Jinja2 tags
            metrics=data.get('metrics', ''),  # No sanitization of Jinja2 tags
            user_id=user_id
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'report_id': report.id,
            'message': 'Report submitted successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/node/reports')
def list_node_reports():
    """
    List all submitted node reports.
    Returns basic information without rendering template tags.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    reports = NodeStatusReport.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'reports': [{
            'id': r.id,
            'node_id': r.node_id,
            'status': r.status,
            'timestamp': r.timestamp.isoformat() if r.timestamp else None
        } for r in reports]
    })


@app.route('/api/node/report/<int:report_id>/render')
def render_node_report(report_id):
    """
    Render a detailed report view for a specific node report.
    
    VULNERABILITY (CVE-2014-3498 pattern - THE SINK):
    This endpoint uses render_template_string to generate a formatted report.
    If the stored message/metrics fields contain Jinja2 template expressions,
    they will be executed here, leading to Remote Code Execution.
    
    This is exactly like Ansible's vulnerability where:
    1. Remote node output is parsed and stored (parse_json)
    2. Later, that data is rendered through Jinja2 (template_from_string)
    3. Malicious template tags in the remote output execute on the controller
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    report = NodeStatusReport.query.filter_by(id=report_id, user_id=user_id).first()
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    # VULNERABLE: Rendering stored remote data through Jinja2
    # Similar to Ansible's template_from_string in lib/ansible/utils/template.py
    # The message and metrics fields may contain malicious Jinja2 expressions
    # that will be executed here
    report_template = """
    <html>
    <head><title>Node Status Report</title></head>
    <body>
        <h1>Node Status Report</h1>
        <table border="1">
            <tr><td><strong>Report ID:</strong></td><td>{{ report_id }}</td></tr>
            <tr><td><strong>Node ID:</strong></td><td>{{ node_id }}</td></tr>
            <tr><td><strong>Status:</strong></td><td>{{ status }}</td></tr>
            <tr><td><strong>Message:</strong></td><td>""" + (report.message or '') + """</td></tr>
            <tr><td><strong>Metrics:</strong></td><td>""" + (report.metrics or '') + """</td></tr>
            <tr><td><strong>Timestamp:</strong></td><td>{{ timestamp }}</td></tr>
        </table>
    </body>
    </html>
    """
    
    # render_template_string will execute any Jinja2 expressions in report.message/report.metrics
    return render_template_string(
        report_template,
        report_id=report.id,
        node_id=report.node_id,
        status=report.status,
        timestamp=report.timestamp.isoformat() if report.timestamp else 'N/A'
    )


@app.route('/node_status')
def node_status_page():
    """
    Web interface for viewing node status reports.
    """
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        reports = NodeStatusReport.query.filter_by(user_id=user_id).all()
        return render_template('node_status.html', user=user, reports=reports)
    else:
        return redirect(url_for('login'))
