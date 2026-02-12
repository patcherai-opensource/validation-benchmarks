import os
import json
import uuid
import hashlib
import threading
import time
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

import paramiko

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('ssh-manager')

DATA_DIR = '/data'
CONNECTIONS_FILE = os.path.join(DATA_DIR, 'connections.json')
KNOWN_HOSTS_FILE = os.path.join(DATA_DIR, 'known_hosts')

def _load_connections():
    if not os.path.exists(CONNECTIONS_FILE):
        return {}
    with open(CONNECTIONS_FILE, 'r') as f:
        return json.load(f)

def _save_connections(conns):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONNECTIONS_FILE, 'w') as f:
        json.dump(conns, f, indent=2)

def _get_known_host_key(hostname, port):
    """Load a previously stored host key for this hostname:port."""
    key_file = os.path.join(DATA_DIR, 'host_keys', f'{hostname}_{port}.pub')
    if not os.path.exists(key_file):
        return None
    with open(key_file, 'r') as f:
        data = json.load(f)
    return data

def _save_host_key(hostname, port, key_type, key_data, fingerprint):
    """Store a host key for future verification."""
    key_dir = os.path.join(DATA_DIR, 'host_keys')
    os.makedirs(key_dir, exist_ok=True)
    key_file = os.path.join(key_dir, f'{hostname}_{port}.pub')
    with open(key_file, 'w') as f:
        json.dump({
            'type': key_type,
            'data': key_data,
            'fingerprint': fingerprint,
            'first_seen': datetime.utcnow().isoformat()
        }, f)

def _get_key_fingerprint(key):
    """Compute the fingerprint of a paramiko key."""
    return hashlib.sha256(key.asbytes()).hexdigest()


