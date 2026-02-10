from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)

COMMAND_TEMPLATES = {
    'user_info': {
        'name': 'User Information',
        'description': 'Look up user account information',
        'template': 'getent passwd {username}',
        'param_name': 'username',
        'placeholder': 'Enter username'
    },
    'host_lookup': {
        'name': 'DNS Lookup',
        'description': 'Resolve hostname to IP address',
        'template': 'host {hostname}',
        'param_name': 'hostname',
        'placeholder': 'Enter hostname'
    },
    'file_info': {
        'name': 'File Statistics',
        'description': 'Get file metadata and statistics',
        'template': 'stat {filepath}',
        'param_name': 'filepath',
        'placeholder': 'Enter file path'
    }
}


@app.route('/')
def index():
    return render_template('index.html', commands=COMMAND_TEMPLATES)


@app.route('/run', methods=['POST'])
def run_command():
    command_id = request.form.get('command_id', '')
    param_value = request.form.get('param_value', '')
    
    if command_id not in COMMAND_TEMPLATES:
        return render_template('result.html', 
                               command_name='Error',
                               output='Invalid command selected.')
    
    cmd_config = COMMAND_TEMPLATES[command_id]
    
    if not param_value:
        return render_template('result.html',
                               command_name=cmd_config['name'],
                               output='Parameter value is required.')
    
    command = cmd_config['template'].format(**{cmd_config['param_name']: param_value})
    
    try:
        p = subprocess.Popen(
            command,
            cwd=os.getcwd(),
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = p.communicate(timeout=10)
        output = stdout.decode('utf-8') if stdout else stderr.decode('utf-8')
        if not output.strip():
            output = 'Command executed successfully but produced no output.'
    except subprocess.TimeoutExpired:
        p.kill()
        output = 'Command execution timed out.'
    except Exception:
        output = 'An error occurred while executing the command.'
    
    return render_template('result.html',
                           command_name=cmd_config['name'],
                           output=output)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message='Internal server error'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
