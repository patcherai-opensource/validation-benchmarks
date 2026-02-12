import json
import traceback
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, render_template_string,
    redirect, url_for, request, session, Response, jsonify
)

from app import app
from app.db import db
from app.models import User, Application, AlertConfig, AlertHistory


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        user = User.query.get(user_id)
        if not user or user.status != 1:
            session.pop('user_id', None)
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers.pop('Server', None)
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page Not Found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500, message='Internal Server Error'), 500


@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user and user.status == 1:
            session['user_id'] = user.id
            user.last_login_time = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials or account locked')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    applications = Application.query.order_by(Application.create_time.desc()).all()
    return render_template('dashboard.html', user=user, applications=applications)


@app.route('/flink/app/list')
@login_required
def app_list():
    applications = Application.query.order_by(Application.create_time.desc()).all()
    result = []
    for a in applications:
        result.append({
            'id': a.id,
            'appName': a.app_name,
            'appType': a.app_type,
            'executionMode': a.execution_mode,
            'state': a.state,
            'jobId': a.job_id,
            'clusterId': a.cluster_id,
            'userId': a.user_id,
            'alertId': a.alert_id,
            'createTime': a.create_time.isoformat() if a.create_time else None,
            'description': a.description
        })
    return jsonify({'code': 200, 'data': result})


@app.route('/flink/app/get', methods=['GET'])
@login_required
def app_get():
    app_id = request.args.get('id', type=int)
    if not app_id:
        return jsonify({'code': 400, 'message': 'Missing application id'}), 400
    application = Application.query.get(app_id)
    if not application:
        return jsonify({'code': 404, 'message': 'Application not found'}), 404
    return jsonify({
        'code': 200,
        'data': {
            'id': application.id,
            'appName': application.app_name,
            'appType': application.app_type,
            'executionMode': application.execution_mode,
            'state': application.state,
            'jobId': application.job_id,
            'clusterId': application.cluster_id,
            'userId': application.user_id,
            'alertId': application.alert_id,
            'createTime': application.create_time.isoformat() if application.create_time else None,
            'description': application.description
        }
    })


@app.route('/flink/alert/list')
@login_required
def alert_list():
    user_id = session['user_id']
    user = User.query.get(user_id)
    # Admin sees all; regular users see only their own
    if user.user_type == 1:
        alerts = AlertConfig.query.order_by(AlertConfig.create_time.desc()).all()
    else:
        alerts = AlertConfig.query.filter_by(user_id=user_id).order_by(AlertConfig.create_time.desc()).all()
    result = []
    for a in alerts:
        result.append({
            'id': a.id,
            'userId': a.user_id,
            'alertName': a.alert_name,
            'alertType': a.alert_type,
            'httpCallbackUrl': a.http_callback_url,
            'httpCallbackMethod': a.http_callback_method,
            'httpCallbackContentType': a.http_callback_content_type,
            'httpCallbackRequestTemplate': a.http_callback_request_template,
            'isEnabled': a.is_enabled,
            'createTime': a.create_time.isoformat() if a.create_time else None
        })
    return jsonify({'code': 200, 'data': result})


@app.route('/flink/alert/add', methods=['POST'])
@login_required
def alert_add():
    user_id = session['user_id']
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    alert_name = data.get('alertName', '').strip()
    if not alert_name:
        return jsonify({'code': 400, 'message': 'Alert name is required'}), 400

    alert_type = int(data.get('alertType', 4))

    http_params = data.get('httpCallbackParams', {})
    if isinstance(http_params, str):
        try:
            http_params = json.loads(http_params)
        except (json.JSONDecodeError, TypeError):
            http_params = {}

    alert_config = AlertConfig(
        user_id=user_id,
        alert_name=alert_name,
        alert_type=alert_type,
        http_callback_url=http_params.get('url', data.get('httpCallbackUrl', '')),
        http_callback_method=http_params.get('method', data.get('httpCallbackMethod', 'POST')),
        http_callback_header=http_params.get('header', data.get('httpCallbackHeader', '')),
        http_callback_content_type=http_params.get('contentType', data.get('httpCallbackContentType', 'application/json')),
        http_callback_request_template=http_params.get('requestTemplate', data.get('httpCallbackRequestTemplate', '')),
        is_enabled=True
    )
    db.session.add(alert_config)
    db.session.commit()

    return jsonify({'code': 200, 'message': 'Alert config created successfully', 'data': {'id': alert_config.id}})


@app.route('/flink/alert/update', methods=['POST', 'PUT'])
@login_required
def alert_update():
    user_id = session['user_id']
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    alert_id = data.get('id')
    if not alert_id:
        return jsonify({'code': 400, 'message': 'Alert config id is required'}), 400

    alert_config = AlertConfig.query.get(int(alert_id))
    if not alert_config:
        return jsonify({'code': 404, 'message': 'Alert config not found'}), 404

    user = User.query.get(user_id)
    if user.user_type != 1 and alert_config.user_id != user_id:
        return jsonify({'code': 403, 'message': 'Permission denied'}), 403

    if 'alertName' in data:
        alert_config.alert_name = data['alertName']
    if 'alertType' in data:
        alert_config.alert_type = int(data['alertType'])

    http_params = data.get('httpCallbackParams', {})
    if isinstance(http_params, str):
        try:
            http_params = json.loads(http_params)
        except (json.JSONDecodeError, TypeError):
            http_params = {}

    if http_params:
        if 'url' in http_params:
            alert_config.http_callback_url = http_params['url']
        if 'method' in http_params:
            alert_config.http_callback_method = http_params['method']
        if 'header' in http_params:
            alert_config.http_callback_header = http_params['header']
        if 'contentType' in http_params:
            alert_config.http_callback_content_type = http_params['contentType']
        if 'requestTemplate' in http_params:
            alert_config.http_callback_request_template = http_params['requestTemplate']
    else:
        if 'httpCallbackUrl' in data:
            alert_config.http_callback_url = data['httpCallbackUrl']
        if 'httpCallbackMethod' in data:
            alert_config.http_callback_method = data['httpCallbackMethod']
        if 'httpCallbackRequestTemplate' in data:
            alert_config.http_callback_request_template = data['httpCallbackRequestTemplate']

    if 'isEnabled' in data:
        alert_config.is_enabled = bool(data['isEnabled'])

    db.session.commit()
    return jsonify({'code': 200, 'message': 'Alert config updated successfully'})


