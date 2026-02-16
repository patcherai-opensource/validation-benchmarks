import os
import json
import uuid
import hashlib
import secrets
from functools import wraps
from datetime import datetime, timezone

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort
from markupsafe import escape
from jinja2 import Template, Environment, BaseLoader, SandboxedEnvironment

app = Flask(__name__, static_folder='static/')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

USERS = {
    'admin': {
        'password_hash': hashlib.sha256('admin'.encode()).hexdigest(),
        'user_id': 1,
        'role': 'admin',
        'status': 'active',
        'last_team_id': 1
    },
    'operator': {
        'password_hash': hashlib.sha256('operator'.encode()).hexdigest(),
        'user_id': 2,
        'role': 'user',
        'status': 'active',
        'last_team_id': 1
    }
}

notification_configs = {}
notification_log = []

JOB_REGISTRY = {
    '1': {'name': 'etl-daily-ingest', 'status': 'RUNNING', 'mode': 'kubernetes-session', 'start_time': '2024-01-15 08:00:00', 'cluster': 'prod-k8s-01'},
    '2': {'name': 'stream-clickstream', 'status': 'RUNNING', 'mode': 'kubernetes-application', 'start_time': '2024-01-14 12:30:00', 'cluster': 'prod-k8s-01'},
    '3': {'name': 'cdc-postgres-sync', 'status': 'FAILED', 'mode': 'yarn-application', 'start_time': '2024-01-13 06:00:00', 'cluster': 'hadoop-prod'},
    '4': {'name': 'metrics-aggregator', 'status': 'RUNNING', 'mode': 'kubernetes-session', 'start_time': '2024-01-15 00:00:00', 'cluster': 'prod-k8s-02'},
}

CLUSTER_REGISTRY = {
    'prod-k8s-01': {'type': 'kubernetes', 'address': 'https://k8s-api.internal:6443', 'status': 'ACTIVE', 'slots_total': 48, 'slots_used': 32},
    'prod-k8s-02': {'type': 'kubernetes', 'address': 'https://k8s-api-2.internal:6443', 'status': 'ACTIVE', 'slots_total': 64, 'slots_used': 18},
    'hadoop-prod': {'type': 'yarn', 'address': 'http://yarn-rm.internal:8088', 'status': 'ACTIVE', 'slots_total': 128, 'slots_used': 96},
}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.content_type == 'application/json':
                return jsonify({'code': 401, 'message': 'Authentication required'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))


@app.route('/passport/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/passport/signin', methods=['POST'])
def signin():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    login_type = request.form.get('loginType', 'account')

    if not username or not password:
        return render_template('login.html', error='Username and password are required')

    user = USERS.get(username)
    if user is None:
        return render_template('login.html', error='Invalid credentials')

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash != user['password_hash']:
        return render_template('login.html', error='Invalid credentials')

    if user['status'] != 'active':
        return render_template('login.html', error='Account is locked')

    session['user_id'] = user['user_id']
    session['username'] = username
    session['role'] = user['role']
    session['team_id'] = user['last_team_id']

    return redirect(url_for('dashboard'))


