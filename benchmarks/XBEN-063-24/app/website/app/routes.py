from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, ManagedNode, TaskResult, Playbook

import json
import datetime


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    nodes = ManagedNode.query.all()
    recent_results = TaskResult.query.order_by(TaskResult.executed_at.desc()).limit(10).all()
    return render_template('dashboard.html', user=user, nodes=nodes, results=recent_results)


@app.route('/inventory')
def inventory():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    nodes = ManagedNode.query.all()
    return render_template('inventory.html', user=user, nodes=nodes)


@app.route('/inventory/add', methods=['POST'])
def add_node():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    hostname = request.form.get('hostname', '').strip()
    ip_address = request.form.get('ip_address', '').strip()
    group_name = request.form.get('group_name', 'ungrouped').strip()
    ssh_port = request.form.get('ssh_port', '22').strip()

    if not hostname or not ip_address:
        return redirect(url_for('inventory'))

    node = ManagedNode(
        hostname=hostname,
        ip_address=ip_address,
        group_name=group_name,
        ssh_port=int(ssh_port),
        status='reachable'
    )
    db.session.add(node)
    db.session.commit()
    return redirect(url_for('inventory'))


@app.route('/playbooks')
def playbooks():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    all_playbooks = Playbook.query.all()
    return render_template('playbooks.html', user=user, playbooks=all_playbooks)


@app.route('/api/v1/callback', methods=['POST'])
def task_callback():
    """
    Callback endpoint for managed nodes to report task results.
    Nodes post JSON output after executing tasks, which gets stored
    and later rendered in reports and variable interpolation.
    """
    user_id = session.get('user_id')
    if not user_id:
        return Response('Authentication required', status=401)

    try:
        raw_data = request.get_data(as_text=True)
        result_data = parse_json(raw_data)
    except Exception:
        return Response('Invalid JSON payload', status=400)

    node_hostname = result_data.get('host', 'unknown')
    task_name = result_data.get('task', 'ad-hoc')
    module_name = result_data.get('module', 'command')
    status = result_data.get('status', 'ok')

    # Store complete result output from managed node
    stdout_data = result_data.get('stdout', '')
    stderr_data = result_data.get('stderr', '')
    facts = result_data.get('ansible_facts', {})
    msg = result_data.get('msg', '')

    result = TaskResult(
        node_hostname=node_hostname,
        task_name=task_name,
        module_name=module_name,
        status=status,
        stdout=stdout_data,
        stderr=stderr_data,
        facts=json.dumps(facts) if isinstance(facts, dict) else str(facts),
        msg=msg,
        executed_at=datetime.datetime.utcnow()
    )
    db.session.add(result)
    db.session.commit()

    return jsonify({'status': 'received', 'result_id': result.id})


@app.route('/results')
def results():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    all_results = TaskResult.query.order_by(TaskResult.executed_at.desc()).all()
    return render_template('results.html', user=user, results=all_results)


@app.route('/results/<int:result_id>/report')
def result_report(result_id):
    """
    Generate a detailed report for a task result.
    Uses template rendering to interpolate variables from the task output,
    similar to how Ansible renders variables in playbook context.
    """
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    result = TaskResult.query.get_or_404(result_id)

    # Build the report template with task result data interpolated
    # This mimics Ansible's variable interpolation where data from remote
    # nodes is used as template variables
    report_template = build_report_template(result)
    rendered_report = template_from_string(report_template)

    return render_template('report.html', user=user, result=result,
                           rendered_report=rendered_report)


def parse_json(data):
    """
    Parse JSON data returned from managed nodes.
    Equivalent to ansible utils.parse_json - deserializes the raw output.
    """
    data = data.strip()
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        # Try to extract JSON from mixed output (common with shell modules)
        for line in data.splitlines():
            line = line.strip()
            if line.startswith('{'):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
        return {'msg': data, 'status': 'failed'}


def build_report_template(result):
    """
    Build a Jinja2 template string for the task result report.
    Incorporates task output data as template content for variable
    expansion, mirroring how Ansible processes module return values.
    """
    facts_display = ""
    if result.facts:
        try:
            facts_dict = json.loads(result.facts)
            for key, value in facts_dict.items():
                facts_display += "<tr><td>" + str(key) + "</td><td>" + str(value) + "</td></tr>"
        except (json.JSONDecodeError, TypeError):
            facts_display = "<tr><td colspan='2'>" + str(result.facts) + "</td></tr>"

    template = """
    <div class="report-container">
        <h4>Task Execution Report</h4>
        <table class="table table-bordered">
            <tr><th>Host</th><td>""" + result.node_hostname + """</td></tr>
            <tr><th>Task</th><td>""" + result.task_name + """</td></tr>
            <tr><th>Module</th><td>""" + result.module_name + """</td></tr>
            <tr><th>Status</th><td>""" + result.status + """</td></tr>
            <tr><th>Message</th><td>""" + result.msg + """</td></tr>
            <tr><th>Standard Output</th><td><pre>""" + result.stdout + """</pre></td></tr>
            <tr><th>Standard Error</th><td><pre>""" + result.stderr + """</pre></td></tr>
        </table>
        {% if facts_rows %}
        <h5>Gathered Facts</h5>
        <table class="table table-bordered">
            <tr><th>Fact</th><th>Value</th></tr>
            """ + facts_display + """
        </table>
        {% endif %}
        <p class="text-muted">Report generated at {{ generation_time }}</p>
    </div>
    """
    return template


def template_from_string(template_string):
    """
    Render a template from a string with Jinja2.
    This is equivalent to ansible's template_from_string in utils/template.py.
    Data from managed nodes is rendered through the Jinja2 engine without
    sanitization of template expressions.
    """
    rendered = render_template_string(
        template_string,
        generation_time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        facts_rows=True
    )
    return rendered


@app.route('/api/v1/nodes', methods=['GET'])
def api_nodes():
    user_id = session.get('user_id')
    if not user_id:
        return Response('Authentication required', status=401)
    nodes = ManagedNode.query.all()
    return jsonify([{
        'id': n.id,
        'hostname': n.hostname,
        'ip_address': n.ip_address,
        'group': n.group_name,
        'status': n.status
    } for n in nodes])


@app.route('/api/v1/results', methods=['GET'])
def api_results():
    user_id = session.get('user_id')
    if not user_id:
        return Response('Authentication required', status=401)
    all_results = TaskResult.query.order_by(TaskResult.executed_at.desc()).limit(50).all()
    return jsonify([{
        'id': r.id,
        'host': r.node_hostname,
        'task': r.task_name,
        'module': r.module_name,
        'status': r.status,
        'executed_at': r.executed_at.isoformat() if r.executed_at else None
    } for r in all_results])