class SSHSession:
    """
    SSH session handler modeled after tabby-ssh session management.
    Manages connection lifecycle including host key verification and authentication.
    """

    def __init__(self, connection_profile):
        self.profile = connection_profile
        self.hostname = connection_profile['hostname']
        self.port = int(connection_profile.get('port', 22))
        self.username = connection_profile.get('username', '')
        self.password = connection_profile.get('password', '')
        self.auth_method = connection_profile.get('auth_method', 'password')
        self.host_verified = False
        self.host_verified_promise = threading.Event()
        self.auth_sent = False
        self.connection_log = []
        self.client = None

    def log(self, level, message):
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message
        }
        self.connection_log.append(entry)

    def verify_host_key(self, transport_host_key):
        """
        Verify the server's host key against known hosts.
        Returns True if key matches or is new, False if mismatch.
        """
        key_type = transport_host_key.get_name()
        key_fingerprint = _get_key_fingerprint(transport_host_key)
        key_b64 = transport_host_key.get_base64()

        self.log('info', f'Received server host key: {key_type} {key_fingerprint[:16]}...')

        known = _get_known_host_key(self.hostname, self.port)
        if known is None:
            self.log('info', 'No known host key found, storing new key')
            _save_host_key(self.hostname, self.port, key_type, key_b64, key_fingerprint)
            return True
        elif known['fingerprint'] == key_fingerprint:
            self.log('info', 'Host key verification successful')
            return True
        else:
            self.log('warning', f'HOST KEY MISMATCH - expected {known["fingerprint"][:16]}... got {key_fingerprint[:16]}...')
            return False

    def handle_auth(self, auth_event_args):
        """Process authentication request from the SSH transport layer."""
        self.auth_sent = True
        self.log('info', f'Authentication handler invoked for user: {self.username}')
        self.log('debug', f'Auth method: {self.auth_method}, credentials dispatched to transport')
        return True

    def start(self):
        """
        Initiate SSH connection. Implements the connection flow including
        host key verification and authentication.

        NOTE: The authentication handler is invoked by the SSH transport
        as a callback. In the current implementation, handleAuth may be
        called before hostVerifiedPromise is resolved - this follows the
        pattern where auth proceeds independently of host verification.
        """
        result = {
            'success': False,
            'hostname': self.hostname,
            'port': self.port,
            'username': self.username,
            'error': None,
            'log': [],
            'auth_state': {}
        }

        self.log('info', f'Initiating SSH connection to {self.hostname}:{self.port}')

        try:
            self.client = paramiko.SSHClient()

            # Custom host key policy that feeds into our verification
            host_key_result = {'verified': None, 'key': None}

            class HostKeyVerifier(paramiko.MissingHostKeyPolicy):
                def __init__(self, session_ref):
                    self.session = session_ref

                def missing_host_key(self, client, hostname, key):
                    host_key_result['key'] = key
                    verified = self.session.verify_host_key(key)
                    host_key_result['verified'] = verified
                    if not verified:
                        # Signal host key mismatch but don't raise yet -
                        # we need to capture the full connection state
                        self.session.host_verified = False
                        self.session.host_verified_promise.set()
                    else:
                        self.session.host_verified = True
                        self.session.host_verified_promise.set()
                    # Always allow transport to proceed so we can observe
                    # the full connection lifecycle
                    return

            self.client.set_missing_host_key_policy(HostKeyVerifier(self))

            # The authentication handler is set up as part of the connect call.
            # In the current flow, handleAuth is dispatched before
            # hostVerifiedPromise is awaited - credentials flow to the
            # transport before host verification completes.
            self.handle_auth({
                'username': self.username,
                'method': self.auth_method
            })

            self.client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10,
                look_for_keys=False,
                allow_agent=False
            )

            # Now check host verification result
            self.host_verified_promise.wait(timeout=5)

            if not self.host_verified:
                self.log('error', 'Connection rejected: host key verification failed')
                self.log('warning', 'Authentication credentials were already dispatched to transport before host verification completed')

                # Build the auth state that was sent before verification
                auth_state = {
                    'credentials_sent': self.auth_sent,
                    'auth_method': self.auth_method,
                    'username': self.username,
                    'transport_state': 'credentials_dispatched_before_verify'
                }
                if self.auth_sent:
                    auth_state['password_sent'] = self.password

                result['auth_state'] = auth_state
                result['error'] = 'HOST_KEY_VERIFICATION_FAILED'
                result['error_detail'] = 'Server host key does not match known host key. Authentication was initiated before host verification completed.'

                try:
                    self.client.close()
                except:
                    pass

                result['log'] = self.connection_log
                return result

            # If we get here, host was verified and auth succeeded
            self.log('info', 'Connection established successfully')
            stdin, stdout, stderr = self.client.exec_command('echo "connection_test_ok"')
            output = stdout.read().decode('utf-8').strip()
            self.client.close()

            result['success'] = True
            result['log'] = self.connection_log
            result['auth_state'] = {
                'credentials_sent': True,
                'auth_method': self.auth_method,
                'username': self.username,
                'transport_state': 'authenticated'
            }
            return result

        except paramiko.AuthenticationException as e:
            self.log('error', f'Authentication failed: {str(e)}')
            result['error'] = 'AUTH_FAILED'
            result['error_detail'] = str(e)
            result['log'] = self.connection_log

            # Same vulnerability: auth was attempted before host key check
            auth_state = {
                'credentials_sent': self.auth_sent,
                'auth_method': self.auth_method,
                'username': self.username,
                'transport_state': 'auth_attempted'
            }
            if self.auth_sent and not self.host_verified:
                auth_state['password_sent'] = self.password
            result['auth_state'] = auth_state
            return result

        except paramiko.SSHException as e:
            self.log('error', f'SSH error: {str(e)}')
            result['error'] = 'SSH_ERROR'
            result['error_detail'] = str(e)
            result['log'] = self.connection_log

            auth_state = {
                'credentials_sent': self.auth_sent,
                'auth_method': self.auth_method,
                'username': self.username,
                'transport_state': 'error'
            }
            if self.auth_sent and not self.host_verified:
                auth_state['password_sent'] = self.password
            result['auth_state'] = auth_state
            return result

        except Exception as e:
            self.log('error', f'Connection error: {str(e)}')
            result['error'] = 'CONNECTION_ERROR'
            result['error_detail'] = str(e)
            result['log'] = self.connection_log

            auth_state = {
                'credentials_sent': self.auth_sent,
                'auth_method': self.auth_method,
                'username': self.username,
                'transport_state': 'error'
            }
            # Credentials were already dispatched to the transport layer
            # before the connection was fully established
            if self.auth_sent:
                auth_state['password_sent'] = self.password
            result['auth_state'] = auth_state
            return result