@app.route('/passport/signout', methods=['POST', 'GET'])
def signout():
    session.clear()
    return redirect(url_for('login_page'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',
                           jobs=JOB_REGISTRY,
                           clusters=CLUSTER_REGISTRY,
                           username=session.get('username'))


@app.route('/job/list', methods=['GET'])
@login_required
def job_list():
    return render_template('jobs.html', jobs=JOB_REGISTRY, username=session.get('username'))


@app.route('/cluster/list', methods=['GET'])
@login_required
def cluster_list():
    return render_template('clusters.html', clusters=CLUSTER_REGISTRY, username=session.get('username'))


@app.route('/setting/notification', methods=['GET'])
@login_required
def notification_settings():
    user_configs = {k: v for k, v in notification_configs.items()
                    if v.get('user_id') == session['user_id']}
    return render_template('notifications.html',
                           configs=user_configs,
                           username=session.get('username'))


@app.route('/setting/notification/add', methods=['POST'])
@login_required
def notification_add():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        alert_name = data.get('alertName', '').strip()
        alert_type = int(data.get('alertType', 8))
        webhook_url = data.get('webhookUrl', '').strip()
        method = data.get('method', 'POST').upper()
        content_type = data.get('contentType', 'application/json')
        message_template = data.get('messageTemplate', '')

        if not alert_name:
            return jsonify({'code': 400, 'message': 'Notification name is required'}), 400

        config_id = str(uuid.uuid4().hex[:8])
        notification_configs[config_id] = {
            'id': config_id,
            'user_id': session['user_id'],
            'alertName': alert_name,
            'alertType': alert_type,
            'webhookUrl': webhook_url,
            'method': method,
            'contentType': content_type,
            'messageTemplate': message_template,
            'created': datetime.now(timezone.utc).isoformat(),
            'modified': datetime.now(timezone.utc).isoformat()
        }

        if request.is_json:
            return jsonify({'code': 200, 'data': True, 'message': 'Notification config saved'})
        return redirect(url_for('notification_settings'))

    except Exception:
        if request.is_json:
            return jsonify({'code': 500, 'message': 'Internal server error'}), 500
        return redirect(url_for('notification_settings'))


@app.route('/setting/notification/update', methods=['POST'])
@login_required
def notification_update():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        config_id = data.get('id', '').strip()
        if config_id not in notification_configs:
            return jsonify({'code': 404, 'message': 'Config not found'}), 404

        config = notification_configs[config_id]
        if config['user_id'] != session['user_id']:
            return jsonify({'code': 403, 'message': 'Access denied'}), 403

        if 'alertName' in data:
            config['alertName'] = data['alertName'].strip()
        if 'webhookUrl' in data:
            config['webhookUrl'] = data['webhookUrl'].strip()
        if 'method' in data:
            config['method'] = data['method'].upper()
        if 'contentType' in data:
            config['contentType'] = data['contentType']
        if 'messageTemplate' in data:
            config['messageTemplate'] = data['messageTemplate']
        config['modified'] = datetime.now(timezone.utc).isoformat()

        if request.is_json:
            return jsonify({'code': 200, 'data': True, 'message': 'Config updated'})
        return redirect(url_for('notification_settings'))

    except Exception:
        if request.is_json:
            return jsonify({'code': 500, 'message': 'Internal server error'}), 500
        return redirect(url_for('notification_settings'))


@app.route('/setting/notification/get', methods=['POST'])
@login_required
def notification_get():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    config_id = data.get('id', '').strip()
    if config_id not in notification_configs:
        return jsonify({'code': 404, 'message': 'Not found'}), 404

    config = notification_configs[config_id]
    if config['user_id'] != session['user_id']:
        return jsonify({'code': 403, 'message': 'Access denied'}), 403

    return jsonify({'code': 200, 'data': config})


@app.route('/setting/notification/list', methods=['GET', 'POST'])
@login_required
def notification_list():
    user_configs = {k: v for k, v in notification_configs.items()
                    if v.get('user_id') == session['user_id']}
    return jsonify({'code': 200, 'data': list(user_configs.values())})


@app.route('/setting/notification/delete', methods=['POST', 'DELETE'])
@login_required
def notification_delete():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    config_id = data.get('id', '').strip()
    if config_id not in notification_configs:
        return jsonify({'code': 404, 'message': 'Not found'}), 404

    config = notification_configs[config_id]
    if config['user_id'] != session['user_id']:
        return jsonify({'code': 403, 'message': 'Access denied'}), 403

    del notification_configs[config_id]
    return jsonify({'code': 200, 'data': True})


@app.route('/setting/notification/test', methods=['POST'])
@login_required
def notification_test():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    config_id = data.get('id', '').strip()
    if config_id not in notification_configs:
        return jsonify({'code': 404, 'message': 'Notification config not found'}), 404

    config = notification_configs[config_id]
    if config['user_id'] != session['user_id']:
        return jsonify({'code': 403, 'message': 'Access denied'}), 403

    message_template = config.get('messageTemplate', '')
    if not message_template:
        return jsonify({'code': 400, 'message': 'No message template configured'}), 400

    alert_context = {
        'title': 'Platform Alert: test notification',
        'jobName': 'test-notification-job',
        'subject': 'Alert Test',
        'status': 'TEST',
        'type': 1,
        'startTime': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        'endTime': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        'duration': '-',
        'restart': False
    }

    try:
        env = Environment(loader=BaseLoader())
        tpl = env.from_string(message_template)
        rendered = tpl.render(**alert_context)
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Template rendering failed: {}'.format(type(e).__name__)}), 500

    notification_log.append({
        'config_id': config_id,
        'rendered': rendered,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

    return jsonify({
        'code': 200,
        'data': True,
        'message': 'Test notification sent successfully',
        'preview': rendered
    })


@app.route('/setting/variable', methods=['GET'])
@login_required
def variable_settings():
    return render_template('variables.html', username=session.get('username'))


@app.route('/ping')
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now(timezone.utc).isoformat()})


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run()
