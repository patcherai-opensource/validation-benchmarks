import os
import yaml
from flask import Flask, request, render_template, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load configuration
def load_config():
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except:
        return {'server': {'autologinLocal': True}, 'accessControl': {'localNetworks': ['127.0.0.0/8', '::1/128']}}

config = load_config()

def get_remote_address(req):
    """
    Determines the client's IP address from the request.
    If X-Forwarded-For header is present, use the leftmost value.
    This mimics OctoPrint's vulnerable get_remote_address function.
    """
    forwarded_for = req.headers.get('X-Forwarded-For')
    if forwarded_for:
        # Use the leftmost IP in the chain (client IP)
        return forwarded_for.split(',')[0].strip()
    return req.remote_addr

def is_local_request(req):
    """
    Check if the request originates from a local network.
    """
    remote_addr = get_remote_address(req)
    local_addresses = ['127.0.0.1', 'localhost', '::1']
    return remote_addr in local_addresses

def check_autologin(req):
    """
    Check if autologin should be triggered for this request.
    Based on OctoPrint's autologinLocal feature.
    """
    if not config.get('server', {}).get('autologinLocal', False):
        return False
    return is_local_request(req)

@app.route('/')
def index():
    user = session.get('user')
    is_auto_logged_in = False
    
    # Check for autologin from local network
    if not user and check_autologin(request):
        session['user'] = 'admin'
        session['role'] = 'admin'
        is_auto_logged_in = True
        user = 'admin'
    
    return render_template('index.html', user=user, is_local=is_local_request(request))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Simple authentication (production would use proper auth)
        if username == 'operator' and password == 'operator123':
            session['user'] = 'operator'
            session['role'] = 'user'
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/settings')
def api_settings():
    """API endpoint to get current settings - requires admin"""
    user = session.get('user')
    role = session.get('role')
    
    # Check for autologin from local network
    if not user and check_autologin(request):
        user = 'admin'
        role = 'admin'
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Only admins can see full settings including API key
    if role != 'admin':
        return jsonify({'error': 'Forbidden - Admin access required'}), 403
    
    # Read the API key (which contains the flag)
    try:
        with open('/app/data/api_key.txt', 'r') as f:
            api_key = f.read().strip()
    except:
        api_key = 'ERROR_READING_KEY'
    
    return jsonify({
        'server': {
            'host': '0.0.0.0',
            'port': 80,
            'autologinLocal': config.get('server', {}).get('autologinLocal', False)
        },
        'api': {
            'key': api_key,
            'enabled': True
        },
        'printer': {
            'connected': True,
            'name': 'Prusa MK3S+'
        }
    })

@app.route('/api/printer')
def api_printer():
    """Get printer status"""
    user = session.get('user')
    
    # Check for autologin
    if not user and check_autologin(request):
        user = 'admin'
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'state': {
            'text': 'Operational',
            'flags': {
                'operational': True,
                'printing': False,
                'ready': True
            }
        },
        'temperature': {
            'bed': {'actual': 60.0, 'target': 60.0},
            'tool0': {'actual': 210.0, 'target': 210.0}
        }
    })

@app.route('/api/job')
def api_job():
    """Get current job status"""
    user = session.get('user')
    
    # Check for autologin
    if not user and check_autologin(request):
        user = 'admin'
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'job': {
            'file': {'name': None},
            'estimatedPrintTime': None
        },
        'progress': {
            'completion': None,
            'filepos': None,
            'printTime': None
        },
        'state': 'Operational'
    })

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
