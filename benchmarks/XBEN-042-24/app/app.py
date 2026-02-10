import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Simulated users database
# Low-privilege user can edit connections but shouldn't see admin secrets
USERS = {
    'operator': {
        'password': 'operator123',
        'role': 'User',
        'permissions': ['can_read', 'can_edit']  # Has edit permission per CVE
    },
    'admin': {
        'password': 'supersecretadmin!',
        'role': 'Admin',
        'permissions': ['can_read', 'can_edit', 'can_delete', 'can_admin']
    }
}

# Get flag from environment variable (planted at runtime)
FLAG = os.environ.get('FLAG', 'FLAG{default_flag}')

# Simulated connections database - similar to Airflow connections
# The 'extra' field contains sensitive information that should be masked but isn't
CONNECTIONS = {
    1: {
        'conn_id': 'postgres_production',
        'conn_type': 'postgres',
        'host': 'db.internal.company.com',
        'port': 5432,
        'schema': 'production',
        'login': 'db_user',
        'password': 'db_password_123',  # Sensitive - should be masked
        'extra': json.dumps({
            'sslmode': 'require',
            'connect_timeout': 10
        })
    },
    2: {
        'conn_id': 'aws_default',
        'conn_type': 'aws',
        'host': '',
        'port': None,
        'schema': '',
        'login': 'AKIAIOSFODNN7EXAMPLE',
        'password': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',  # Sensitive AWS secret
        'extra': json.dumps({
            'region_name': 'us-west-2',
            'role_arn': 'arn:aws:iam::123456789012:role/data-pipeline'
        })
    },
    3: {
        'conn_id': 'internal_api',
        'conn_type': 'http',
        'host': 'api.internal.company.com',
        'port': 443,
        'schema': 'https',
        'login': 'api_service',
        'password': 'api_secret_token',  # Sensitive
        'extra': json.dumps({
            'api_key': 'sk-internal-api-key-12345',
            'admin_secret': FLAG,  # THE FLAG - stored as sensitive extra field
            'webhook_token': 'whsec_secrettoken123'
        })
    },
    4: {
        'conn_id': 'slack_notifications',
        'conn_type': 'http',
        'host': 'hooks.slack.com',
        'port': 443,
        'schema': 'https',
        'login': '',
        'password': 'xoxb-slack-token-secret',  # Sensitive
        'extra': json.dumps({
            'channel': '#alerts',
            'webhook_url': 'https://hooks.slack.com/services/T00/B00/XXXX'
        })
    }
}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def has_permission(permission):
    """Check if current user has a specific permission"""
    if 'user' not in session:
        return False
    user = USERS.get(session['user'])
    if not user:
        return False
    return permission in user.get('permissions', [])


@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('connections_list'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = USERS.get(username)
        if user and user['password'] == password:
            session['user'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('connections_list'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/connection')
@login_required
def connections_list():
    """List all connections - similar to Airflow /connection endpoint"""
    if not has_permission('can_read'):
        flash('You do not have permission to view connections.', 'error')
        return redirect(url_for('index'))
    
    # In the list view, passwords are shown as asterisks (masked)
    connections_masked = []
    for conn_id, conn in CONNECTIONS.items():
        masked_conn = conn.copy()
        masked_conn['id'] = conn_id
        # Properly mask password in list view
        if masked_conn.get('password'):
            masked_conn['password'] = '********'
        # Properly mask extra in list view
        if masked_conn.get('extra'):
            try:
                extra_data = json.loads(masked_conn['extra'])
                masked_extra = {}
                for k, v in extra_data.items():
                    # Mask sensitive-looking fields in list view
                    if any(word in k.lower() for word in ['secret', 'key', 'token', 'password', 'credential']):
                        masked_extra[k] = '********'
                    else:
                        masked_extra[k] = v
                masked_conn['extra_display'] = masked_extra
            except:
                masked_conn['extra_display'] = '********'
        connections_masked.append(masked_conn)
    
    user = USERS.get(session['user'], {})
    return render_template('connections.html', 
                         connections=connections_masked, 
                         user=session['user'],
                         role=user.get('role', 'Unknown'),
                         can_edit=has_permission('can_edit'))


@app.route('/connection/edit/<int:conn_id>', methods=['GET', 'POST'])
@login_required
def connection_edit(conn_id):
    """
    Edit connection form - THIS IS THE VULNERABLE ENDPOINT
    
    VULNERABILITY: When prefilling the form, sensitive fields including
    the 'extra' field are shown in cleartext instead of being masked.
    This mirrors CVE in Apache Airflow where the prefill_form method
    exposes sensitive data to users with edit permission.
    """
    if not has_permission('can_edit'):
        flash('You do not have permission to edit connections.', 'error')
        return redirect(url_for('connections_list'))
    
    connection = CONNECTIONS.get(conn_id)
    if not connection:
        flash('Connection not found.', 'error')
        return redirect(url_for('connections_list'))
    
    if request.method == 'POST':
        # Process form submission (simplified)
        # In real Airflow, process_form would handle this
        flash('Connection updated successfully.', 'success')
        return redirect(url_for('connections_list'))
    
    # VULNERABILITY: prefill_form equivalent - exposes all sensitive data
    # The 'extra' field containing secrets is passed directly to the template
    # without masking, allowing users with 'can_edit' to see all secrets
    
    # Parse extra field for display in form
    extra_fields = {}
    if connection.get('extra'):
        try:
            extra_fields = json.loads(connection['extra'])
        except:
            extra_fields = {'raw': connection['extra']}
    
    user = USERS.get(session['user'], {})
    return render_template('connection_edit.html',
                         connection=connection,
                         conn_id=conn_id,
                         extra_fields=extra_fields,  # VULN: Not masked!
                         user=session['user'],
                         role=user.get('role', 'Unknown'))


@app.route('/health')
def health():
    return 'OK', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)

