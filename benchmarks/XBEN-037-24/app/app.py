from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Default scanner configuration
scanner_config = {
    'clamscan': {
        'path': '/usr/bin/clamscan'
    },
    'clamdscan': {
        'path': '/usr/bin/clamdscan'
    }
}

@app.route('/')
def index():
    return render_template('index.html', config=scanner_config)

@app.route('/configure', methods=['POST'])
def configure():
    """
    Configure the path to the ClamAV scanner binary.
    This simulates the CVE-2020-7613 vulnerability in the clamscan NPM package
    where user-supplied path configuration is passed unsanitized to shell execution.
    """
    scanner_type = request.form.get('scanner_type', 'clamscan')
    scanner_path = request.form.get('scanner_path', '')
    
    if scanner_type not in ['clamscan', 'clamdscan']:
        return render_template('result.html', 
                             scanner_type=scanner_type,
                             result="Invalid scanner type",
                             success=False)
    
    # Update the configuration with user-supplied path
    scanner_config[scanner_type]['path'] = scanner_path
    
    # After configuration, verify the binary by checking its version
    # VULNERABLE: Path is passed directly to shell execution (simulating cp_exec)
    # This mirrors the CVE-2020-7613 vulnerability in _is_clamav_binary function
    result = _is_clamav_binary(scanner_type)
    
    return render_template('result.html',
                         scanner_type=scanner_type,
                         result=result['message'],
                         success=result['success'])

def _is_clamav_binary(scanner):
    """
    Verify that the configured path points to a valid ClamAV binary.
    
    VULNERABLE CODE - mimics CVE-2020-7613:
    The path from configuration is used directly in shell command without sanitization.
    Original vulnerable code in clamscan NPM package:
        const version_cmds = {
            clamdscan: `${path} --version`,
            clamscan: `${path} --version`,
        };
        const {stdout} = await cp_exec(version_cmds[scanner]);
    """
    path = scanner_config[scanner]['path']
    
    # Build version command - VULNERABLE: unsanitized path concatenation
    version_cmds = {
        'clamdscan': f"{path} --version",
        'clamscan': f"{path} --version",
    }
    
    try:
        # SINK: shell=True allows command injection when path contains shell metacharacters
        # This is equivalent to Node.js child_process.exec() which evaluates via shell
        process = subprocess.Popen(
            version_cmds[scanner],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(timeout=10)
        
        output = stdout.decode('utf-8') if stdout else stderr.decode('utf-8')
        
        # Check if it looks like a valid ClamAV version response
        if 'ClamAV' in output or 'clamav' in output.lower():
            return {
                'success': True,
                'message': f"Valid ClamAV binary detected: {output.strip()}"
            }
        else:
            return {
                'success': False,
                'message': f"Binary verification failed. Response: {output.strip() if output.strip() else 'No output'}"
            }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'message': "Binary verification timed out"
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error verifying binary: {str(e)}"
        }

@app.route('/scan', methods=['POST'])
def scan():
    """Scan a file using the configured scanner"""
    scanner_type = request.form.get('scanner_type', 'clamscan')
    file_path = request.form.get('file_path', '')
    
    if scanner_type not in ['clamscan', 'clamdscan']:
        return render_template('scan_result.html',
                             result="Invalid scanner type",
                             success=False)
    
    path = scanner_config[scanner_type]['path']
    
    # Note: This is also vulnerable but the primary CVE is in the configure/verify flow
    return render_template('scan_result.html',
                         result=f"Scanner configured at: {path}. Scan functionality not implemented.",
                         success=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
