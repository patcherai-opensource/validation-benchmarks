from flask import Flask, render_template, request, jsonify
import subprocess
import os
import json

app = Flask(__name__)

ALLOWED_COMMANDS = {
    'ls': 'List directory contents',
    'pwd': 'Print working directory',
    'whoami': 'Display current user',
    'date': 'Display current date and time',
    'uptime': 'Show system uptime',
    'df': 'Display disk space usage',
    'uname': 'Display system information',
    'hostname': 'Display hostname',
    'id': 'Display user identity',
    'env': 'Display environment variables (filtered)',
}


def run_command(executable_cmd, cmdline_args=None, timeout=30):
    """
    Execute a command with arguments.
    
    This function constructs the command string from the executable and arguments,
    then executes it in a subprocess.
    """
    command = [executable_cmd]
    if cmdline_args:
        if isinstance(cmdline_args, list):
            command.extend(cmdline_args)
        else:
            command.append(cmdline_args)
    
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
            'status': 'completed',
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
            'stderr': 'Command execution timed out'
        }
    except Exception as e:
        return {
            'status': 'error',
            'rc': -1,
            'stdout': '',
            'stderr': str(e)
        }


@app.route('/')
def index():
    return render_template('index.html', commands=ALLOWED_COMMANDS)


@app.route('/api/commands', methods=['GET'])
def list_commands():
    return jsonify({'commands': ALLOWED_COMMANDS})


@app.route('/api/run', methods=['POST'])
def run():
    data = request.get_json() if request.is_json else request.form
    
    executable_cmd = data.get('executable_cmd', '').strip()
    cmdline_args = data.get('cmdline_args', '')
    
    if not executable_cmd:
        return jsonify({'error': 'No command specified'}), 400
    
    if executable_cmd not in ALLOWED_COMMANDS:
        return jsonify({'error': f'Command not allowed. Available commands: {", ".join(ALLOWED_COMMANDS.keys())}'}), 403
    
    if isinstance(cmdline_args, str):
        args_list = cmdline_args.split() if cmdline_args else []
    else:
        args_list = cmdline_args if cmdline_args else []
    
    result = run_command(executable_cmd, args_list)
    
    return jsonify({
        'command': executable_cmd,
        'args': args_list,
        'result': result
    })


@app.route('/docs')
def docs():
    return render_template('docs.html', commands=ALLOWED_COMMANDS)


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
