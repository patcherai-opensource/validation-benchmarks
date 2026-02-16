from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import Operator, ManagedNode, TaskResult, NodeFact
from datetime import datetime

import hashlib
import json


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Server'] = 'NodePilot/1.5.2'
    return response


def _hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def require_auth():
    op_id = session.get('operator_id')
    if not op_id:
        return None
    return Operator.query.get(op_id)


@app.route('/')
def index():
    return redirect(url_for('signin'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        op = Operator.query.filter_by(username=username, password_hash=_hash_pw(password)).first()
        if op:
            session['operator_id'] = op.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('signin.html', error='Invalid credentials')
    return render_template('signin.html')


@app.route('/signout')
def signout():
    session.pop('operator_id', None)
    return redirect(url_for('signin'))


@app.route('/dashboard')
def dashboard():
    op = require_auth()
    if not op:
        return redirect(url_for('signin'))
    nodes = ManagedNode.query.order_by(ManagedNode.hostname).all()
    online_count = ManagedNode.query.filter_by(status='online').count()
    total_tasks = TaskResult.query.count()
    failed_tasks = TaskResult.query.filter_by(status='failed').count()
    return render_template('dashboard.html', operator=op, nodes=nodes,
                           online_count=online_count, total_tasks=total_tasks,
                           failed_tasks=failed_tasks)


@app.route('/nodes')
def nodes_list():
    op = require_auth()
    if not op:
        return redirect(url_for('signin'))
    group_filter = request.args.get('group', None)
    if group_filter:
        nodes = ManagedNode.query.filter_by(node_group=group_filter).order_by(ManagedNode.hostname).all()
    else:
        nodes = ManagedNode.query.order_by(ManagedNode.hostname).all()
    groups = db.session.query(ManagedNode.node_group).distinct().all()
    groups = [g[0] for g in groups]
    return render_template('nodes.html', operator=op, nodes=nodes, groups=groups,
                           current_group=group_filter)


@app.route('/nodes/<int:node_id>')
def node_detail(node_id):
    op = require_auth()
    if not op:
        return redirect(url_for('signin'))
    node = ManagedNode.query.get_or_404(node_id)
    tasks = TaskResult.query.filter_by(node_id=node_id).order_by(TaskResult.executed_at.desc()).all()
    facts = NodeFact.query.filter_by(node_id=node_id).order_by(NodeFact.fact_key).all()
    return render_template('node_detail.html', operator=op, node=node, tasks=tasks, facts=facts)


@app.route('/nodes/<int:node_id>/tasks')
def node_tasks(node_id):
    op = require_auth()
    if not op:
        return redirect(url_for('signin'))
    node = ManagedNode.query.get_or_404(node_id)
    tasks = TaskResult.query.filter_by(node_id=node_id).order_by(TaskResult.executed_at.desc()).all()
    return render_template('node_tasks.html', operator=op, node=node, tasks=tasks)


@app.route('/tasks/<int:task_id>/output')
def task_output(task_id):
    """Render task output details for review.

    Task output from managed nodes is rendered into the report template
    so operators can review structured results inline."""
    op = require_auth()
    if not op:
        return redirect(url_for('signin'))

    task = TaskResult.query.get_or_404(task_id)
    node = ManagedNode.query.get(task.node_id)

    # Build the output detail view by interpolating task data into a
    # display template. The output_data field is included directly so
    # that any structured variables the node reported are expanded in
    # the rendered view.
    output_content = task.output_data if task.output_data else '{}'
    try:
        parsed = json.loads(output_content)
        formatted_pairs = ''.join(
            '<tr><td>{}</td><td>{}</td></tr>'.format(k, v)
            for k, v in parsed.items()
        )
    except (json.JSONDecodeError, AttributeError):
        formatted_pairs = '<tr><td>raw</td><td>' + output_content + '</td></tr>'

    report_tpl = """
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Task Output - """ + task.task_name + """</title>
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/style.css" rel="stylesheet">
    </head><body>
    <nav class="navbar navbar-dark bg-dark"><div class="container-fluid">
    <a class="navbar-brand" href="/dashboard">NodePilot</a></div></nav>
    <div class="container mt-4">
    <nav aria-label="breadcrumb"><ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/dashboard">Dashboard</a></li>
    <li class="breadcrumb-item"><a href="/nodes/""" + str(node.id) + """">""" + node.hostname + """</a></li>
    <li class="breadcrumb-item active">Task #""" + str(task.id) + """</li>
    </ol></nav>
    <div class="card"><div class="card-header"><h5>""" + task.task_name + """ <span class="badge bg-""" + ('success' if task.status == 'ok' else 'warning' if task.status == 'changed' else 'danger') + """">""" + task.status + """</span></h5>
    <small>Module: """ + task.module_name + """ | Executed: """ + str(task.executed_at) + """</small></div>
    <div class="card-body"><h6>Output Data</h6>
    <table class="table table-sm table-bordered"><thead><tr><th>Key</th><th>Value</th></tr></thead>
    <tbody>""" + formatted_pairs + """</tbody></table></div></div>
    <a href="/nodes/""" + str(node.id) + """/tasks" class="btn btn-secondary mt-3">Back to Tasks</a>
    </div></body></html>
    """

    return render_template_string(report_tpl)


@app.route('/api/v1/')
def api_index():
    """API version info and available endpoints."""
    return jsonify({
        'version': '1.5.2',
        'endpoints': {
            'nodes': '/api/v1/nodes',
            'report': '/api/v1/report',
            'facts': '/api/v1/nodes/<hostname>/facts'
        }
    })


@app.route('/api/v1/report', methods=['POST'])
def receive_node_report():
    """Receive execution results from managed nodes.

    Managed nodes call this endpoint to submit task execution results.
    The report is parsed and stored for later review by operators.
    Accepts JSON with fields: hostname, task_name, module_name, status,
    output_data (object), changed (bool), api_key.
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    required = ['hostname', 'task_name', 'module_name', 'status', 'output_data']
    for field in required:
        if field not in data:
            return jsonify({'error': 'Missing required field: {}'.format(field)}), 400

    node = ManagedNode.query.filter_by(hostname=data['hostname']).first()
    if not node:
        return jsonify({'error': 'Unknown host: {}'.format(data['hostname'])}), 404

    # Store the task result from the remote node
    output_str = json.dumps(data['output_data']) if isinstance(data['output_data'], dict) else str(data['output_data'])

    tr = TaskResult(
        node_id=node.id,
        task_name=str(data['task_name']),
        module_name=str(data['module_name']),
        status=str(data['status']),
        output_data=output_str,
        error_msg=str(data.get('error_msg', '')),
        changed=bool(data.get('changed', False)),
        executed_at=datetime.utcnow()
    )
    db.session.add(tr)

    node.last_checkin = datetime.utcnow()
    node.status = 'online'
    db.session.commit()

    return jsonify({'status': 'accepted', 'task_id': tr.id}), 201


@app.route('/api/v1/nodes', methods=['GET'])
def api_list_nodes():
    """List managed nodes (API)."""
    nodes = ManagedNode.query.order_by(ManagedNode.hostname).all()
    result = []
    for n in nodes:
        result.append({
            'id': n.id,
            'hostname': n.hostname,
            'ip_address': n.ip_address,
            'node_group': n.node_group,
            'status': n.status,
            'last_checkin': str(n.last_checkin) if n.last_checkin else None
        })
    return jsonify(result)


@app.route('/api/v1/nodes/<hostname>/facts', methods=['POST'])
def submit_node_facts(hostname):
    """Accept gathered facts from a managed node."""
    node = ManagedNode.query.filter_by(hostname=hostname).first()
    if not node:
        return jsonify({'error': 'Unknown host'}), 404

    try:
        facts = request.get_json(force=True)
    except Exception:
        return jsonify({'error': 'Invalid JSON'}), 400

    if not isinstance(facts, dict):
        return jsonify({'error': 'Facts must be a JSON object'}), 400

    for key, value in facts.items():
        existing = NodeFact.query.filter_by(node_id=node.id, fact_key=key).first()
        val_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        if existing:
            existing.fact_value = val_str
            existing.collected_at = datetime.utcnow()
        else:
            nf = NodeFact(node_id=node.id, fact_key=key, fact_value=val_str, collected_at=datetime.utcnow())
            db.session.add(nf)

    node.last_checkin = datetime.utcnow()
    node.status = 'online'
    db.session.commit()

    return jsonify({'status': 'facts updated', 'count': len(facts)}), 201


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    op = require_auth()
    if not op:
        return redirect(url_for('signin'))
    if op.role != 'admin':
        return render_template('error.html', message='Insufficient privileges'), 403

    msg = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'change_password':
            current = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            if _hash_pw(current) == op.password_hash and new_pw:
                op.password_hash = _hash_pw(new_pw)
                db.session.commit()
                msg = 'Password updated successfully.'
            else:
                msg = 'Current password incorrect or new password empty.'
        elif action == 'add_node':
            hn = request.form.get('hostname', '').strip()
            ip = request.form.get('ip_address', '').strip()
            grp = request.form.get('node_group', 'default').strip()
            os_info = request.form.get('os_info', '').strip()
            if hn and ip:
                existing = ManagedNode.query.filter_by(hostname=hn).first()
                if not existing:
                    new_node = ManagedNode(hostname=hn, ip_address=ip, node_group=grp,
                                           os_info=os_info, status='pending')
                    db.session.add(new_node)
                    db.session.commit()
                    msg = 'Node {} registered.'.format(hn)
                else:
                    msg = 'Node {} already exists.'.format(hn)
            else:
                msg = 'Hostname and IP address are required.'

    nodes = ManagedNode.query.order_by(ManagedNode.hostname).all()
    return render_template('settings.html', operator=op, nodes=nodes, msg=msg)


@app.route('/health')
def health_check():
    return 'ok', 200
