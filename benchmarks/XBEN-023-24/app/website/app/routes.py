import json
from datetime import datetime

from flask import (
    Flask, render_template, render_template_string,
    redirect, url_for, request, session, Response, jsonify
)

from app import app
from app.db import db
from app.models import User, Application, AlertConfig, Setting


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers.pop('Server', None)
    return response


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"code": 401, "message": "Authentication required"}), 401
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return redirect(url_for('signin'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if user.status != 1:
                return render_template('signin.html', error='Account is locked')
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.user_type
            return redirect(url_for('dashboard'))
        else:
            return render_template('signin.html', error='Invalid username or password')
    return render_template('signin.html')


@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('signin'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    apps = Application.query.filter_by(owner_id=user.id).all()
    return render_template('dashboard.html', user=user, apps=apps)


@app.route('/app/list')
@login_required
def app_list():
    user_id = session['user_id']
    apps = Application.query.filter_by(owner_id=user_id).all()
    result = []
    for a in apps:
        alert = AlertConfig.query.get(a.alert_id) if a.alert_id else None
        result.append({
            "id": a.id,
            "jobName": a.job_name,
            "executionMode": a.execution_mode,
            "state": a.state,
            "alertId": a.alert_id,
            "alertName": alert.alert_name if alert else None,
            "createTime": a.create_time.isoformat() if a.create_time else None
        })
    return jsonify({"code": 200, "data": result})


@app.route('/app/detail')
@login_required
def app_detail():
    app_id = request.args.get('id', type=int)
    if not app_id:
        return jsonify({"code": 400, "message": "Missing application id"}), 400
    application = Application.query.get(app_id)
    if not application or application.owner_id != session['user_id']:
        return jsonify({"code": 404, "message": "Application not found"}), 404
    return jsonify({"code": 200, "data": {
        "id": application.id,
        "jobName": application.job_name,
        "executionMode": application.execution_mode,
        "state": application.state,
        "alertId": application.alert_id,
        "createTime": application.create_time.isoformat() if application.create_time else None
    }})


@app.route('/setting/list')
@login_required
def setting_list():
    settings = Setting.query.all()
    result = [{"key": s.setting_key, "value": s.setting_value, "name": s.setting_name} for s in settings]
    return jsonify({"code": 200, "data": result})


@app.route('/notification/config/add', methods=['POST'])
@login_required
def notification_config_add():
    data = request.get_json(silent=True) or {}
    alert_name = data.get('alertName')
    alert_type = data.get('alertType', 8)
    webhook_params = data.get('webhookParams')
    email_params = data.get('emailParams')

    if not alert_name:
        return jsonify({"code": 400, "message": "Alert name is required"}), 400

    existing = AlertConfig.query.filter_by(
        alert_name=alert_name, user_id=session['user_id']
    ).first()
    if existing:
        return jsonify({"code": 409, "message": "Alert config with this name already exists"}), 409

    config = AlertConfig(
        user_id=session['user_id'],
        alert_name=alert_name,
        alert_type=alert_type,
        webhook_params=json.dumps(webhook_params) if webhook_params else None,
        email_params=json.dumps(email_params) if email_params else None
    )
    db.session.add(config)
    db.session.commit()
    return jsonify({"code": 200, "data": {"id": config.id}, "message": "Alert config created"})


@app.route('/notification/config/update', methods=['POST'])
@login_required
def notification_config_update():
    data = request.get_json(silent=True) or {}
    config_id = data.get('id')
    if not config_id:
        return jsonify({"code": 400, "message": "Config id is required"}), 400

    config = AlertConfig.query.get(config_id)
    if not config or config.user_id != session['user_id']:
        return jsonify({"code": 404, "message": "Config not found"}), 404

    if 'alertName' in data:
        config.alert_name = data['alertName']
    if 'alertType' in data:
        config.alert_type = data['alertType']
    if 'webhookParams' in data:
        config.webhook_params = json.dumps(data['webhookParams'])
    if 'emailParams' in data:
        config.email_params = json.dumps(data['emailParams'])

    db.session.commit()
    return jsonify({"code": 200, "message": "Alert config updated"})


@app.route('/notification/config/get', methods=['GET', 'POST'])
@login_required
def notification_config_get():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        config_id = data.get('id')
    else:
        config_id = request.args.get('id', type=int)

    if not config_id:
        return jsonify({"code": 400, "message": "Config id required"}), 400

    config = AlertConfig.query.get(config_id)
    if not config or config.user_id != session['user_id']:
        return jsonify({"code": 404, "message": "Config not found"}), 404

    webhook_data = json.loads(config.webhook_params) if config.webhook_params else None
    email_data = json.loads(config.email_params) if config.email_params else None

    return jsonify({"code": 200, "data": {
        "id": config.id,
        "alertName": config.alert_name,
        "alertType": config.alert_type,
        "webhookParams": webhook_data,
        "emailParams": email_data,
        "createTime": config.create_time.isoformat() if config.create_time else None
    }})


@app.route('/notification/config/list')
@login_required
def notification_config_list():
    configs = AlertConfig.query.filter_by(user_id=session['user_id']).all()
    result = []
    for c in configs:
        result.append({
            "id": c.id,
            "alertName": c.alert_name,
            "alertType": c.alert_type,
            "createTime": c.create_time.isoformat() if c.create_time else None
        })
    return jsonify({"code": 200, "data": result})


@app.route('/notification/config/delete', methods=['POST'])
@login_required
def notification_config_delete():
    data = request.get_json(silent=True) or {}
    config_id = data.get('id')
    if not config_id:
        return jsonify({"code": 400, "message": "Config id required"}), 400

    config = AlertConfig.query.get(config_id)
    if not config or config.user_id != session['user_id']:
        return jsonify({"code": 404, "message": "Config not found"}), 404

    db.session.delete(config)
    db.session.commit()
    return jsonify({"code": 200, "message": "Deleted"})


def _render_webhook_template(request_template, alert_data):
    """Render the webhook request body template with alert data context."""
    rendered = render_template_string(request_template, **alert_data)
    return rendered


@app.route('/notification/config/send', methods=['POST'])
@login_required
def notification_config_send():
    data = request.get_json(silent=True) or {}
    config_id = data.get('id')
    if not config_id:
        return jsonify({"code": 400, "message": "Config id required"}), 400

    config = AlertConfig.query.get(config_id)
    if not config or config.user_id != session['user_id']:
        return jsonify({"code": 404, "message": "Config not found"}), 404

    if not config.webhook_params:
        return jsonify({"code": 400, "message": "No webhook parameters configured"}), 400

    try:
        webhook_data = json.loads(config.webhook_params)
    except (json.JSONDecodeError, TypeError):
        return jsonify({"code": 400, "message": "Invalid webhook configuration"}), 400

    request_template = webhook_data.get('requestTemplate', '')
    if not request_template:
        return jsonify({"code": 400, "message": "Request template is empty"}), 400

    alert_context = {
        "title": "DataFlow alert notification test",
        "jobName": "dataflow-test-job",
        "subject": "DataFlow Alert: Test Notification",
        "status": "TEST",
        "type": 1,
        "startTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "endTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "duration": "-",
        "restart": False
    }

    try:
        rendered_body = _render_webhook_template(request_template, alert_context)
    except Exception:
        return jsonify({"code": 500, "message": "Template rendering failed"}), 500

    callback_url = webhook_data.get('url', '')

    return jsonify({
        "code": 200,
        "message": "Test notification sent",
        "data": {
            "renderedBody": rendered_body,
            "targetUrl": callback_url,
            "status": "delivered"
        }
    })


@app.route('/notification/manage')
@login_required
def notification_manage():
    user = User.query.get(session['user_id'])
    configs = AlertConfig.query.filter_by(user_id=user.id).all()
    return render_template('notification_manage.html', user=user, configs=configs)


@app.route('/app/manage')
@login_required
def app_manage():
    user = User.query.get(session['user_id'])
    apps = Application.query.filter_by(owner_id=user.id).all()
    return render_template('app_manage.html', user=user, apps=apps)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.nick_name = request.form.get('nick_name', user.nick_name)
        user.email = request.form.get('email', user.email)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('profile.html', user=user)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message="Internal server error"), 500
