from flask import Flask, render_template, request, jsonify
import subprocess
import os
import json

app = Flask(__name__)

# Simulated task configurations (like ansible playbooks/tasks)
TASK_REGISTRY = {
    "system_check": {"executable": "uname", "description": "Check system information"},
    "disk_usage": {"executable": "df", "description": "Check disk space usage"},
    "memory_info": {"executable": "free", "description": "Display memory usage"},
    "list_processes": {"executable": "ps", "description": "List running processes"},
    "network_stats": {"executable": "netstat", "description": "Network statistics"},
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/api/tasks')
def list_tasks():
    """List available automation tasks"""
    return jsonify({
        "status": "success",
        "tasks": {k: v["description"] for k, v in TASK_REGISTRY.items()}
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.2.4"})

@app.route('/api/config')
def config():
    """Get runner configuration"""
    return jsonify({
        "runner_mode": "subprocess",
        "timeout": 30,
        "shell_enabled": True,
        "supported_executables": list(TASK_REGISTRY.keys())
    })

# Safe endpoint - uses list-based subprocess (no injection possible)
@app.route('/api/tasks/run', methods=['POST'])
def run_task():
    """Run a predefined automation task (safe)"""
    data = request.get_json() or {}
    task_name = data.get('task', '')
    
    if task_name not in TASK_REGISTRY:
        return jsonify({"status": "error", "message": f"Unknown task: {task_name}"}), 400
    
    task = TASK_REGISTRY[task_name]
    try:
        # Safe - uses list, no shell
        result = subprocess.run(
            [task["executable"], "-a"] if task_name == "system_check" else [task["executable"]],
            capture_output=True,
            text=True,
            timeout=10
        )
        return jsonify({
            "status": "success",
            "task": task_name,
            "output": result.stdout,
            "errors": result.stderr
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# VULNERABLE ENDPOINT - mimics ansible-runner's run_command behavior
# Arguments are joined and executed with shell=True
@app.route('/api/runner/execute', methods=['POST'])
def execute_command():
    """Execute automation command with arguments (like ansible-runner run_command)"""
    data = request.get_json() or {}
    
    executable_cmd = data.get('executable_cmd', '')
    cmdline_args = data.get('cmdline_args', [])
    runner_mode = data.get('runner_mode', 'subprocess')
    
    if not executable_cmd:
        return jsonify({"status": "error", "message": "executable_cmd is required"}), 400
    
    # Validate runner_mode
    if runner_mode not in ['subprocess', 'pexpect']:
        return jsonify({"status": "error", "message": "Invalid runner_mode"}), 400
    
    # Build command string (VULNERABLE - mimics ansible-runner behavior)
    # This is the same pattern as CVE-2021-4041
    command_parts = [executable_cmd] + (cmdline_args if isinstance(cmdline_args, list) else [])
    command = " ".join(command_parts)
    
    try:
        # VULNERABLE: shell=True with user-controlled input
        proc = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(timeout=15)
        
        return jsonify({
            "status": "completed",
            "command": executable_cmd,
            "exit_code": proc.returncode,
            "stdout": stdout.decode('utf-8', errors='replace'),
            "stderr": stderr.decode('utf-8', errors='replace')
        })
    except subprocess.TimeoutExpired:
        proc.kill()
        return jsonify({"status": "error", "message": "Command timed out"}), 504
    except Exception as e:
        return jsonify({"status": "error", "message": f"Execution failed: {str(e)}"}), 500

# Legacy web interface for simple commands
@app.route('/runner', methods=['GET', 'POST'])
def runner_web():
    if request.method == 'GET':
        return render_template('runner.html')
    
    executable = request.form.get('executable', '')
    args = request.form.get('args', '')
    
    if not executable:
        return render_template('runner.html', error="Executable is required")
    
    # Build command (VULNERABLE)
    command = executable + " " + args if args else executable
    
    try:
        proc = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(timeout=15)
        output = stdout.decode('utf-8', errors='replace') + stderr.decode('utf-8', errors='replace')
        return render_template('runner.html', output=output, executable=executable, args=args)
    except Exception as e:
        return render_template('runner.html', error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
