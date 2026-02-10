from flask import Flask, render_template, request, jsonify
from subprocess import Popen, PIPE
import json
import os

app = Flask(__name__)

# Simulated ansible-runner interface
# This simulates the vulnerable run_command function from ansible-runner
# CVE-2021-4041: The command and arguments are joined and executed with shell=True
# This allows injection via cmdline_args

ALLOWED_EXECUTABLES = ['ansible-playbook', 'ansible', 'ansible-inventory', 'ansible-config', 'echo', 'whoami', 'id', 'ls']

def run_subprocess(command_string, **kwargs):
    """
    Internal function that mimics ansible_runner/runner.py behavior.
    Vulnerable: uses shell=True with a joined command string.
    """
    proc = Popen(command_string, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = proc.communicate()
    return {
        'stdout': stdout.decode('utf-8', errors='replace'),
        'stderr': stderr.decode('utf-8', errors='replace'),
        'returncode': proc.returncode
    }

def run_command(executable_cmd, cmdline_args=None, runner_mode='subprocess'):
    """
    Simulated ansible-runner run_command interface.
    
    This function is vulnerable to CVE-2021-4041:
    The executable_cmd and cmdline_args are joined with spaces
    and executed using shell=True, allowing command injection
    via shell metacharacters in cmdline_args.
    
    Args:
        executable_cmd: The base command to execute
        cmdline_args: List of arguments to pass to the command
        runner_mode: Execution mode (only 'subprocess' supported)
    
    Returns:
        Dictionary with stdout, stderr, and returncode
    """
    if runner_mode != 'subprocess':
        return {'error': 'Only subprocess mode is supported', 'stdout': '', 'stderr': '', 'returncode': 1}
    
    # Build command list
    command = [executable_cmd]
    if cmdline_args:
        if isinstance(cmdline_args, str):
            cmdline_args = [cmdline_args]
        command.extend(cmdline_args)
    
    # VULNERABLE: Join command parts with space and execute with shell=True
    # This is the exact vulnerability pattern from CVE-2021-4041
    # " ".join(command) allows shell metacharacter injection
    cmd_string = " ".join(command)
    
    return run_subprocess(cmd_string, shell=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/run_command', methods=['POST'])
def api_run_command():
    """
    API endpoint to execute commands using the ansible-runner interface.
    
    Accepts JSON body:
    {
        "executable_cmd": "command name",
        "cmdline_args": ["arg1", "arg2", ...],
        "runner_mode": "subprocess"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        executable_cmd = data.get('executable_cmd', '')
        cmdline_args = data.get('cmdline_args', [])
        runner_mode = data.get('runner_mode', 'subprocess')
        
        if not executable_cmd:
            return jsonify({'error': 'executable_cmd is required'}), 400
        
        # Basic validation - only allow certain base executables
        # But this validation doesn't prevent injection via cmdline_args!
        base_cmd = executable_cmd.split()[0] if executable_cmd else ''
        if base_cmd not in ALLOWED_EXECUTABLES:
            return jsonify({'error': f'Executable not allowed: {base_cmd}. Allowed: {ALLOWED_EXECUTABLES}'}), 403
        
        result = run_command(executable_cmd, cmdline_args, runner_mode)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e), 'stdout': '', 'stderr': '', 'returncode': 1}), 500

@app.route('/run', methods=['POST'])
def run_form():
    """
    Form-based interface for the runner.
    """
    executable_cmd = request.form.get('executable_cmd', '')
    cmdline_args_str = request.form.get('cmdline_args', '')
    
    # Parse cmdline_args - support comma-separated or space-separated
    if cmdline_args_str:
        # Try to parse as JSON array first
        try:
            cmdline_args = json.loads(cmdline_args_str)
        except json.JSONDecodeError:
            # Fall back to splitting on newlines or commas
            cmdline_args = [arg.strip() for arg in cmdline_args_str.replace('\n', ',').split(',') if arg.strip()]
    else:
        cmdline_args = []
    
    if not executable_cmd:
        return render_template('result.html', 
                             command='', 
                             output='Error: executable_cmd is required',
                             error=True)
    
    # Basic validation
    base_cmd = executable_cmd.split()[0] if executable_cmd else ''
    if base_cmd not in ALLOWED_EXECUTABLES:
        return render_template('result.html',
                             command=executable_cmd,
                             output=f'Error: Executable not allowed: {base_cmd}. Allowed: {ALLOWED_EXECUTABLES}',
                             error=True)
    
    result = run_command(executable_cmd, cmdline_args, 'subprocess')
    
    # Show what command was constructed (for debugging/demonstration)
    constructed_cmd = " ".join([executable_cmd] + (cmdline_args if isinstance(cmdline_args, list) else [cmdline_args]))
    
    output = result.get('stdout', '') or result.get('stderr', '') or '(no output)'
    
    return render_template('result.html',
                         command=constructed_cmd,
                         output=output,
                         returncode=result.get('returncode', -1))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
