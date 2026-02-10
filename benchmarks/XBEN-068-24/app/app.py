from flask import Flask, request, jsonify, render_template
import subprocess
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__)


class TaskRunner:
    """
    Task runner class for executing automation tasks.
    Inspired by ansible-runner patterns for subprocess execution.
    """
    
    def __init__(self, runner_mode='subprocess'):
        self.runner_mode = runner_mode
        self.tasks_dir = '/var/lib/taskrunner/tasks'
        os.makedirs(self.tasks_dir, exist_ok=True)
    
    def run_command(self, executable_cmd, cmdline_args=None, timeout=30):
        """
        Execute a command with given arguments.
        Similar to ansible_runner.interface.run_command
        """
        if cmdline_args is None:
            cmdline_args = []
        
        command = [executable_cmd] + cmdline_args
        cmd_string = " ".join(command)
        
        try:
            proc = subprocess.Popen(
                cmd_string,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            stdout, stderr = proc.communicate(timeout=timeout)
            return {
                'status': 'successful' if proc.returncode == 0 else 'failed',
                'rc': proc.returncode,
                'stdout': stdout.decode('utf-8', errors='replace'),
                'stderr': stderr.decode('utf-8', errors='replace')
            }
        except subprocess.TimeoutExpired:
            proc.kill()
            return {
                'status': 'timeout',
                'rc': -1,
                'stdout': '',
                'stderr': 'Command timed out'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'rc': -1,
                'stdout': '',
                'stderr': str(e)
            }


runner = TaskRunner()

ALLOWED_COMMANDS = {
    'ping': '/bin/ping',
    'nslookup': '/usr/bin/nslookup',
    'dig': '/usr/bin/dig',
    'traceroute': '/usr/bin/traceroute',
    'curl': '/usr/bin/curl',
    'wget': '/usr/bin/wget'
}


@app.route('/api/v1/tasks/run', methods=['POST'])
def run_task():
    """
    API endpoint to run automation tasks.
    Accepts JSON payload with command and arguments.
    """
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    
    command = data.get('command')
    args = data.get('args', [])
    
    if not command:
        return jsonify({'error': 'Missing required field: command'}), 400
    
    if command not in ALLOWED_COMMANDS:
        return jsonify({
            'error': f'Command not allowed: {command}',
            'allowed_commands': list(ALLOWED_COMMANDS.keys())
        }), 403
    
    if not isinstance(args, list):
        return jsonify({'error': 'args must be a list'}), 400
    
    executable = ALLOWED_COMMANDS[command]
    
    result = runner.run_command(executable, args)
    
    task_id = str(uuid.uuid4())[:8]
    
    return jsonify({
        'task_id': task_id,
        'command': command,
        'result': result
    })


@app.route('/api/v1/tasks/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get status of a task (mock implementation)"""
    return jsonify({
        'task_id': task_id,
        'status': 'completed',
        'message': 'Task execution completed'
    })


@app.route('/api/v1/commands', methods=['GET'])
def list_commands():
    """List available commands for execution"""
    return jsonify({
        'available_commands': list(ALLOWED_COMMANDS.keys()),
        'description': 'These commands are available for network diagnostics'
    })


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/docs')
def api_docs():
    return render_template('docs.html')


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

