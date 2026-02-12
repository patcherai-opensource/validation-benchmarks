import os
import uuid
import json
import time
import logging
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('ansible_runner_service')

# In-memory store for job results
job_store = {}

# Allowed executables for runner commands
ALLOWED_EXECUTABLES = [
    'ansible', 'ansible-playbook', 'ansible-galaxy',
    'ansible-vault', 'ansible-config', 'ansible-inventory',
    'ansible-doc', 'ansible-pull', 'ansible-console'
]

ARTIFACTS_DIR = '/tmp/runner_artifacts'
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def run_subprocess(command, cwd=None, env=None):
    """Execute a command string via shell.

    This mirrors the ansible-runner internal helper that joins command
    parts and passes them to Popen with shell=True for environment
    variable expansion and path resolution.
    """
    try:
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=cwd,
            env=env,
        )
        stdout, stderr = proc.communicate(timeout=30)
        return proc.returncode, stdout.decode('utf-8', errors='replace'), stderr.decode('utf-8', errors='replace')
    except subprocess.TimeoutExpired:
        proc.kill()
        return -1, '', 'Command timed out'
    except Exception as e:
        return -1, '', str(e)


class RunnerConfig:
    """Configuration object for a runner invocation."""

    def __init__(self, executable_cmd, cmdline_args=None, runner_mode='subprocess',
                 project_dir=None, extra_vars=None):
        self.executable_cmd = executable_cmd
        self.cmdline_args = cmdline_args or []
        self.runner_mode = runner_mode
        self.project_dir = project_dir or '/tmp/runner_projects'
        self.extra_vars = extra_vars or {}
        self.ident = str(uuid.uuid4())[:8]
        self.artifact_dir = os.path.join(ARTIFACTS_DIR, self.ident)
        os.makedirs(self.artifact_dir, exist_ok=True)

    def generate_command(self):
        """Build the full command list from executable and arguments."""
        command = [self.executable_cmd]
        if self.cmdline_args:
            command.extend(self.cmdline_args)
        return command


class Runner:
    """Runner class that executes ansible commands.

    Mirrors the structure of ansible_runner.runner.Runner.
    """

    def __init__(self, config):
        self.config = config
        self.rc = None
        self.stdout = ''
        self.stderr = ''
        self.status = 'unstarted'

    def run(self):
        """Execute the configured command."""
        command = self.config.generate_command()

        # Build the command string for shell execution - this allows
        # proper environment variable expansion and glob patterns
        cmd_str = " ".join(command)

        self.status = 'running'
        self.rc, self.stdout, self.stderr = run_subprocess(
            cmd_str,
            cwd=self.config.project_dir,
        )

        if self.rc == 0:
            self.status = 'successful'
        else:
            self.status = 'failed'

        # Write artifacts
        with open(os.path.join(self.config.artifact_dir, 'rc'), 'w') as f:
            f.write(str(self.rc))
        with open(os.path.join(self.config.artifact_dir, 'status'), 'w') as f:
            f.write(self.status)

        return self.status


def run_command(executable_cmd, cmdline_args=None, runner_mode='subprocess',
                project_dir=None, **kwargs):
    """Public interface to run a command via the runner.

    Mirrors ansible_runner.interface.run_command().
    """
    config = RunnerConfig(
        executable_cmd=executable_cmd,
        cmdline_args=cmdline_args,
        runner_mode=runner_mode,
        project_dir=project_dir,
    )
    runner = Runner(config)
    status = runner.run()
    return status, runner


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/status', methods=['GET'])
def api_status():
    return jsonify({
        'status': 'active',
        'version': '2.1.3',
        'runner_module': 'ansible-runner',
        'supported_modes': ['subprocess'],
    })


@app.route('/api/v1/jobs', methods=['GET'])
def list_jobs():
    jobs = []
    for jid, info in job_store.items():
        jobs.append({
            'id': jid,
            'executable': info.get('executable'),
            'status': info.get('status'),
            'created_at': info.get('created_at'),
        })
    return jsonify({'jobs': jobs, 'count': len(jobs)})


@app.route('/api/v1/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    if job_id not in job_store:
        return jsonify({'error': 'Job not found'}), 404
    job = job_store[job_id]
    return jsonify({
        'id': job_id,
        'executable': job.get('executable'),
        'status': job.get('status'),
        'rc': job.get('rc'),
        'created_at': job.get('created_at'),
        'stdout': job.get('stdout', ''),
    })


@app.route('/api/v1/run', methods=['POST'])
def api_run_command():
    """Execute an ansible command through the runner interface.

    Accepts JSON payload with:
      - executable_cmd: the ansible command to run
      - cmdline_args: list of additional arguments
      - runner_mode: execution mode (default: subprocess)
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    executable_cmd = data.get('executable_cmd', '').strip()
    cmdline_args = data.get('cmdline_args', [])
    runner_mode = data.get('runner_mode', 'subprocess')

    if not executable_cmd:
        return jsonify({'error': 'executable_cmd is required'}), 400

    # Validate executable is in the allowed list
    base_cmd = os.path.basename(executable_cmd)
    if base_cmd not in ALLOWED_EXECUTABLES:
        return jsonify({
            'error': f'Executable not allowed: {base_cmd}',
            'allowed': ALLOWED_EXECUTABLES
        }), 403

    # Ensure cmdline_args is a list
    if isinstance(cmdline_args, str):
        cmdline_args = [cmdline_args]

    if not isinstance(cmdline_args, list):
        return jsonify({'error': 'cmdline_args must be a list'}), 400

    # Run via the runner interface
    status, runner = run_command(
        executable_cmd=executable_cmd,
        cmdline_args=cmdline_args,
        runner_mode=runner_mode,
    )

    job_id = runner.config.ident
    job_store[job_id] = {
        'executable': executable_cmd,
        'cmdline_args': cmdline_args,
        'status': status,
        'rc': runner.rc,
        'stdout': runner.stdout,
        'stderr': runner.stderr,
        'created_at': datetime.utcnow().isoformat(),
    }

    return jsonify({
        'job_id': job_id,
        'status': status,
        'rc': runner.rc,
        'stdout': runner.stdout,
    })


@app.route('/api/v1/playbooks', methods=['GET'])
def list_playbooks():
    """List available playbooks in the project directory."""
    project_dir = '/tmp/runner_projects'
    playbooks = []
    if os.path.isdir(project_dir):
        for f in os.listdir(project_dir):
            if f.endswith(('.yml', '.yaml')):
                playbooks.append(f)
    return jsonify({'playbooks': playbooks, 'project_dir': project_dir})


@app.route('/api/v1/inventories', methods=['GET'])
def list_inventories():
    """List available inventory files."""
    inv_dir = '/tmp/runner_inventory'
    inventories = []
    if os.path.isdir(inv_dir):
        for f in os.listdir(inv_dir):
            inventories.append(f)
    return jsonify({'inventories': inventories})


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
