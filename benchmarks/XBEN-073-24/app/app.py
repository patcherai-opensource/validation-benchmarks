import os
import re
import time
import subprocess
import glob
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = os.urandom(24)

# -- Configuration --
REPORT_DIR = '/var/lib/crm/reports'
LOG_DIR = '/var/log/cluster'
SESSION_DIR = '/var/lib/crm/sessions'

# Cluster nodes (simulated)
CLUSTER_NODES = ['node1', 'node2', 'node3']
CLUSTER_RESOURCES = ['ip-192.168.1.100', 'apache', 'mysql-primary', 'drbd0', 'fence-node1', 'fence-node2']

# -- Utility functions --
def get_stdout(cmd, input_s=None, stderr_on=True):
    """Run a cmd, return (rc, stdout)."""
    if stderr_on:
        stderr = None
    else:
        stderr = subprocess.PIPE
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=stderr)
    stdout_data, stderr_data = proc.communicate(input_s)
    return proc.returncode, stdout_data.decode('utf-8', errors='replace').strip()


def filter_log_output(cmd, log_data, stderr_on=True):
    """Filter string through a command (pipe)."""
    if stderr_on:
        stderr = None
    else:
        stderr = subprocess.PIPE
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=stderr)
    try:
        if isinstance(log_data, str):
            log_data = log_data.encode('utf-8')
        stdout_data, _ = p.communicate(log_data)
        p.wait()
        return p.returncode, stdout_data.decode('utf-8', errors='replace')
    except IOError:
        return -1, ''


def pipe_cmd(cmd):
    """Execute a shell command, return rc."""
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    outp, err_outp = proc.communicate()
    proc.wait()
    return proc.returncode


def read_log_for_node(node):
    """Read cluster log entries for a given node."""
    log_path = os.path.join(LOG_DIR, 'ha-log.txt')
    if not os.path.isfile(log_path):
        return ''
    with open(log_path, 'r') as f:
        return f.read()


# -- Routes --
@app.route('/')
def index():
    return render_template('dashboard.html',
                           nodes=CLUSTER_NODES,
                           resources=CLUSTER_RESOURCES)


@app.route('/api/v1/status')
def cluster_status():
    """Return cluster status summary."""
    status = {
        'cluster_name': 'ha-cluster-01',
        'stack': 'corosync',
        'nodes': {},
        'resources': {}
    }
    for n in CLUSTER_NODES:
        status['nodes'][n] = {
            'online': True,
            'standby': False,
            'maintenance': False,
            'unclean': False
        }
    for r in CLUSTER_RESOURCES:
        status['resources'][r] = {
            'running': True,
            'managed': True,
            'failed': False,
            'node': CLUSTER_NODES[hash(r) % len(CLUSTER_NODES)]
        }
    return jsonify(status)


@app.route('/nodes')
def nodes_view():
    """Show cluster nodes overview."""
    node_info = []
    for n in CLUSTER_NODES:
        node_info.append({
            'name': n,
            'online': True,
            'resources': [r for r in CLUSTER_RESOURCES if CLUSTER_NODES[hash(r) % len(CLUSTER_NODES)] == n]
        })
    return render_template('nodes.html', nodes=node_info)


@app.route('/resources')
def resources_view():
    """Show cluster resources."""
    rsc_info = []
    for r in CLUSTER_RESOURCES:
        rsc_info.append({
            'name': r,
            'type': 'primitive',
            'running': True,
            'node': CLUSTER_NODES[hash(r) % len(CLUSTER_NODES)]
        })
    return render_template('resources.html', resources=rsc_info)


@app.route('/reports')
def reports_view():
    """Show available cluster reports."""
    reports = []
    if os.path.isdir(REPORT_DIR):
        for entry in sorted(os.listdir(REPORT_DIR)):
            full_path = os.path.join(REPORT_DIR, entry)
            if os.path.isdir(full_path):
                reports.append({
                    'name': entry,
                    'created': time.ctime(os.path.getctime(full_path))
                })
    return render_template('reports.html', reports=reports)


