import os
import uuid
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort

app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory storage for inventories and job history
inventories = {}
job_history = []

# Pre-defined playbook templates (mirrors Ansible playbook structure)
PLAYBOOK_TEMPLATES = {
    "system_info": {
        "name": "System Information Gathering",
        "description": "Collects basic system information from target hosts",
        "tasks": [
            {
                "name": "Get user info",
                "lookup": "pipe",
                "command_template": "getent passwd {username}",
                "register": "user_info"
            },
            {
                "name": "Check home directory",
                "lookup": "pipe",
                "command_template": "ls -la /home/{username}",
                "register": "home_dir"
            }
        ]
    },
    "service_check": {
        "name": "Service Health Check",
        "description": "Checks status of services on target hosts",
        "tasks": [
            {
                "name": "Check service status",
                "lookup": "pipe",
                "command_template": "systemctl is-active {service_name}",
                "register": "service_status"
            },
            {
                "name": "Get service uptime",
                "lookup": "pipe",
                "command_template": "systemctl show {service_name} --property=ActiveEnterTimestamp",
                "register": "service_uptime"
            }
        ]
    },
    "network_diag": {
        "name": "Network Diagnostics",
        "description": "Runs network diagnostics against target hosts",
        "tasks": [
            {
                "name": "DNS lookup",
                "lookup": "pipe",
                "command_template": "nslookup {hostname}",
                "register": "dns_result"
            },
            {
                "name": "Check connectivity",
                "lookup": "pipe",
                "command_template": "ping -c 1 -W 2 {hostname}",
                "register": "ping_result"
            }
        ]
    },
    "log_review": {
        "name": "Log Review",
        "description": "Reviews recent log entries for specified application",
        "tasks": [
            {
                "name": "Tail application log",
                "lookup": "pipe",
                "command_template": "tail -n 20 /var/log/{log_file}",
                "register": "recent_logs"
            }
        ]
    }
}


