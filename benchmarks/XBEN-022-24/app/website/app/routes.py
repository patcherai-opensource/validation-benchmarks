from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
from functools import wraps
import hashlib
import json
import os
from datetime import datetime

from app import app
from app.db import db
from app.models import User, Team, FlinkApp, AlertConfig, Variable


@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/flink/') or request.path.startswith('/setting/'):
                return jsonify({'code': 401, 'message': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User.query.filter_by(username=username, password=password_hash).first()
        if user:
            if user.status == 0:
                return render_template('login.html', error='Account is locked. Contact administrator.')
            session['user_id'] = user.id
            user.last_login_time = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    apps = FlinkApp.query.all()
    teams = Team.query.all()
    running_count = FlinkApp.query.filter_by(state=5).count()
    failed_count = FlinkApp.query.filter_by(state=9).count()
    total_count = FlinkApp.query.count()
    return render_template('dashboard.html', user=user, apps=apps, teams=teams,
                           running_count=running_count, failed_count=failed_count,
                           total_count=total_count)


@app.route('/flink/app/list')
@login_required
def flink_app_list():
    user = get_current_user()
    apps = FlinkApp.query.all()
    return render_template('app_list.html', user=user, apps=apps)


@app.route('/flink/app/detail/<int:app_id>')
@login_required
def flink_app_detail(app_id):
    user = get_current_user()
    flink_app = FlinkApp.query.get_or_404(app_id)
    alert = None
    if flink_app.alert_id:
        alert = AlertConfig.query.get(flink_app.alert_id)
    return render_template('app_detail.html', user=user, app=flink_app, alert=alert)


@app.route('/setting/alert/list')
@login_required
def alert_list():
    user = get_current_user()
    alerts = AlertConfig.query.all()
    return render_template('alert_list.html', user=user, alerts=alerts)


@app.route('/flink/alert/add', methods=['POST'])
@login_required
def alert_add():
    user = get_current_user()
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': 'Invalid request body'}), 400

    alert_name = data.get('alertName')
    alert_type = data.get('alertType', 4)

    if not alert_name:
        return jsonify({'code': 400, 'message': 'Alert name is required'}), 400

    existing = AlertConfig.query.filter_by(alert_name=alert_name).first()
    if existing:
        return jsonify({'code': 400, 'message': 'Alert config with this name already exists'}), 400

    alert = AlertConfig(
        user_id=user.id,
        alert_name=alert_name,
        alert_type=alert_type
    )

    if alert_type == 1:
        email_params = data.get('emailParams')
        if email_params:
            alert.email_params = json.dumps(email_params) if isinstance(email_params, dict) else email_params
    elif alert_type == 2:
        dingtalk_params = data.get('dingtalkParams')
        if dingtalk_params:
            alert.dingtalk_params = json.dumps(dingtalk_params) if isinstance(dingtalk_params, dict) else dingtalk_params
    elif alert_type == 3:
        wechat_params = data.get('wechatParams')
        if wechat_params:
            alert.wechat_params = json.dumps(wechat_params) if isinstance(wechat_params, dict) else wechat_params
    elif alert_type == 4:
        http_callback_params = data.get('httpCallbackParams')
        if http_callback_params:
            alert.http_callback_params = json.dumps(http_callback_params) if isinstance(http_callback_params, dict) else http_callback_params

    db.session.add(alert)
    db.session.commit()

    return jsonify({'code': 200, 'message': 'Alert config created successfully', 'data': {'id': alert.id}})


@app.route('/flink/alert/update', methods=['POST', 'PUT'])
@login_required
def alert_update():
    user = get_current_user()
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': 'Invalid request body'}), 400

    alert_id = data.get('id')
    if not alert_id:
        return jsonify({'code': 400, 'message': 'Alert id is required'}), 400

    alert = AlertConfig.query.get(alert_id)
    if not alert:
        return jsonify({'code': 404, 'message': 'Alert config not found'}), 404

    if 'alertName' in data:
        alert.alert_name = data['alertName']
    if 'alertType' in data:
        alert.alert_type = data['alertType']

    alert_type = alert.alert_type

    if alert_type == 1 and 'emailParams' in data:
        email_params = data['emailParams']
        alert.email_params = json.dumps(email_params) if isinstance(email_params, dict) else email_params
    elif alert_type == 2 and 'dingtalkParams' in data:
        dingtalk_params = data['dingtalkParams']
        alert.dingtalk_params = json.dumps(dingtalk_params) if isinstance(dingtalk_params, dict) else dingtalk_params
    elif alert_type == 3 and 'wechatParams' in data:
        wechat_params = data['wechatParams']
        alert.wechat_params = json.dumps(wechat_params) if isinstance(wechat_params, dict) else wechat_params
    elif alert_type == 4 and 'httpCallbackParams' in data:
        http_callback_params = data['httpCallbackParams']
        alert.http_callback_params = json.dumps(http_callback_params) if isinstance(http_callback_params, dict) else http_callback_params

    alert.modify_time = datetime.utcnow()
    db.session.commit()

    return jsonify({'code': 200, 'message': 'Alert config updated successfully'})


@app.route('/flink/alert/delete', methods=['POST', 'DELETE'])
@login_required
def alert_delete():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'code': 400, 'message': 'Alert id is required'}), 400

    alert = AlertConfig.query.get(data['id'])
    if not alert:
        return jsonify({'code': 404, 'message': 'Alert config not found'}), 404

    linked_apps = FlinkApp.query.filter_by(alert_id=alert.id).count()
    if linked_apps > 0:
        return jsonify({'code': 400, 'message': 'Cannot delete alert config that is linked to applications'}), 400

    db.session.delete(alert)
    db.session.commit()
    return jsonify({'code': 200, 'message': 'Alert config deleted successfully'})