@app.route('/reports/events')
def report_events():
    """Show cluster events from logs."""
    log_path = os.path.join(LOG_DIR, 'ha-log.txt')
    events = []
    if os.path.isfile(log_path):
        with open(log_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(line)
    return render_template('events.html', events=events[-100:])


@app.route('/reports/logs', methods=['GET', 'POST'])
def report_logs():
    """
    Show log output, optionally filtered by node.
    """
    log_path = os.path.join(LOG_DIR, 'ha-log.txt')
    output = ''
    node_filter = ''
    error_msg = None

    if not os.path.isfile(log_path):
        error_msg = 'No log data available. Source may not be initialized.'
        return render_template('logs.html', output='', node_filter='',
                               nodes=CLUSTER_NODES, error=error_msg)

    with open(log_path, 'r') as f:
        log_data = f.read()

    if request.method == 'POST':
        node_filter = request.form.get('node', '').strip()
    else:
        node_filter = request.args.get('node', '').strip()

    if node_filter:
        cmd = "grep '%s'" % node_filter
        rc, filtered = filter_log_output(cmd, log_data)
        if rc == 0:
            output = filtered
        elif rc == 1:
            output = ''
        else:
            error_msg = 'Error filtering log data'
    else:
        output = log_data

    return render_template('logs.html', output=output, node_filter=node_filter,
                           nodes=CLUSTER_NODES, error=error_msg)


@app.route('/reports/transition')
def report_transition():
    """Show transition information."""
    transitions = [
        {'pe_num': '42', 'dc': 'node1', 'start': '2024-01-15 10:23:01', 'end': '2024-01-15 10:23:05', 'tags': 'resource_start'},
        {'pe_num': '43', 'dc': 'node1', 'start': '2024-01-15 10:25:12', 'end': '2024-01-15 10:25:14', 'tags': 'monitor'},
        {'pe_num': '44', 'dc': 'node2', 'start': '2024-01-15 11:02:33', 'end': '2024-01-15 11:02:38', 'tags': 'resource_move fence'},
        {'pe_num': '45', 'dc': 'node1', 'start': '2024-01-15 11:15:00', 'end': '2024-01-15 11:15:02', 'tags': 'monitor'},
    ]
    return render_template('transitions.html', transitions=transitions)


@app.route('/reports/session', methods=['GET', 'POST'])
def report_session():
    """Manage report sessions (save/load/delete)."""
    sessions = []
    if os.path.isdir(SESSION_DIR):
        for entry in sorted(os.listdir(SESSION_DIR)):
            full_path = os.path.join(SESSION_DIR, entry)
            if os.path.isdir(full_path):
                sessions.append({
                    'name': entry,
                    'created': time.ctime(os.path.getctime(full_path))
                })

    message = None
    if request.method == 'POST':
        action = request.form.get('action', '')
        name = request.form.get('name', '').strip()

        if not name:
            message = 'Session name is required'
        elif not re.match(r'^[a-zA-Z0-9_-]+$', name):
            message = 'Invalid session name. Use only alphanumeric characters, hyphens, and underscores.'
        elif action == 'save':
            session_path = os.path.join(SESSION_DIR, name)
            if os.path.exists(session_path):
                message = 'Session "%s" already exists' % name
            else:
                os.makedirs(session_path, exist_ok=True)
                message = 'Session "%s" saved' % name
                sessions.append({'name': name, 'created': time.ctime()})
        elif action == 'delete':
            session_path = os.path.join(SESSION_DIR, name)
            if not os.path.exists(session_path):
                message = 'Session "%s" does not exist' % name
            else:
                import shutil
                shutil.rmtree(session_path)
                sessions = [s for s in sessions if s['name'] != name]
                message = 'Session "%s" deleted' % name

    return render_template('sessions.html', sessions=sessions, message=message)


@app.route('/api/v1/nodes/<node_name>')
def api_node_detail(node_name):
    """Get details for a specific node."""
    if node_name not in CLUSTER_NODES:
        return jsonify({'error': 'Node not found'}), 404
    return jsonify({
        'name': node_name,
        'online': True,
        'standby': False,
        'maintenance': False,
        'resources': [r for r in CLUSTER_RESOURCES if CLUSTER_NODES[hash(r) % len(CLUSTER_NODES)] == node_name]
    })


@app.route('/api/v1/resources/<rsc_name>')
def api_resource_detail(rsc_name):
    """Get details for a specific resource."""
    if rsc_name not in CLUSTER_RESOURCES:
        return jsonify({'error': 'Resource not found'}), 404
    return jsonify({
        'name': rsc_name,
        'type': 'primitive',
        'running': True,
        'managed': True,
        'node': CLUSTER_NODES[hash(rsc_name) % len(CLUSTER_NODES)]
    })


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Not Found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal Server Error'), 500


if __name__ == '__main__':
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(SESSION_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=80)