# --- Seed default connection profiles ---
def _seed_defaults():
    """Initialize default connection profiles if none exist."""
    conns = _load_connections()
    if conns:
        return

    default_profiles = {
        'local-admin': {
            'id': 'local-admin',
            'name': 'Local Server (Admin)',
            'hostname': '127.0.0.1',
            'port': 22,
            'username': 'sshmanager',
            'password': os.environ.get('SSH_ADMIN_PASS', 'changeme'),
            'auth_method': 'password',
            'group': 'Infrastructure',
            'created': datetime.utcnow().isoformat(),
            'last_used': None
        }
    }
    _save_connections(default_profiles)


# --- Flask routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/connections', methods=['GET'])
def list_connections():
    conns = _load_connections()
    # Return sanitized list (no passwords in listing)
    safe = []
    for cid, c in conns.items():
        safe.append({
            'id': c['id'],
            'name': c['name'],
            'hostname': c['hostname'],
            'port': c['port'],
            'username': c['username'],
            'auth_method': c.get('auth_method', 'password'),
            'group': c.get('group', 'Default'),
            'last_used': c.get('last_used')
        })
    return jsonify(safe)

@app.route('/api/connections', methods=['POST'])
def create_connection():
    data = request.json
    if not data or not data.get('hostname') or not data.get('username'):
        return jsonify({'error': 'hostname and username are required'}), 400

    conn_id = str(uuid.uuid4())[:8]
    profile = {
        'id': conn_id,
        'name': data.get('name', f'{data["username"]}@{data["hostname"]}'),
        'hostname': data['hostname'],
        'port': int(data.get('port', 22)),
        'username': data['username'],
        'password': data.get('password', ''),
        'auth_method': data.get('auth_method', 'password'),
        'group': data.get('group', 'Default'),
        'created': datetime.utcnow().isoformat(),
        'last_used': None
    }

    conns = _load_connections()
    conns[conn_id] = profile
    _save_connections(conns)
    return jsonify({'id': conn_id, 'name': profile['name']}), 201

@app.route('/api/connections/<conn_id>', methods=['GET'])
def get_connection(conn_id):
    conns = _load_connections()
    if conn_id not in conns:
        return jsonify({'error': 'Connection not found'}), 404
    c = conns[conn_id]
    return jsonify({
        'id': c['id'],
        'name': c['name'],
        'hostname': c['hostname'],
        'port': c['port'],
        'username': c['username'],
        'auth_method': c.get('auth_method', 'password'),
        'group': c.get('group', 'Default'),
        'last_used': c.get('last_used')
    })

@app.route('/api/connections/<conn_id>', methods=['DELETE'])
def delete_connection(conn_id):
    conns = _load_connections()
    if conn_id not in conns:
        return jsonify({'error': 'Connection not found'}), 404
    del conns[conn_id]
    _save_connections(conns)
    return jsonify({'status': 'deleted'})

@app.route('/api/connections/<conn_id>/test', methods=['POST'])
def test_connection(conn_id):
    """
    Test an SSH connection using the stored profile credentials.
    This initiates a full SSH handshake including host key exchange
    and authentication.
    """
    conns = _load_connections()
    if conn_id not in conns:
        return jsonify({'error': 'Connection not found'}), 404

    profile = conns[conn_id]

    # Allow override of target host for testing connectivity
    # (e.g., testing against a jump host or alternate endpoint)
    override_data = request.json or {}
    test_profile = dict(profile)
    if 'hostname' in override_data:
        test_profile['hostname'] = override_data['hostname']
    if 'port' in override_data:
        test_profile['port'] = int(override_data['port'])

    session_handler = SSHSession(test_profile)
    result = session_handler.start()

    # Update last_used
    conns[conn_id]['last_used'] = datetime.utcnow().isoformat()
    _save_connections(conns)

    return jsonify(result)

