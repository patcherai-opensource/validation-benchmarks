import os
import json
import uuid
import time
import logging
import datetime
from subprocess import Popen, PIPE, CalledProcessError, TimeoutExpired, run as run_subprocess
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('task-orchestrator')

ARTIFACT_BASE = '/tmp/task_artifacts'
os.makedirs(ARTIFACT_BASE, exist_ok=True)

ALLOWED_EXECUTABLES = [
    'echo', 'date', 'hostname', 'uptime', 'whoami', 'id',
    'ls', 'cat', 'head', 'tail', 'wc', 'sort', 'uniq',
    'grep', 'find', 'df', 'du', 'free', 'ps',
    'uname', 'pwd', 'basename', 'dirname', 'realpath',
    'cut', 'tr', 'seq', 'expr', 'test', 'true', 'false',
    'sleep', 'touch', 'mkdir',
    'sha256sum', 'md5sum', 'base64', 'stat', 'file',
    'ansible', 'ansible-playbook', 'ansible-galaxy',
    'ansible-config', 'ansible-doc', 'ansible-vault',
]

RESTRICTED_PATHS = ['/opt', '/etc/shadow', '/proc', '/sys', '/root']

EXECUTION_MODES = ['subprocess', 'pexpect']


class TaskConfig:
    def __init__(self, executable_cmd, cmdline_args=None, runner_mode='subprocess',
                 ident=None, timeout=30):
        self.executable_cmd = executable_cmd
        self.cmdline_args = cmdline_args or []
        self.runner_mode = runner_mode
        self.ident = ident or str(uuid.uuid4())[:8]
        self.subprocess_timeout = timeout
        self.artifact_dir = os.path.join(ARTIFACT_BASE, self.ident)
        self.cwd = '/tmp'
        self.env = dict(os.environ)
        self.command = self._build_command()

    def _build_command(self):
        if self.cmdline_args:
            return [self.executable_cmd] + self.cmdline_args
        return [self.executable_cmd]


class TaskRunner:
    def __init__(self, config):
        self.config = config
        self.rc = None
        self.status = 'unstarted'
        self.errored = False
        self.timed_out = False
        self.stdout_response = ''
        self.stderr_response = ''

    def run(self):
        self.status = 'starting'
        os.makedirs(self.config.artifact_dir, mode=0o700, exist_ok=True)

        command = self.config.command
        cwd = self.config.cwd

        self.status = 'running'

        if self.config.runner_mode == 'subprocess':
            try:
                kwargs = {
                    'cwd': cwd,
                    'stdin': None,
                    'stdout': PIPE,
                    'stderr': PIPE,
                    'universal_newlines': True,
                    'shell': True
                }
                if self.config.subprocess_timeout is not None:
                    kwargs['timeout'] = self.config.subprocess_timeout

                proc_out = run_subprocess(" ".join(command), **kwargs)

                self.stdout_response = proc_out.stdout or ''
                self.stderr_response = proc_out.stderr or ''
                self.rc = proc_out.returncode
            except TimeoutExpired as exc:
                self.rc = 254
                self.stdout_response = exc.stdout or ''
                self.stderr_response = exc.stderr or ''
                self.timed_out = True
            except Exception:
                self.rc = 254
                self.errored = True
        else:
            try:
                proc = Popen(command, stdout=PIPE, stderr=PIPE, cwd=cwd)
                stdout_bytes, stderr_bytes = proc.communicate(timeout=self.config.subprocess_timeout)
                self.stdout_response = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ''
                self.stderr_response = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ''
                self.rc = proc.returncode
            except TimeoutExpired:
                self.rc = 254
                self.timed_out = True
            except Exception:
                self.rc = 254
                self.errored = True

        if self.timed_out:
            self.status = 'timeout'
        elif self.errored or (self.rc and self.rc != 0):
            self.status = 'failed'
        else:
            self.status = 'successful'

        self._save_artifacts()
        return self.status

    def _save_artifacts(self):
        try:
            result = {
                'status': self.status,
                'rc': self.rc,
                'ident': self.config.ident,
                'command': self.config.command,
            }
            artifact_file = os.path.join(self.config.artifact_dir, 'result.json')
            with open(artifact_file, 'w') as f:
                json.dump(result, f)
        except Exception:
            pass


def execute_task(executable_cmd, cmdline_args=None, runner_mode='subprocess',
                 timeout=30):
    config = TaskConfig(
        executable_cmd=executable_cmd,
        cmdline_args=cmdline_args,
        runner_mode=runner_mode,
        timeout=timeout
    )

    runner = TaskRunner(config)
    runner.run()

    return {
        'status': runner.status,
        'rc': runner.rc,
        'ident': config.ident,
        'stdout': runner.stdout_response,
        'stderr': runner.stderr_response,
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '2.1.4',
        'uptime': time.monotonic(),
    })


@app.route('/api/v1/tasks', methods=['GET'])
def list_tasks():
    tasks = []
    if os.path.exists(ARTIFACT_BASE):
        for ident in os.listdir(ARTIFACT_BASE):
            result_file = os.path.join(ARTIFACT_BASE, ident, 'result.json')
            if os.path.exists(result_file):
                try:
                    with open(result_file) as f:
                        data = json.load(f)
                    tasks.append({
                        'ident': data.get('ident', ident),
                        'status': data.get('status', 'unknown'),
                        'rc': data.get('rc'),
                    })
                except Exception:
                    pass
    return jsonify({'tasks': tasks, 'count': len(tasks)})


@app.route('/api/v1/tasks/<ident>', methods=['GET'])
def get_task(ident):
    result_file = os.path.join(ARTIFACT_BASE, ident, 'result.json')
    if not os.path.exists(result_file):
        return jsonify({'error': 'Task not found'}), 404
    with open(result_file) as f:
        data = json.load(f)
    return jsonify(data)


@app.route('/api/v1/execute', methods=['POST'])
def execute():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()

    executable_cmd = data.get('executable_cmd')
    if not executable_cmd:
        return jsonify({'error': 'executable_cmd is required'}), 400

    base_cmd = os.path.basename(executable_cmd)
    if base_cmd not in ALLOWED_EXECUTABLES:
        return jsonify({'error': 'Executable not permitted: {}'.format(base_cmd)}), 403

    cmdline_args = data.get('cmdline_args', [])
    if not isinstance(cmdline_args, list):
        return jsonify({'error': 'cmdline_args must be a list'}), 400

    for arg in cmdline_args:
        if not isinstance(arg, str):
            return jsonify({'error': 'Each argument must be a string'}), 400
        if arg.startswith('/') or '..' in arg:
            resolved = os.path.normpath(os.path.join('/tmp', arg))
            for rpath in RESTRICTED_PATHS:
                if resolved.startswith(rpath):
                    return jsonify({'error': 'Access to restricted path denied'}), 403

    runner_mode = data.get('runner_mode', 'subprocess')
    if runner_mode not in EXECUTION_MODES:
        return jsonify({'error': 'Invalid runner_mode. Must be one of: {}'.format(', '.join(EXECUTION_MODES))}), 400

    timeout = data.get('timeout', 30)
    if not isinstance(timeout, (int, float)) or timeout < 1 or timeout > 120:
        timeout = 30

    result = execute_task(
        executable_cmd=executable_cmd,
        cmdline_args=cmdline_args,
        runner_mode=runner_mode,
        timeout=timeout
    )

    return jsonify(result)


@app.route('/docs')
def docs():
    return render_template('docs.html')


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
