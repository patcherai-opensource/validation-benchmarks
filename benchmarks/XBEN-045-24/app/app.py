from flask import Flask, render_template, request, jsonify
import subprocess
import re
import os
import json

app = Flask(__name__)

# Simulated Ansible-like configuration store (facts/variables)
# In a real Ansible setup, these would come from inventory, facts, or set_fact
config_store = {
    "system_user": "guest",
    "log_level": "info",
    "service_name": "webapp"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration variables"""
    return jsonify(config_store)

@app.route('/api/config', methods=['POST'])
def set_config():
    """
    Set configuration variables (simulates Ansible set_fact or external facts).
    In a real scenario, these could come from:
    - User input in a web form
    - External API calls
    - Inventory files controlled by users
    """
    data = request.get_json() or {}
    for key, value in data.items():
        if key and isinstance(key, str) and len(key) < 50:
            config_store[key] = str(value)
    return jsonify({"status": "ok", "config": config_store})

def pipe_lookup(command_template):
    """
    Simulates Ansible's pipe lookup plugin (lib/ansible/plugins/lookup/pipe.py).
    
    CVE-2020-1734: The pipe lookup plugin uses subprocess.Popen() with shell=True.
    If the 'term' variable contains user-controlled data that isn't properly 
    sanitized with the | quote filter, command injection is possible.
    
    Example vulnerable Ansible playbook usage:
        msg: "{{ lookup('pipe', 'getent passwd ' + myuser) }}"
    
    If myuser = "foo; cat /etc/passwd", the command becomes:
        getent passwd foo; cat /etc/passwd
    """
    # This is the vulnerable code pattern from the CVE
    # From lib/ansible/plugins/lookup/pipe.py:
    # p = subprocess.Popen(term, cwd=self._loader.get_basedir(), shell=True, 
    #                      stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    
    basedir = os.getcwd()
    p = subprocess.Popen(
        command_template, 
        cwd=basedir, 
        shell=True,  # CVE-2020-1734: shell=True enables command injection
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = p.communicate()
    
    if stdout:
        return stdout.decode('utf-8', errors='replace')
    elif stderr:
        return f"Error: {stderr.decode('utf-8', errors='replace')}"
    return ""

@app.route('/api/lookup/pipe', methods=['POST'])
def lookup_pipe():
    """
    Ansible pipe lookup API endpoint.
    
    Mimics the pipe lookup plugin that executes shell commands.
    The vulnerability exists when variables/facts are interpolated into
    the command without proper escaping.
    
    Expected POST body:
    {
        "command": "echo",
        "args": "{{ system_user }}"
    }
    
    The args field can contain variable references that get interpolated
    from config_store (simulating Ansible facts/variables).
    """
    data = request.get_json() or {}
    command = data.get('command', '')
    args = data.get('args', '')
    
    # Basic command validation - only allow certain base commands
    # This simulates a "safe" configuration but the variable injection is the problem
    allowed_commands = ['echo', 'whoami', 'date', 'id', 'hostname', 'uname', 'getent', 'ls']
    
    if not command or command.split()[0] not in allowed_commands:
        return jsonify({"error": "Command not allowed. Allowed: " + ", ".join(allowed_commands)}), 400
    
    # Variable interpolation - simulating Ansible's Jinja2 template rendering
    # This is where the vulnerability lies: variables from config_store are 
    # interpolated WITHOUT proper escaping (no | quote filter applied)
    interpolated_args = args
    for key, value in config_store.items():
        # Replace {{ variable_name }} with the value from config_store
        # CVE-2020-1734: This value should be escaped with shlex.quote() but isn't
        interpolated_args = interpolated_args.replace("{{ " + key + " }}", value)
        interpolated_args = interpolated_args.replace("{{" + key + "}}", value)
    
    # Build final command - the vulnerability is that interpolated_args contains
    # unsanitized user input from config_store
    full_command = f"{command} {interpolated_args}"
    
    # Execute using the vulnerable pipe_lookup function
    result = pipe_lookup(full_command)
    
    return jsonify({
        "command": full_command,
        "result": result.strip()
    })

@app.route('/api/system/info', methods=['GET'])
def system_info():
    """Get basic system information using pipe lookups"""
    info = {}
    info['hostname'] = pipe_lookup('hostname').strip()
    info['user'] = pipe_lookup('whoami').strip()
    info['date'] = pipe_lookup('date').strip()
    return jsonify(info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
