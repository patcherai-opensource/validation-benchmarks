import os
import json
import uuid
import hashlib
import logging
import threading
import socket
import time
from datetime import datetime, timedelta
from functools import wraps

import paramiko
from paramiko import RSAKey
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = os.urandom(32)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('gateway')

PROFILES_DB = os.path.join(os.path.dirname(__file__), 'data', 'profiles.json')
KNOWN_HOSTS_DB = os.path.join(os.path.dirname(__file__), 'data', 'known_hosts.json')
CONNECTION_LOG_DB = os.path.join(os.path.dirname(__file__), 'data', 'connection_log.json')
HOST_KEYS_DIR = os.path.join(os.path.dirname(__file__), 'data', 'host_keys')

ADMIN_USER = 'admin'
ADMIN_PASS_HASH = None

_lock = threading.Lock()


def _read_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def _hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def _get_admin_pass_hash():
    global ADMIN_PASS_HASH
    if ADMIN_PASS_HASH is None:
        pw_file = os.path.join(os.path.dirname(__file__), 'data', '.admin_pw')
        if os.path.exists(pw_file):
            with open(pw_file, 'r') as f:
                ADMIN_PASS_HASH = f.read().strip()
    return ADMIN_PASS_HASH


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def _append_connection_log(entry):
    with _lock:
        logs = _read_json(CONNECTION_LOG_DB)
        logs.append(entry)
        if len(logs) > 500:
            logs = logs[-500:]
        _write_json(CONNECTION_LOG_DB, logs)


def _get_known_hosts():
    return _read_json(KNOWN_HOSTS_DB)


def _save_known_hosts(hosts):
    _write_json(KNOWN_HOSTS_DB, hosts)


def _compute_host_fingerprint(key):
    key_bytes = key.asbytes()
    return hashlib.sha256(key_bytes).hexdigest()


def _check_host_trust(hostname, port, server_key):
    fingerprint = _compute_host_fingerprint(server_key)
    known = _get_known_hosts()
    host_entries = [
        e for e in known
        if e.get('host') == hostname and e.get('port') == port
    ]
    if not host_entries:
        return None, fingerprint
    for entry in host_entries:
        if entry.get('fingerprint') == fingerprint:
            return True, fingerprint
    return False, fingerprint


def _initiate_remote_session(profile, target_host=None, target_port=None):
    """
    Establish SSH connection to a remote host using profile credentials.
    Mirrors the connection flow: handshake, then auth, then host verification.
    """
    connect_host = target_host or profile.get('host', 'localhost')
    connect_port = int(target_port or profile.get('port', 22))
    profile_host = profile.get('host', connect_host)
    profile_port = int(profile.get('port', connect_port))
    username = profile.get('user', '')
    password = profile.get('credential', '')

    transport = None
    auth_dispatched = False
    dispatched_credentials = None
    verification_error = None
    result = {
        'status': 'unknown',
        'host': connect_host,
        'port': connect_port,
        'user': username,
        'timestamp': datetime.utcnow().isoformat(),
        'host_key_fingerprint': None,
        'auth_methods_attempted': [],
    }

    try:
        sock = socket.create_connection((connect_host, connect_port), timeout=8)
    except Exception as e:
        result['status'] = 'connection_failed'
        result['error'] = f'Could not reach {connect_host}:{connect_port}'
        return result

    try:
        transport = paramiko.Transport(sock)
        transport.start_client()

        server_key = transport.get_remote_server_key()
        result['host_key_type'] = server_key.get_name()
        result['host_key_fingerprint'] = _compute_host_fingerprint(server_key)

        # Authenticate with remote server
        try:
            transport.auth_password(username, password)
            auth_dispatched = True
            dispatched_credentials = {'user': username, 'credential': password}
            result['auth_methods_attempted'].append('password')
        except paramiko.AuthenticationException:
            auth_dispatched = True
            dispatched_credentials = {'user': username, 'credential': password}
            result['auth_methods_attempted'].append('password')
            result['auth_result'] = 'rejected'
        except Exception:
            auth_dispatched = True
            dispatched_credentials = {'user': username, 'credential': password}
            result['auth_methods_attempted'].append('password')
            result['auth_result'] = 'error'

        # Verify host key against known hosts using profile's configured host
        trust_status, fingerprint = _check_host_trust(
            profile_host, profile_port, server_key
        )

        if trust_status is None:
            result['status'] = 'host_unknown'
            result['host_verification'] = 'unknown_host'
            verification_error = 'Host key not found in known hosts'
        elif trust_status is False:
            result['status'] = 'host_key_mismatch'
            result['host_verification'] = 'MISMATCH'
            verification_error = 'Host key verification failed'
        else:
            result['host_verification'] = 'verified'
            if result.get('auth_result') != 'rejected':
                result['status'] = 'connected'
            else:
                result['status'] = 'auth_failed'

    except Exception as e:
        result['status'] = 'transport_error'
        result['error'] = str(e)
    finally:
        if transport:
            try:
                transport.close()
            except Exception:
                pass

    if auth_dispatched and dispatched_credentials and verification_error:
        result['transmitted_auth'] = dispatched_credentials

    return result