@app.route('/flink/alert/get', methods=['GET'])
@login_required
def alert_get():
    alert_id = request.args.get('id', type=int)
    if not alert_id:
        return jsonify({'code': 400, 'message': 'Alert id is required'}), 400

    alert = AlertConfig.query.get(alert_id)
    if not alert:
        return jsonify({'code': 404, 'message': 'Alert config not found'}), 404

    result = {
        'id': alert.id,
        'alertName': alert.alert_name,
        'alertType': alert.alert_type,
        'userId': alert.user_id,
        'createTime': alert.create_time.isoformat() if alert.create_time else None,
        'modifyTime': alert.modify_time.isoformat() if alert.modify_time else None,
    }

    if alert.alert_type == 4 and alert.http_callback_params:
        result['httpCallbackParams'] = json.loads(alert.http_callback_params)
    elif alert.alert_type == 1 and alert.email_params:
        result['emailParams'] = json.loads(alert.email_params)

    return jsonify({'code': 200, 'data': result})


@app.route('/flink/alert/send', methods=['POST'])
@login_required
def alert_send():
    """Test an alert configuration by sending a test notification"""
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'code': 400, 'message': 'Alert id is required'}), 400

    alert = AlertConfig.query.get(data['id'])
    if not alert:
        return jsonify({'code': 404, 'message': 'Alert config not found'}), 404

    if alert.alert_type == 4:
        # HTTP Callback alert type - process the request template
        if not alert.http_callback_params:
            return jsonify({'code': 400, 'message': 'HTTP callback parameters not configured'}), 400

        try:
            callback_params = json.loads(alert.http_callback_params)
        except (json.JSONDecodeError, TypeError):
            return jsonify({'code': 400, 'message': 'Invalid HTTP callback parameters'}), 400

        request_template = callback_params.get('requestTemplate', '')

        # Build the alert context with sample data for testing
        alert_context = {
            'title': 'StreamPark Alert Test',
            'subject': 'Test Notification',
            'status': 'TESTING',
            'jobName': 'test-job',
            'startTime': datetime.utcnow().isoformat(),
            'duration': '0s',
            'alertTime': datetime.utcnow().isoformat(),
            'link': request.host_url + 'dashboard',
            'type': 'test'
        }

        # Render the request template with alert context
        try:
            rendered = render_template_string(request_template, **alert_context)
        except Exception as e:
            return jsonify({'code': 500, 'message': 'Template rendering failed: ' + str(e)}), 500

        # In a full deployment this would POST to the callback URL
        # For now, return the rendered template as a preview
        return jsonify({
            'code': 200,
            'message': 'Alert test completed successfully',
            'data': {
                'rendered': rendered,
                'callbackUrl': callback_params.get('url', ''),
                'method': callback_params.get('method', 'POST')
            }
        })

    elif alert.alert_type == 1:
        return jsonify({'code': 200, 'message': 'Email alert test sent successfully'})
    elif alert.alert_type == 2:
        return jsonify({'code': 200, 'message': 'DingTalk alert test sent successfully'})
    elif alert.alert_type == 3:
        return jsonify({'code': 200, 'message': 'WeChat alert test sent successfully'})
    else:
        return jsonify({'code': 400, 'message': 'Unsupported alert type'}), 400


@app.route('/flink/app/update', methods=['POST', 'PUT'])
@login_required
def flink_app_update():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'code': 400, 'message': 'Application id is required'}), 400

    flink_app = FlinkApp.query.get(data['id'])
    if not flink_app:
        return jsonify({'code': 404, 'message': 'Application not found'}), 404

    if 'alertId' in data:
        if data['alertId']:
            alert = AlertConfig.query.get(data['alertId'])
            if not alert:
                return jsonify({'code': 400, 'message': 'Alert config not found'}), 400
        flink_app.alert_id = data['alertId']

    if 'description' in data:
        flink_app.description = data['description']

    flink_app.modify_time = datetime.utcnow()
    db.session.commit()

    return jsonify({'code': 200, 'message': 'Application updated successfully'})


@app.route('/setting/variable/list')
@login_required
def variable_list():
    user = get_current_user()
    variables = Variable.query.all()
    return render_template('variable_list.html', user=user, variables=variables)


@app.route('/setting/variable/add', methods=['POST'])
@login_required
def variable_add():
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': 'Invalid request body'}), 400

    variable_code = data.get('variableCode')
    variable_value = data.get('variableValue')

    if not variable_code or not variable_value:
        return jsonify({'code': 400, 'message': 'Variable code and value are required'}), 400

    existing = Variable.query.filter_by(variable_code=variable_code).first()
    if existing:
        return jsonify({'code': 400, 'message': 'Variable with this code already exists'}), 400

    user = get_current_user()
    variable = Variable(
        variable_code=variable_code,
        variable_value=variable_value,
        description=data.get('description', ''),
        creator_id=user.id,
        desensitization=data.get('desensitization', False)
    )
    db.session.add(variable)
    db.session.commit()

    return jsonify({'code': 200, 'message': 'Variable created successfully', 'data': {'id': variable.id}})


@app.route('/setting/team/list')
@login_required
def team_list():
    user = get_current_user()
    teams = Team.query.all()
    team_data = []
    for team in teams:
        app_count = FlinkApp.query.filter_by(team_id=team.id).count()
        team_data.append({'team': team, 'app_count': app_count})
    return render_template('team_list.html', user=user, team_data=team_data)


@app.route('/user/list')
@login_required
def user_list():
    user = get_current_user()
    if user.user_type != 1:
        return jsonify({'code': 403, 'message': 'Insufficient permissions'}), 403
    users = User.query.all()
    return render_template('user_list.html', user=user, users=users)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
