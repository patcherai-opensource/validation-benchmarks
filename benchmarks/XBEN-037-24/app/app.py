from flask import Flask, render_template, request, redirect, url_for, flash, session
import subprocess
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

CONFIG_FILE = '/app/config/scanner_config.json'

DEFAULT_CONFIG = {
    'scanner': {
        'path': '/usr/bin/clamscan',
        'scan_options': '--infected --remove=no',
        'max_file_size': 25
    },
    'daemon': {
        'path': '/usr/bin/clamdscan',
        'socket': '/var/run/clamav/clamd.sock'
    }
}

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_scanner_version(scanner_type='scanner'):
    config = load_config()
    path = config.get(scanner_type, {}).get('path', '/usr/bin/clamscan')
    
    version_cmd = f"{path} --version"
    try:
        result = subprocess.Popen(
            version_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = result.communicate(timeout=5)
        output = stdout.decode('utf-8', errors='ignore') if stdout else stderr.decode('utf-8', errors='ignore')
        return output.strip() if output.strip() else "Unable to determine version"
    except subprocess.TimeoutExpired:
        result.kill()
        return "Version check timed out"
    except Exception as e:
        return f"Error checking version"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    config = load_config()
    scan_result = None
    
    if request.method == 'POST':
        upload_path = request.form.get('file_path', '/tmp/uploads')
        scanner_path = config.get('scanner', {}).get('path', '/usr/bin/clamscan')
        options = config.get('scanner', {}).get('scan_options', '--infected')
        
        if not os.path.exists(upload_path):
            scan_result = {'status': 'error', 'message': 'Path does not exist'}
        else:
            cmd = f"{scanner_path} {options} {upload_path}"
            try:
                proc = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = proc.communicate(timeout=30)
                output = stdout.decode('utf-8', errors='ignore') if stdout else stderr.decode('utf-8', errors='ignore')
                
                if proc.returncode == 0:
                    scan_result = {'status': 'clean', 'message': 'No threats found'}
                elif proc.returncode == 1:
                    scan_result = {'status': 'infected', 'message': 'Threats detected'}
                else:
                    scan_result = {'status': 'error', 'message': 'Scan completed with warnings'}
            except subprocess.TimeoutExpired:
                proc.kill()
                scan_result = {'status': 'error', 'message': 'Scan timed out'}
            except Exception:
                scan_result = {'status': 'error', 'message': 'Scan failed'}
    
    return render_template('scan.html', config=config, scan_result=scan_result)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    config = load_config()
    message = None
    version_info = {}
    
    if request.method == 'POST':
        action = request.form.get('action', 'save')
        
        if action == 'check_version':
            scanner_type = request.form.get('scanner_type', 'scanner')
            version_info[scanner_type] = get_scanner_version(scanner_type)
        elif action == 'save':
            scanner_path = request.form.get('scanner_path')
            daemon_path = request.form.get('daemon_path')
            scan_options = request.form.get('scan_options')
            max_file_size = request.form.get('max_file_size', '25')
            
            if scanner_path:
                config['scanner']['path'] = scanner_path
            if daemon_path:
                config['daemon']['path'] = daemon_path
            if scan_options:
                config['scanner']['scan_options'] = scan_options
            try:
                config['scanner']['max_file_size'] = int(max_file_size)
            except:
                pass
            
            save_config(config)
            message = {'type': 'success', 'text': 'Settings saved successfully'}
            
        elif action == 'reset':
            save_config(DEFAULT_CONFIG.copy())
            config = DEFAULT_CONFIG.copy()
            message = {'type': 'success', 'text': 'Settings reset to defaults'}
    
    return render_template('settings.html', config=config, message=message, version_info=version_info)

@app.route('/status')
def status():
    config = load_config()
    scanner_version = get_scanner_version('scanner')
    daemon_version = get_scanner_version('daemon')
    
    return render_template('status.html', 
                          config=config,
                          scanner_version=scanner_version,
                          daemon_version=daemon_version)

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