@app.route('/')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        expected = _get_admin_pass_hash()
        if username == ADMIN_USER and expected and _hash_password(password) == expected:
            session['authenticated'] = True
            session['user'] = username
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/api/v1/profiles', methods=['GET'])
@login_required
def list_profiles():
    profiles = _read_json(PROFILES_DB)
    safe_profiles = []
    for p in profiles:
        safe_profiles.append({
            'id': p.get('id'),
            'name': p.get('name'),
            'host': p.get('host'),
            'port': p.get('port'),
            'user': p.get('user'),
            'auth_type': p.get('auth_type', 'password'),
            'created_at': p.get('created_at'),
        })
    return jsonify(safe_profiles)


@app.route('/api/v1/profiles', methods=['POST'])
@login_required
def create_profile():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('host') or not data.get('user'):
        return jsonify({'error': 'Missing required fields: name, host, user'}), 400

    profiles = _read_json(PROFILES_DB)
    profile = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'host': data['host'],
        'port': int(data.get('port', 22)),
        'user': data['user'],
        'credential': data.get('credential', ''),
        'auth_type': data.get('auth_type', 'password'),
        'created_at': datetime.utcnow().isoformat(),
    }
    profiles.append(profile)
    _write_json(PROFILES_DB, profiles)
    return jsonify({'id': profile['id'], 'name': profile['name']}), 201


@app.route('/api/v1/profiles/<profile_id>', methods=['GET'])
@login_required
def get_profile(profile_id):
    profiles = _read_json(PROFILES_DB)
    for p in profiles:
        if p['id'] == profile_id:
            return jsonify({
                'id': p.get('id'),
                'name': p.get('name'),
                'host': p.get('host'),
                'port': p.get('port'),
                'user': p.get('user'),
                'auth_type': p.get('auth_type', 'password'),
                'created_at': p.get('created_at'),
            })
    return jsonify({'error': 'Profile not found'}), 404


@app.route('/api/v1/profiles/<profile_id>', methods=['DELETE'])
@login_required
def delete_profile(profile_id):
    profiles = _read_json(PROFILES_DB)
    new_profiles = [p for p in profiles if p['id'] != profile_id]
    if len(new_profiles) == len(profiles):
        return jsonify({'error': 'Profile not found'}), 404
    _write_json(PROFILES_DB, new_profiles)
    return jsonify({'status': 'deleted'})


@app.route('/api/v1/connect/test', methods=['POST'])
@login_required
def test_connection():
    data = request.get_json()
    if not data or not data.get('profile_id'):
        return jsonify({'error': 'profile_id is required'}), 400

    profile_id = data['profile_id']
    target_host = data.get('target_host')
    target_port = data.get('target_port')

    profiles = _read_json(PROFILES_DB)
    profile = None
    for p in profiles:
        if p['id'] == profile_id:
            profile = p
            break

    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    result = _initiate_remote_session(
        profile,
        target_host=target_host,
        target_port=target_port,
    )

    _append_connection_log(result)

    return jsonify(result)


@app.route('/api/v1/connect/quick', methods=['POST'])
@login_required
def quick_connect():
    data = request.get_json()
    if not data or not data.get('host') or not data.get('user'):
        return jsonify({'error': 'host and user are required'}), 400

    temp_profile = {
        'host': data['host'],
        'port': int(data.get('port', 22)),
        'user': data['user'],
        'credential': data.get('credential', ''),
    }

    result = _initiate_remote_session(temp_profile)
    _append_connection_log(result)
    return jsonify(result)


@app.route('/api/v1/known-hosts', methods=['GET'])
@login_required
def list_known_hosts():
    return jsonify(_get_known_hosts())


@app.route('/api/v1/known-hosts', methods=['POST'])
@login_required
def add_known_host():
    data = request.get_json()
    if not data or not data.get('host') or not data.get('fingerprint'):
        return jsonify({'error': 'host and fingerprint required'}), 400

    hosts = _get_known_hosts()
    entry = {
        'host': data['host'],
        'port': int(data.get('port', 22)),
        'fingerprint': data['fingerprint'],
        'key_type': data.get('key_type', 'ssh-rsa'),
        'added_at': datetime.utcnow().isoformat(),
    }

    hosts = [h for h in hosts if not (h['host'] == entry['host'] and h['port'] == entry['port'])]
    hosts.append(entry)
    _save_known_hosts(hosts)
    return jsonify({'status': 'added'})


@app.route('/api/v1/known-hosts', methods=['DELETE'])
@login_required
def remove_known_host():
    data = request.get_json()
    if not data or not data.get('host'):
        return jsonify({'error': 'host required'}), 400

    host = data['host']
    port = int(data.get('port', 22))
    hosts = _get_known_hosts()
    new_hosts = [h for h in hosts if not (h['host'] == host and h['port'] == port)]
    _save_known_hosts(new_hosts)
    return jsonify({'status': 'removed'})


@app.route('/api/v1/logs', methods=['GET'])
@login_required
def get_connection_logs():
    logs = _read_json(CONNECTION_LOG_DB)
    limit = request.args.get('limit', 50, type=int)
    return jsonify(logs[-limit:])


@app.route('/api/v1/settings', methods=['GET'])
@login_required
def get_settings():
    return jsonify({
        'verify_host_keys': True,
        'keepalive_interval': 15000,
        'keepalive_count_max': 3,
        'ready_timeout': 20000,
        'agent_type': 'auto',
        'version': '1.0.213',
    })


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

