from flask import Flask, render_template, request, jsonify
import subprocess
import re
import os
import json

app = Flask(__name__)

# Simulated facts database (like Ansible facts)
SYSTEM_FACTS = {
    "hostname": "automation-node-01",
    "os_family": "Debian",
    "distribution": "Ubuntu",
    "distribution_version": "22.04",
    "ansible_version": "2.9.6",
    "python_version": "3.8.10"
}

# Available lookup plugins (for documentation)
LOOKUP_PLUGINS = {
    "env": "Look up environment variables",
    "file": "Read file contents",
    "pipe": "Execute command and return stdout",
    "lines": "Read lines from file",
    "template": "Process Jinja2 template"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/facts')
def get_facts():
    """Return system facts - safe endpoint"""
    return jsonify({"status": "success", "facts": SYSTEM_FACTS})

@app.route('/api/v1/plugins')
def list_plugins():
    """List available lookup plugins"""
    return jsonify({"status": "success", "plugins": LOOKUP_PLUGINS})

@app.route('/docs')
def documentation():
    """API documentation page"""
    return render_template('docs.html')

@app.route('/api/v1/inventory')
def inventory():
    """Return inventory data"""
    inventory_data = {
        "all": {
            "hosts": ["web01", "web02", "db01"],
            "vars": {
                "ansible_user": "deploy"
            }
        }
    }
    return jsonify({"status": "success", "inventory": inventory_data})

@app.route('/api/v1/validate', methods=['POST'])
def validate_config():
    """Validate playbook configuration - safe endpoint"""
    data = request.get_json() or {}
    playbook_name = data.get('playbook', '')
    
    # Simple validation - no command execution
    if not playbook_name:
        return jsonify({"status": "error", "message": "Playbook name required"})
    
    # Simulate validation
    valid_playbooks = ['site.yml', 'deploy.yml', 'setup.yml']
    if playbook_name in valid_playbooks:
        return jsonify({"status": "success", "valid": True, "message": f"Playbook '{playbook_name}' is valid"})
    else:
        return jsonify({"status": "success", "valid": False, "message": f"Playbook '{playbook_name}' not found"})

# Lookup plugin execution - simulates Ansible's pipe lookup
@app.route('/api/v1/lookup', methods=['POST'])
def lookup():
    """
    Execute lookup plugin with provided variables.
    Supports 'pipe' plugin for command execution.
    WARNING: Variables should be sanitized before use.
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "JSON data required"}), 400
    
    plugin = data.get('plugin', '')
    expression = data.get('expression', '')
    variables = data.get('vars', {})
    
    if not plugin:
        return jsonify({"status": "error", "message": "Plugin type required"}), 400
    
    if plugin == 'env':
        # Environment variable lookup - safe
        env_var = expression
        value = os.environ.get(env_var, '')
        # Don't expose FLAG directly
        if 'FLAG' in env_var.upper():
            return jsonify({"status": "error", "message": "Access denied"}), 403
        return jsonify({"status": "success", "value": value})
    
    elif plugin == 'file':
        # File lookup - restricted
        return jsonify({"status": "error", "message": "File lookup disabled for security"}), 403
    
    elif plugin == 'pipe':
        # Command execution - VULNERABLE like Ansible's pipe lookup
        # The expression may contain variable substitutions
        cmd = expression
        
        # Substitute variables into the command (like Ansible's variable interpolation)
        # This is where the vulnerability exists - variables are not escaped
        for var_name, var_value in variables.items():
            placeholder = "{{ " + var_name + " }}"
            cmd = cmd.replace(placeholder, str(var_value))
        
        # Basic blocklist for obvious attacks (incomplete - like the CVE)
        # The | quote filter should be used but often isn't
        BLOCKED = ['rm ', 'dd ', 'mkfs', ':(){ ', 'fork']
        for blocked in BLOCKED:
            if blocked.lower() in cmd.lower():
                return jsonify({"status": "error", "message": "Potentially dangerous command blocked"}), 403
        
        try:
            # Execute command with shell=True - the vulnerability
            # Like Ansible's pipe lookup: subprocess.Popen(term, shell=True, ...)
            p = subprocess.Popen(
                cmd, 
                shell=True, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            stdout, stderr = p.communicate(timeout=5)
            
            output = stdout.decode('utf-8') if stdout else stderr.decode('utf-8')
            
            return jsonify({
                "status": "success", 
                "output": output.strip(),
                "return_code": p.returncode
            })
        except subprocess.TimeoutExpired:
            p.kill()
            return jsonify({"status": "error", "message": "Command timed out"}), 408
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    else:
        return jsonify({"status": "error", "message": f"Unknown plugin: {plugin}"}), 400

# Legacy endpoint for backward compatibility
@app.route('/execute', methods=['POST'])
def execute_legacy():
    """Legacy command execution endpoint - deprecated"""
    return jsonify({
        "status": "error", 
        "message": "This endpoint has been deprecated. Please use /api/v1/lookup with the 'pipe' plugin."
    }), 410

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "ansible-lookup-api"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