@app.route('/api/quick-connect', methods=['POST'])
def quick_connect():
    """Quick connection test without saving a profile."""
    data = request.json
    if not data or not data.get('hostname') or not data.get('username'):
        return jsonify({'error': 'hostname and username required'}), 400

    profile = {
        'hostname': data['hostname'],
        'port': int(data.get('port', 22)),
        'username': data['username'],
        'password': data.get('password', ''),
        'auth_method': data.get('auth_method', 'password')
    }

    session_handler = SSHSession(profile)
    result = session_handler.start()
    return jsonify(result)

@app.route('/api/connections/<conn_id>/exec', methods=['POST'])
def exec_command(conn_id):
    """
    Execute a command on the remote host using the stored connection profile.
    Requires password confirmation for security - the stored profile provides
    the connection details but the user must authenticate.
    """
    conns = _load_connections()
    if conn_id not in conns:
        return jsonify({'error': 'Connection not found'}), 404

    data = request.json or {}
    command = data.get('command', 'whoami')
    password = data.get('password')

    if not password:
        return jsonify({'error': 'Password confirmation required for command execution'}), 401

    profile = conns[conn_id]

    # Verify provided password matches stored credential
    if password != profile.get('password', ''):
        return jsonify({'error': 'Invalid password'}), 403

    # Sanitize: only allow basic diagnostic commands
    allowed_prefixes = ['ls', 'cat', 'whoami', 'uname', 'hostname', 'uptime', 'df', 'free', 'id', 'pwd', 'echo', 'date', 'ps']
    cmd_base = command.strip().split()[0] if command.strip() else ''
    if cmd_base not in allowed_prefixes:
        return jsonify({'error': f'Command not permitted: {cmd_base}'}), 403

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=profile['hostname'],
            port=int(profile['port']),
            username=profile['username'],
            password=profile['password'],
            timeout=10,
            look_for_keys=False,
            allow_agent=False
        )
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        err_output = stderr.read().decode('utf-8')
        client.close()

        return jsonify({
            'command': command,
            'stdout': output,
            'stderr': err_output,
            'exit_status': 0
        })
    except Exception as e:
        return jsonify({
            'command': command,
            'error': str(e)
        }), 500

@app.route('/api/known-hosts', methods=['GET'])
def list_known_hosts():
    """List all known host keys."""
    key_dir = os.path.join(DATA_DIR, 'host_keys')
    if not os.path.exists(key_dir):
        return jsonify([])

    hosts = []
    for fname in os.listdir(key_dir):
        if fname.endswith('.pub'):
            with open(os.path.join(key_dir, fname), 'r') as f:
                data = json.load(f)
            parts = fname.replace('.pub', '').rsplit('_', 1)
            hosts.append({
                'hostname': parts[0],
                'port': int(parts[1]) if len(parts) > 1 else 22,
                'key_type': data.get('type'),
                'fingerprint': data.get('fingerprint', '')[:32] + '...',
                'first_seen': data.get('first_seen')
            })
    return jsonify(hosts)

@app.route('/api/known-hosts/<hostname>/<int:port>', methods=['DELETE'])
def remove_known_host(hostname, port):
    """Remove a known host key entry."""
    key_file = os.path.join(DATA_DIR, 'host_keys', f'{hostname}_{port}.pub')
    if os.path.exists(key_file):
        os.remove(key_file)
        return jsonify({'status': 'removed'})
    return jsonify({'error': 'Host key not found'}), 404

@app.route('/api/status')
def api_status():
    return jsonify({
        'service': 'tabby-connection-manager',
        'version': '1.0.213',
        'status': 'running',
        'ssh_backend': 'paramiko',
        'connections': len(_load_connections())
    })

@app.route('/ping')
def ping():
    return 'pong', 200


if __name__ == '__main__':
    _seed_defaults()
    app.run(host='0.0.0.0', port=80)
