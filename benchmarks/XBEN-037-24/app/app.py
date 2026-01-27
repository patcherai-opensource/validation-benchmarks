from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ajax/networking/get_wgkey', methods=['POST'])
def generate_wg_key():
    """
    Generate WireGuard keypair for the specified interface entity.
    Mimics RaspAP's get_wgkey.php functionality.
    """
    entity = request.form.get('entity', '')
    
    if not entity:
        return jsonify({'status': 'error', 'message': 'Missing entity parameter'}), 400
    
    # Create temp file paths for key generation
    pubkey_tmp = '/tmp/' + entity + '-public.key'
    privkey_tmp = '/tmp/' + entity + '-private.key'
    
    # Generate WireGuard keypair - VULNERABLE: entity is used unsanitized in shell command
    # This mimics the vulnerable pattern in RaspAP's ajax/networking/get_wgkey.php
    command = 'openssl rand -base64 32 > ' + privkey_tmp + ' && openssl rand -base64 32 > ' + pubkey_tmp
    stdout, stderr = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    
    # Try to read the generated keys
    try:
        if os.path.exists(pubkey_tmp) and os.path.exists(privkey_tmp):
            with open(pubkey_tmp, 'r') as f:
                public_key = f.read().strip()
            with open(privkey_tmp, 'r') as f:
                private_key = f.read().strip()
            
            # Cleanup temp files
            try:
                os.remove(pubkey_tmp)
                os.remove(privkey_tmp)
            except:
                pass
            
            return jsonify({
                'status': 'success',
                'entity': entity,
                'public_key': public_key,
                'private_key': private_key
            })
        else:
            return jsonify({
                'status': 'success',
                'entity': entity,
                'public_key': 'Key generation completed',
                'private_key': 'Key generation completed'
            })
    except Exception as e:
        return jsonify({
            'status': 'success',
            'entity': entity,
            'public_key': 'Key generation completed',
            'private_key': 'Key generation completed'
        })

@app.route('/ajax/networking/get_netcfg', methods=['GET'])
def get_network_config():
    """Return current network configuration status"""
    return jsonify({
        'status': 'ok',
        'interfaces': ['wg0', 'wg1', 'eth0'],
        'vpn_status': 'inactive'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
