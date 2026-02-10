from flask import Flask, request, jsonify, render_template
import subprocess
import os

app = Flask(__name__)

# =============================================================================
# Ansible Runner Interface Simulation
# =============================================================================
# This simulates the ansible-runner interface.run_command() API
# which allows running arbitrary commands with arguments.
# 
# In production ansible-runner (pre-CVE-2021-4041 fix), the implementation
# joined command + arguments with spaces and executed with shell=True,
# leading to command injection when arguments contained shell metacharacters.
# =============================================================================

class AnsibleRunnerConfig:
    """Simulated ansible-runner Config object"""
    def __init__(self, executable_cmd, cmdline_args=None, runner_mode='subprocess'):
        self.executable_cmd = executable_cmd
        self.cmdline_args = cmdline_args or []
        self.runner_mode = runner_mode


class Runner:
    """
    Simulated ansible-runner Runner class
    
    VULNERABLE: This implementation joins command and arguments and executes
    with shell=True, mimicking CVE-2021-4041 in ansible-runner.
    
    The vulnerable pattern is:
        command = [executable_cmd] + cmdline_args
        Popen(" ".join(command), shell=True)
    """
    
    def __init__(self, config):
        self.config = config
        self.status = None
        self.stdout = None
        self.stderr = None
        self.rc = None
    
    def run(self):
        """Execute the configured command - VULNERABLE TO COMMAND INJECTION"""
        # Build command list
        command = [self.config.executable_cmd] + self.config.cmdline_args
        
        # VULNERABLE: Join with space and execute with shell=True
        # This is the exact pattern from CVE-2021-4041
        cmd_string = " ".join(command)
        
        try:
            proc = subprocess.Popen(
                cmd_string,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True  # VULNERABLE: shell=True allows metacharacter interpretation
            )
            stdout, stderr = proc.communicate(timeout=30)
            
            self.stdout = stdout.decode('utf-8', errors='replace')
            self.stderr = stderr.decode('utf-8', errors='replace')
            self.rc = proc.returncode
            self.status = 'successful' if self.rc == 0 else 'failed'
            
        except subprocess.TimeoutExpired:
            proc.kill()
            self.status = 'timeout'
            self.rc = -1
        except Exception as e:
            self.status = 'failed'
            self.stderr = str(e)
            self.rc = -1
        
        return self


def run_command(executable_cmd, cmdline_args=None, runner_mode='subprocess'):
    """
    Simulated ansible_runner.interface.run_command() API
    
    This is the entry point that was vulnerable in CVE-2021-4041.
    It takes an executable command and list of arguments, then
    executes them using the Runner class.
    
    VULNERABLE: Arguments are joined and passed to shell, allowing
    injection of shell metacharacters like ; | & etc.
    """
    config = AnsibleRunnerConfig(
        executable_cmd=executable_cmd,
        cmdline_args=cmdline_args or [],
        runner_mode=runner_mode
    )
    
    runner = Runner(config)
    runner.run()
    
    return runner


# =============================================================================
# Web Interface for Ansible Runner
# =============================================================================

@app.route('/api/run_command', methods=['POST'])
def api_run_command():
    """
    API endpoint to execute commands via ansible-runner interface
    
    Expected JSON payload:
    {
        "executable_cmd": "command_to_run",
        "cmdline_args": ["arg1", "arg2", ...],
        "runner_mode": "subprocess"  (optional)
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON payload required"}), 400
        
        executable_cmd = data.get('executable_cmd', '')
        cmdline_args = data.get('cmdline_args', [])
        runner_mode = data.get('runner_mode', 'subprocess')
        
        if not executable_cmd:
            return jsonify({"error": "executable_cmd is required"}), 400
        
        # Ensure cmdline_args is a list
        if not isinstance(cmdline_args, list):
            cmdline_args = [str(cmdline_args)]
        
        # Execute command using ansible-runner interface (VULNERABLE)
        result = run_command(
            executable_cmd=executable_cmd,
            cmdline_args=cmdline_args,
            runner_mode=runner_mode
        )
        
        return jsonify({
            "status": result.status,
            "rc": result.rc,
            "stdout": result.stdout,
            "stderr": result.stderr
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ping', methods=['POST'])
def api_ping():
    """
    Convenience endpoint to ping a host using ansible-runner
    
    Expected JSON payload:
    {
        "host": "hostname_or_ip",
        "count": 1  (optional)
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON payload required"}), 400
        
        host = data.get('host', '')
        count = data.get('count', 1)
        
        if not host:
            return jsonify({"error": "host is required"}), 400
        
        # Build ping command arguments
        cmdline_args = ['-c', str(count), host]
        
        # Execute via ansible-runner (VULNERABLE - host can contain shell metacharacters)
        result = run_command(
            executable_cmd='ping',
            cmdline_args=cmdline_args,
            runner_mode='subprocess'
        )
        
        return jsonify({
            "status": result.status,
            "rc": result.rc,
            "stdout": result.stdout,
            "stderr": result.stderr
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/docs')
def docs():
    """API Documentation"""
    return render_template('docs.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

