from flask import Flask, request, jsonify, render_template
import subprocess
import os

app = Flask(__name__)

# Handle flag injection at runtime via environment variable
flag = os.environ.get('FLAG', 'FLAG{default-flag}')
with open('/app/FLAG.txt', 'w') as f:
    f.write(flag)
os.chmod('/app/FLAG.txt', 0o600)

# Predefined automation playbooks
PLAYBOOKS = {
    'ping': {'name': 'Network Ping', 'executable': '/usr/bin/ping', 'description': 'Ping a host to check connectivity'},
    'disk': {'name': 'Disk Check', 'executable': '/bin/df', 'description': 'Check disk space usage'},
    'uptime': {'name': 'System Uptime', 'executable': '/usr/bin/uptime', 'description': 'Show system uptime'},
    'whoami': {'name': 'Current User', 'executable': '/usr/bin/whoami', 'description': 'Display current user'},
    'date': {'name': 'System Date', 'executable': '/bin/date', 'description': 'Show current date and time'},
}


def run_command(executable_cmd, cmdline_args=None, runner_mode='subprocess'):
    """
    Execute a command with the specified arguments.
    Mimics ansible_runner.interface.run_command functionality.
    
    Args:
        executable_cmd: The executable to run
        cmdline_args: List of command line arguments
        runner_mode: Execution mode (subprocess only supported)
    """
    if cmdline_args is None:
        cmdline_args = []
    
    # Build command list
    command = [executable_cmd] + cmdline_args
    
    # Join command for shell execution (vulnerable pattern from ansible-runner)
    # This mimics the vulnerable pattern: " ".join(command) with shell=True
    cmd_string = " ".join(command)
    
    try:
        proc = subprocess.Popen(
            cmd_string,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True  # Vulnerable: shell=True with joined string
        )
        stdout, stderr = proc.communicate(timeout=10)
        return {
            'status': 'successful' if proc.returncode == 0 else 'failed',
            'rc': proc.returncode,
            'stdout': stdout.decode('utf-8', errors='replace'),
            'stderr': stderr.decode('utf-8', errors='replace')
        }
    except subprocess.TimeoutExpired:
        proc.kill()
        return {'status': 'timeout', 'rc': -1, 'stdout': '', 'stderr': 'Command timed out'}
    except Exception as e:
        return {'status': 'error', 'rc': -1, 'stdout': '', 'stderr': str(e)}


@app.route('/api/v1/playbooks', methods=['GET'])
def list_playbooks():
    """List available automation playbooks"""
    return jsonify({
        'status': 'ok',
        'playbooks': [
            {'id': k, 'name': v['name'], 'description': v['description']} 
            for k, v in PLAYBOOKS.items()
        ]
    })


@app.route('/api/v1/run', methods=['POST'])
def run_playbook():
    """
    Execute an automation playbook with optional arguments.
    
    Expected JSON body:
    {
        "playbook": "ping",
        "args": ["-c", "1", "localhost"]
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    playbook_id = data.get('playbook', '')
    args = data.get('args', [])
    
    # Validate playbook exists
    if playbook_id not in PLAYBOOKS:
        return jsonify({
            'error': f'Unknown playbook: {playbook_id}',
            'available': list(PLAYBOOKS.keys())
        }), 400
    
    # Basic validation - args must be a list
    if not isinstance(args, list):
        return jsonify({'error': 'args must be a list'}), 400
    
    # Convert all args to strings
    args = [str(a) for a in args]
    
    playbook = PLAYBOOKS[playbook_id]
    
    # Execute using run_command (mimics ansible_runner.interface.run_command)
    result = run_command(
        executable_cmd=playbook['executable'],
        cmdline_args=args,
        runner_mode='subprocess'
    )
    
    return jsonify({
        'playbook': playbook_id,
        'playbook_name': playbook['name'],
        'result': result
    })


@app.route('/api/v1/run_async', methods=['POST'])
def run_playbook_async():
    """
    Execute playbook asynchronously (actually runs sync but returns job format).
    This endpoint demonstrates the run_command_async pattern.
    """
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    playbook_id = data.get('playbook', '')
    args = data.get('args', [])
    
    if playbook_id not in PLAYBOOKS:
        return jsonify({
            'error': f'Unknown playbook: {playbook_id}',
            'available': list(PLAYBOOKS.keys())
        }), 400
    
    if not isinstance(args, list):
        return jsonify({'error': 'args must be a list'}), 400
    
    args = [str(a) for a in args]
    playbook = PLAYBOOKS[playbook_id]
    
    result = run_command(
        executable_cmd=playbook['executable'],
        cmdline_args=args,
        runner_mode='subprocess'
    )
    
    # Return in async job format
    import uuid
    job_id = str(uuid.uuid4())[:8]
    return jsonify({
        'job_id': job_id,
        'playbook': playbook_id,
        'status': result['status'],
        'result': result
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'ansible-runner-api'})


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