@app.route('/flink/alert/delete', methods=['POST', 'DELETE'])
@login_required
def alert_delete():
    user_id = session['user_id']
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    alert_id = data.get('id')
    if not alert_id:
        return jsonify({'code': 400, 'message': 'Alert config id is required'}), 400

    alert_config = AlertConfig.query.get(int(alert_id))
    if not alert_config:
        return jsonify({'code': 404, 'message': 'Alert config not found'}), 404

    user = User.query.get(user_id)
    if user.user_type != 1 and alert_config.user_id != user_id:
        return jsonify({'code': 403, 'message': 'Permission denied'}), 403

    AlertHistory.query.filter_by(alert_config_id=alert_config.id).delete()
    db.session.delete(alert_config)
    db.session.commit()
    return jsonify({'code': 200, 'message': 'Alert config deleted successfully'})


def render_alert_template(request_template, alert_data):
    """
    Renders the HTTP callback request template with alert context data.
    Uses Jinja2 template rendering to substitute placeholders.
    """
    try:
        rendered = render_template_string(request_template, **alert_data)
        return rendered
    except Exception as e:
        return None


@app.route('/flink/alert/send', methods=['POST'])
@login_required
def alert_send():
    """Send a test alert using the specified alert configuration."""
    user_id = session['user_id']
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    alert_id = data.get('id')
    if not alert_id:
        return jsonify({'code': 400, 'message': 'Alert config id is required'}), 400

    alert_config = AlertConfig.query.get(int(alert_id))
    if not alert_config:
        return jsonify({'code': 404, 'message': 'Alert config not found'}), 404

    if not alert_config.is_enabled:
        return jsonify({'code': 400, 'message': 'Alert config is disabled'}), 400

    # Build alert template data that would come from a real alert trigger
    alert_template_data = {
        'title': data.get('title', 'StreamPark Alert Notification'),
        'alertType': alert_config.alert_type,
        'alertTime': datetime.utcnow().isoformat(),
        'jobName': data.get('jobName', 'test-job'),
        'status': data.get('status', 'FAILED'),
        'startTime': data.get('startTime', datetime.utcnow().isoformat()),
        'endTime': data.get('endTime', datetime.utcnow().isoformat()),
        'duration': data.get('duration', '0s'),
        'message': data.get('message', 'Test alert notification'),
        'user': User.query.get(alert_config.user_id).nick_name or 'unknown',
        'alertId': alert_config.id,
        'alertName': alert_config.alert_name
    }

    request_template = alert_config.http_callback_request_template
    if not request_template:
        return jsonify({'code': 400, 'message': 'No request template configured for this alert'}), 400

    rendered_body = render_alert_template(request_template, alert_template_data)

    if rendered_body is None:
        history = AlertHistory(
            alert_config_id=alert_config.id,
            title=alert_template_data['title'],
            content='Template rendering failed',
            alert_status=2
        )
        db.session.add(history)
        db.session.commit()
        return jsonify({'code': 500, 'message': 'Failed to render alert template'}), 500

    # Record the alert attempt (in production, this would send the HTTP callback)
    history = AlertHistory(
        alert_config_id=alert_config.id,
        title=alert_template_data['title'],
        content=rendered_body,
        alert_status=1
    )
    db.session.add(history)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': 'Alert sent successfully',
        'data': {
            'renderedBody': rendered_body,
            'callbackUrl': alert_config.http_callback_url,
            'method': alert_config.http_callback_method,
            'historyId': history.id
        }
    })


@app.route('/flink/alert/history')
@login_required
def alert_history():
    alert_id = request.args.get('alertId', type=int)
    if not alert_id:
        histories = AlertHistory.query.order_by(AlertHistory.create_time.desc()).limit(50).all()
    else:
        histories = AlertHistory.query.filter_by(alert_config_id=alert_id).order_by(
            AlertHistory.create_time.desc()).limit(50).all()

    result = []
    for h in histories:
        result.append({
            'id': h.id,
            'alertConfigId': h.alert_config_id,
            'title': h.title,
            'content': h.content,
            'alertStatus': h.alert_status,
            'createTime': h.create_time.isoformat() if h.create_time else None
        })
    return jsonify({'code': 200, 'data': result})


@app.route('/settings')
@login_required
def settings():
    user = User.query.get(session['user_id'])
    alerts = AlertConfig.query.filter_by(user_id=user.id).order_by(AlertConfig.create_time.desc()).all()
    return render_template('settings.html', user=user, alerts=alerts)


@app.route('/user/info')
@login_required
def user_info():
    user = User.query.get(session['user_id'])
    return jsonify({
        'code': 200,
        'data': {
            'userId': user.id,
            'username': user.username,
            'nickName': user.nick_name,
            'email': user.email,
            'userType': user.user_type,
            'status': user.status,
            'lastLoginTime': user.last_login_time.isoformat() if user.last_login_time else None
        }
    })