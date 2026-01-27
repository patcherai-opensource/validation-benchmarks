from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Store scanner configuration in memory
scanner_config = {
    'clamscan_path': '/usr/bin/clamscan',
    'clamdscan_path': '/usr/bin/clamdscan',
    'active_scanner': 'clamscan'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Return current scanner configuration"""
    return jsonify({
        'status': 'success',
        'config': {
            'clamscan_path': scanner_config['clamscan_path'],
            'clamdscan_path': scanner_config['clamdscan_path'],
            'active_scanner': scanner_config['active_scanner']
        }
    })

def _is_clamav_binary(scanner_type):
    """Verify that the configured path points to a valid ClamAV binary"""
    if scanner_type == 'clamscan':
        path = scanner_config['clamscan_path']
    else:
        path = scanner_config['clamdscan_path']
    
    # Build version check command (vulnerable to command injection)
    version_cmd = path + ' --version'
    
    try:
        # Execute the version command to verify the binary
        stdout, stderr = subprocess.Popen(
            version_cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        ).communicate(timeout=10)
        
        output = stdout.decode('utf-8', errors='ignore')
        error_output = stderr.decode('utf-8', errors='ignore')
        
        # Combine stdout and stderr for diagnostics
        full_output = output + error_output
        
        # Check if output looks like ClamAV version info
        if 'ClamAV' in output or 'clamav' in output.lower():
            return True, output.strip()
        else:
            # Return actual output for debugging purposes
            return False, f'Binary verification failed. Output: {full_output[:500]}' if full_output.strip() else 'No output from binary'
    except subprocess.TimeoutExpired:
        return False, 'Command timed out'
    except Exception as e:
        return False, str(e)

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update scanner configuration"""
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'message': 'No configuration data provided'}), 400
    
    # Update configuration values
    if 'clamscan_path' in data:
        scanner_config['clamscan_path'] = data['clamscan_path']
    
    if 'clamdscan_path' in data:
        scanner_config['clamdscan_path'] = data['clamdscan_path']
    
    if 'active_scanner' in data:
        if data['active_scanner'] not in ['clamscan', 'clamdscan']:
            return jsonify({
                'status': 'error', 
                'message': 'Invalid scanner type. Use "clamscan" or "clamdscan"'
            }), 400
        scanner_config['active_scanner'] = data['active_scanner']
    
    # Verify the configured binary by calling _is_clamav_binary
    scanner_type = scanner_config['active_scanner']
    is_valid, result = _is_clamav_binary(scanner_type)
    
    if is_valid:
        return jsonify({
            'status': 'success',
            'message': 'Configuration updated and verified',
            'scanner_verified': True,
            'version_info': result
        })
    else:
        return jsonify({
            'status': 'warning',
            'message': 'Configuration updated but binary verification failed',
            'scanner_verified': False,
            'error': result
        })

@app.route('/api/verify', methods=['POST'])
def verify_scanner():
    """Verify that the active scanner binary is valid"""
    scanner_type = scanner_config['active_scanner']
    is_valid, result = _is_clamav_binary(scanner_type)
    
    return jsonify({
        'status': 'success' if is_valid else 'error',
        'scanner_type': scanner_type,
        'path': scanner_config[f'{scanner_type}_path'],
        'verified': is_valid,
        'details': result
    })

@app.route('/configure', methods=['GET'])
def configure_page():
    """Render the configuration page"""
    return render_template('configure.html', config=scanner_config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
