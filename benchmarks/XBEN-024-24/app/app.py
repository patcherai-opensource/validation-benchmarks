import os
import urllib.request
import urllib.error
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# User database (in production this would be backed by a real database)
users = {
    'admin': {
        'username': 'admin',
        'password': 'axis',
        'role': 'administrator',
        'display_name': 'System Administrator',
        'email': 'admin@axis-services.local'
    }
}

# Service registry
services = {
    'OrderProcessingService': {
        'name': 'OrderProcessingService',
        'endpoint': 'http://services.internal:8081/orders/v2',
        'wsdl': 'http://services.internal:8081/orders/v2?wsdl',
        'status': 'active',
        'type': 'SOAP',
        'description': 'Handles order processing and fulfillment workflows'
    },
    'InventoryService': {
        'name': 'InventoryService',
        'endpoint': 'http://services.internal:8082/inventory',
        'wsdl': 'http://services.internal:8082/inventory?wsdl',
        'status': 'active',
        'type': 'SOAP',
        'description': 'Real-time inventory tracking and management'
    },
    'NotificationService': {
        'name': 'NotificationService',
        'endpoint': 'http://services.internal:8083/notify',
        'wsdl': 'http://services.internal:8083/notify?wsdl',
        'status': 'inactive',
        'type': 'REST',
        'description': 'Email and SMS notification dispatch service'
    },
    'AuthenticationService': {
        'name': 'AuthenticationService',
        'endpoint': 'http://services.internal:8084/auth',
        'wsdl': 'http://services.internal:8084/auth?wsdl',
        'status': 'active',
        'type': 'SOAP',
        'description': 'Centralized authentication and token management'
    }
}

# Blocked protocols for service lookups - prevent dangerous JNDI-style attacks
# Security: filter known dangerous protocols used in JNDI injection
BLOCKED_PROTOCOLS = ['ldap', 'ldaps', 'rmi', 'jms', 'jndi', 'dns']


def check_protocol_filter(url):
    """
    Filter dangerous protocols from service lookup URLs.
    Prevents JNDI injection and similar protocol-based attacks.
    Only HTTP(S) and standard service protocols should be permitted.
    """
    parsed_protocol = url.strip().split('://')[0].lower() if '://' in url else ''

    for blocked in BLOCKED_PROTOCOLS:
        if parsed_protocol == blocked:
            return False, f"Protocol '{parsed_protocol}' is not permitted for security reasons"

    return True, None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        user = users.get(session['username'])
        if not user or user.get('role') != 'administrator':
            flash('Access denied. Administrator privileges required.')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@require_auth
def dashboard():
    username = session['username']
    user = users[username]
    return render_template('dashboard.html', user=user, services=services)


@app.route('/services')
@require_auth
def list_services():
    return render_template('services.html', services=services)


@app.route('/services/<service_name>')
@require_auth
def service_detail(service_name):
    service = services.get(service_name)
    if not service:
        flash('Service not found.')
        return redirect(url_for('list_services'))
    return render_template('service_detail.html', service=service)


@app.route('/admin/services/deploy', methods=['GET', 'POST'])
@require_admin
def deploy_service():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        endpoint = request.form.get('endpoint', '').strip()
        wsdl = request.form.get('wsdl', '').strip()
        stype = request.form.get('type', 'SOAP')
        description = request.form.get('description', '').strip()

        if not name or not endpoint:
            flash('Service name and endpoint are required.')
            return render_template('deploy_service.html')

        if name in services:
            flash('A service with that name already exists.')
            return render_template('deploy_service.html')

        services[name] = {
            'name': name,
            'endpoint': endpoint,
            'wsdl': wsdl or endpoint + '?wsdl',
            'status': 'inactive',
            'type': stype,
            'description': description
        }
        flash(f'Service "{name}" registered successfully.')
        return redirect(url_for('list_services'))

    return render_template('deploy_service.html')


@app.route('/admin/services/lookup', methods=['GET', 'POST'])
@require_admin
def service_lookup():
    """
    Service Factory lookup - resolve and test service endpoints.
    Administrators can provide a service name (from registry) or a direct
    URL to verify connectivity and retrieve service metadata/WSDL.
    """
    result = None
    error = None

    if request.method == 'POST':
        lookup_name = request.form.get('serviceName', '').strip()

        if not lookup_name:
            error = 'Service name or URL is required.'
        else:
            # Check if it's a registered service name
            if lookup_name in services:
                target_url = services[lookup_name]['wsdl']
            else:
                target_url = lookup_name

            # Apply protocol security filter
            allowed, filter_msg = check_protocol_filter(target_url)
            if not allowed:
                error = filter_msg
            else:
                try:
                    req = urllib.request.Request(target_url, headers={
                        'User-Agent': 'AxisServiceManager/1.3',
                        'Accept': '*/*'
                    })
                    with urllib.request.urlopen(req, timeout=10) as response:
                        content = response.read(8192)
                        try:
                            result = content.decode('utf-8')
                        except UnicodeDecodeError:
                            result = content.decode('latin-1')
                except urllib.error.HTTPError as e:
                    error = f'HTTP {e.code}: {e.reason}'
                except urllib.error.URLError as e:
                    error = f'Connection failed: {str(e.reason)}'
                except Exception as e:
                    error = f'Lookup failed: {str(e)}'

    return render_template('service_lookup.html', result=result, error=error)


@app.route('/admin/settings')
@require_admin
def admin_settings():
    return render_template('admin_settings.html')


@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'AxisServiceManager'}), 200


@app.route('/axis/services')
def axis_services_list():
    """Public listing of available services (metadata only)."""
    service_list = []
    for name, svc in services.items():
        if svc['status'] == 'active':
            service_list.append({
                'name': svc['name'],
                'type': svc['type'],
                'status': svc['status']
            })
    return jsonify({'services': service_list})


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=False, host='0.0.0.0', port=80)