def pipe_lookup(command):
    """
    Ansible-compatible pipe lookup plugin implementation.
    Executes a command and returns its stdout.
    See: lib/ansible/plugins/lookup/pipe.py
    """
    try:
        p = subprocess.Popen(
            command,
            cwd="/tmp",
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = p.communicate(timeout=10)
        if p.returncode == 0:
            return stdout.decode('utf-8', errors='replace').strip()
        else:
            return "[ERROR] Command returned non-zero exit code: {}".format(
                stderr.decode('utf-8', errors='replace').strip()
            )
    except subprocess.TimeoutExpired:
        p.kill()
        return "[ERROR] Command timed out"
    except Exception as e:
        return "[ERROR] Execution failed"


def resolve_template(template_str, variables):
    """
    Resolve variable references in a command template.
    Variables are substituted directly, similar to how Ansible
    resolves Jinja2 expressions in playbook tasks.
    Note: Users should sanitize variables with the | quote filter
    in production environments.
    """
    result = template_str
    for key, value in variables.items():
        result = result.replace("{" + key + "}", value)
    return result


@app.route('/')
def dashboard():
    return render_template('dashboard.html',
                           inventories=inventories,
                           playbooks=PLAYBOOK_TEMPLATES,
                           recent_jobs=job_history[-10:])


@app.route('/inventories')
def list_inventories():
    return render_template('inventories.html', inventories=inventories)


@app.route('/inventories/new', methods=['GET', 'POST'])
def create_inventory():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Inventory name is required', 'error')
            return redirect(url_for('create_inventory'))

        inv_id = str(uuid.uuid4())[:8]
        variables = {}

        # Parse variable fields
        var_keys = request.form.getlist('var_key')
        var_values = request.form.getlist('var_value')
        for k, v in zip(var_keys, var_values):
            k = k.strip()
            if k:
                variables[k] = v

        inventories[inv_id] = {
            'id': inv_id,
            'name': name,
            'variables': variables,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        flash('Inventory "{}" created successfully'.format(name), 'success')
        return redirect(url_for('list_inventories'))

    return render_template('inventory_form.html')


@app.route('/inventories/<inv_id>')
def view_inventory(inv_id):
    inventory = inventories.get(inv_id)
    if not inventory:
        abort(404)
    return render_template('inventory_detail.html', inventory=inventory)


@app.route('/inventories/<inv_id>/edit', methods=['GET', 'POST'])
def edit_inventory(inv_id):
    inventory = inventories.get(inv_id)
    if not inventory:
        abort(404)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Inventory name is required', 'error')
            return redirect(url_for('edit_inventory', inv_id=inv_id))

        variables = {}
        var_keys = request.form.getlist('var_key')
        var_values = request.form.getlist('var_value')
        for k, v in zip(var_keys, var_values):
            k = k.strip()
            if k:
                variables[k] = v

        inventory['name'] = name
        inventory['variables'] = variables
        flash('Inventory updated successfully', 'success')
        return redirect(url_for('view_inventory', inv_id=inv_id))

    return render_template('inventory_form.html', inventory=inventory)


@app.route('/inventories/<inv_id>/delete', methods=['POST'])
def delete_inventory(inv_id):
    if inv_id in inventories:
        del inventories[inv_id]
        flash('Inventory deleted', 'success')
    return redirect(url_for('list_inventories'))


@app.route('/playbooks')
def list_playbooks():
    return render_template('playbooks.html', playbooks=PLAYBOOK_TEMPLATES)


@app.route('/playbooks/<playbook_id>')
def view_playbook(playbook_id):
    playbook = PLAYBOOK_TEMPLATES.get(playbook_id)
    if not playbook:
        abort(404)
    return render_template('playbook_detail.html',
                           playbook_id=playbook_id,
                           playbook=playbook,
                           inventories=inventories)


@app.route('/playbooks/<playbook_id>/run', methods=['POST'])
def run_playbook(playbook_id):
    playbook = PLAYBOOK_TEMPLATES.get(playbook_id)
    if not playbook:
        abort(404)

    inv_id = request.form.get('inventory_id', '')
    inventory = inventories.get(inv_id)
    if not inventory:
        flash('Please select a valid inventory', 'error')
        return redirect(url_for('view_playbook', playbook_id=playbook_id))

    variables = inventory['variables']
    results = []
    job_id = str(uuid.uuid4())[:8]

    for task in playbook['tasks']:
        task_result = {
            'name': task['name'],
            'register': task['register']
        }

        if task['lookup'] == 'pipe':
            # Resolve the command template with inventory variables
            # This mirrors the Ansible pipe lookup plugin behavior:
            # subprocess.Popen(term, shell=True, ...)
            # where term includes unescaped variable values
            resolved_cmd = resolve_template(task['command_template'], variables)
            output = pipe_lookup(resolved_cmd)
            task_result['command'] = resolved_cmd
            task_result['output'] = output
            task_result['status'] = 'ok' if not output.startswith('[ERROR]') else 'failed'
        else:
            task_result['output'] = 'Unknown lookup type'
            task_result['status'] = 'skipped'

        results.append(task_result)

    job = {
        'id': job_id,
        'playbook': playbook['name'],
        'playbook_id': playbook_id,
        'inventory': inventory['name'],
        'inventory_id': inv_id,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'results': results,
        'status': 'completed'
    }
    job_history.append(job)

    return render_template('job_result.html', job=job)


@app.route('/jobs')
def list_jobs():
    return render_template('jobs.html', jobs=job_history)


@app.route('/jobs/<job_id>')
def view_job(job_id):
    job = next((j for j in job_history if j['id'] == job_id), None)
    if not job:
        abort(404)
    return render_template('job_result.html', job=job)


@app.route('/api/v1/inventories', methods=['GET', 'POST'])
def api_inventories():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Name is required'}), 400

        inv_id = str(uuid.uuid4())[:8]
        variables = data.get('variables', {})

        inventories[inv_id] = {
            'id': inv_id,
            'name': name,
            'variables': variables,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify(inventories[inv_id]), 201

    return jsonify({
        'count': len(inventories),
        'results': list(inventories.values())
    })


@app.route('/api/v1/playbooks', methods=['GET'])
def api_list_playbooks():
    result = []
    for pid, pb in PLAYBOOK_TEMPLATES.items():
        result.append({
            'id': pid,
            'name': pb['name'],
            'description': pb['description'],
            'task_count': len(pb['tasks'])
        })
    return jsonify({'count': len(result), 'results': result})


@app.route('/api/v1/playbooks/<playbook_id>/launch', methods=['POST'])
def api_launch_playbook(playbook_id):
    playbook = PLAYBOOK_TEMPLATES.get(playbook_id)
    if not playbook:
        return jsonify({'error': 'Playbook not found'}), 404

    data = request.get_json(silent=True) or {}
    inv_id = data.get('inventory_id', '')
    extra_vars = data.get('extra_vars', {})

    inventory = inventories.get(inv_id)
    if not inventory:
        return jsonify({'error': 'Inventory not found'}), 404

    # Merge extra_vars with inventory variables (extra_vars take precedence)
    variables = dict(inventory['variables'])
    variables.update(extra_vars)

    results = []
    job_id = str(uuid.uuid4())[:8]

    for task in playbook['tasks']:
        task_result = {
            'name': task['name'],
            'register': task['register']
        }

        if task['lookup'] == 'pipe':
            resolved_cmd = resolve_template(task['command_template'], variables)
            output = pipe_lookup(resolved_cmd)
            task_result['command'] = resolved_cmd
            task_result['output'] = output
            task_result['status'] = 'ok' if not output.startswith('[ERROR]') else 'failed'
        else:
            task_result['output'] = 'Unknown lookup type'
            task_result['status'] = 'skipped'

        results.append(task_result)

    job = {
        'id': job_id,
        'playbook': playbook['name'],
        'inventory': inventory['name'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'results': results,
        'status': 'completed'
    }
    job_history.append(job)

    return jsonify(job)


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
