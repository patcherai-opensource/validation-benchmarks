from flask import Flask, render_template, request, jsonify
import subprocess
import re
import os

app = Flask(__name__)

# Simulated Ansible-like playbook runner that uses pipe lookup
# This simulates the CVE-2020-1734 vulnerability in Ansible's pipe lookup plugin

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/docs')
def api_docs():
    return jsonify({
        "version": "1.2.0",
        "service": "AnsibleVar Lookup Service",
        "endpoints": {
            "/api/lookup": {
                "method": "POST",
                "description": "Execute a lookup command with variable substitution",
                "parameters": {
                    "lookup_type": "string (required) - Type of lookup: pipe, env, file",
                    "variable": "string (required) - The variable/command to look up"
                }
            },
            "/api/facts": {
                "method": "GET", 
                "description": "Get system facts"
            }
        }
    })

@app.route('/api/facts')
def get_facts():
    """Return simulated ansible facts"""
    return jsonify({
        "ansible_facts": {
            "hostname": "ansible-controller",
            "os_family": "Debian",
            "distribution": "Ubuntu",
            "python_version": "3.8"
        }
    })

@app.route('/api/lookup', methods=['POST'])
def lookup():
    """
    Simulates Ansible's pipe lookup plugin vulnerability (CVE-2020-1734)
    The pipe lookup uses subprocess.Popen with shell=True, allowing command injection
    when user-supplied variables are not properly quoted/escaped.
    """
    try:
        data = request.get_json() or {}
        lookup_type = data.get('lookup_type', request.form.get('lookup_type', ''))
        variable = data.get('variable', request.form.get('variable', ''))
        
        if not lookup_type or not variable:
            return jsonify({
                "status": "error",
                "message": "Missing required parameters: lookup_type and variable"
            }), 400
        
        # Only support pipe lookup for this simulation
        if lookup_type != 'pipe':
            return jsonify({
                "status": "error", 
                "message": f"Unsupported lookup type: {lookup_type}. Only 'pipe' is supported."
            }), 400
        
        # Input validation - filter some dangerous characters but miss others
        # This mirrors the incomplete sanitization that allows the CVE
        BLOCKED_CHARS = ['<', '>', '|', '&', '`']
        for char in BLOCKED_CHARS:
            if char in variable:
                return jsonify({
                    "status": "error",
                    "message": "Invalid characters detected in variable"
                }), 400
        
        # VULNERABLE: Simulates the pipe lookup plugin behavior
        # The variable is used directly in shell command without proper quoting
        # Similar to: p = subprocess.Popen(term, shell=True, ...)
        # where term includes unescaped user input
        
        # Simulate a common use case: getent lookup for user info
        command = 'getent passwd ' + variable
        
        # Execute using subprocess.Popen with shell=True (the vulnerable pattern)
        p = subprocess.Popen(
            command, 
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = p.communicate()
        
        output = stdout.decode('utf-8') if stdout else ''
        error = stderr.decode('utf-8') if stderr else ''
        
        if p.returncode == 0:
            # Parse getent output
            if output.strip():
                parts = output.strip().split(':')
                if len(parts) >= 5:
                    return jsonify({
                        "status": "success",
                        "lookup_type": lookup_type,
                        "result": {
                            "username": parts[0],
                            "uid": parts[2],
                            "gid": parts[3],
                            "info": parts[4] if len(parts) > 4 else "",
                            "home": parts[5] if len(parts) > 5 else "",
                            "shell": parts[6] if len(parts) > 6 else ""
                        }
                    })
            return jsonify({
                "status": "success",
                "lookup_type": lookup_type,
                "result": output.strip() if output else "No result found"
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Lookup failed: {error.strip() if error else 'Unknown error'}"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal error: {str(e)}"
        }), 500

# Legacy endpoint for backwards compatibility
@app.route('/lookup', methods=['POST'])
def legacy_lookup():
    """Legacy form-based lookup endpoint"""
    variable = request.form.get('variable', '')
    
    if not variable:
        return render_template('result.html', 
                             variable=variable, 
                             output="Error: No variable provided")
    
    # Same vulnerability pattern
    BLOCKED_CHARS = ['<', '>', '|', '&', '`']
    for char in BLOCKED_CHARS:
        if char in variable:
            return render_template('result.html',
                                 variable=variable,
                                 output="Invalid characters detected in variable")
    
    command = 'getent passwd ' + variable
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    
    output = stdout.decode('utf-8') if stdout else stderr.decode('utf-8')
    
    if output.strip():
        parts = output.strip().split(':')
        if len(parts) >= 5:
            formatted = f"User: {parts[0]}\nUID: {parts[2]}\nGID: {parts[3]}\nInfo: {parts[4] if len(parts) > 4 else 'N/A'}"
            return render_template('result.html', variable=variable, output=formatted)
    
    return render_template('result.html', variable=variable, output=output if output else "No result found")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
