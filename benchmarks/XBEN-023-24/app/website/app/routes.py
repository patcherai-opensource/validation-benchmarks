import os
import json
import time
from datetime import datetime

from flask import (Flask, render_template, render_template_string,
                   redirect, url_for, request, session, Response, jsonify)

from app import app
from app.db import db
from app.models import User, ServiceInstance, AlertConfig, AlertLog


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers.pop('Server', None)
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/ping')
def health_ping():
    return 'OK', 200


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    instances = ServiceInstance.query.all()
    recent_alerts = AlertLog.query.order_by(AlertLog.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', user=user, instances=instances, alerts=recent_alerts)


@app.route('/api/instances', methods=['GET'])
@login_required
def api_instances():
    instances = ServiceInstance.query.all()
    result = []
    for inst in instances:
        result.append({
            'id': inst.id,
            'name': inst.name,
            'service_url': inst.service_url,
            'health_url': inst.health_url,
            'status': inst.status,
            'last_checked': inst.last_checked.isoformat() if inst.last_checked else None
        })
    return jsonify(result)


@app.route('/api/instances/<int:instance_id>', methods=['GET'])
@login_required
def api_instance_detail(instance_id):
    inst = ServiceInstance.query.get_or_404(instance_id)
    return jsonify({
        'id': inst.id,
        'name': inst.name,
        'service_url': inst.service_url,
        'health_url': inst.health_url,
        'management_url': inst.management_url,
        'status': inst.status,
        'metadata': json.loads(inst.metadata_json) if inst.metadata_json else {},
        'last_checked': inst.last_checked.isoformat() if inst.last_checked else None
    })


@app.route('/api/instances', methods=['POST'])
@login_required
def api_register_instance():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('serviceUrl'):
        return jsonify({'error': 'Missing required fields: name, serviceUrl'}), 400

    instance = ServiceInstance(
        name=data['name'],
        service_url=data['serviceUrl'],
        health_url=data.get('healthUrl', data['serviceUrl'] + '/actuator/health'),
        management_url=data.get('managementUrl', data['serviceUrl'] + '/actuator'),
        status='UNKNOWN',
        metadata_json=json.dumps(data.get('metadata', {})),
        last_checked=datetime.utcnow()
    )
    db.session.add(instance)
    db.session.commit()
    return jsonify({'id': instance.id, 'name': instance.name}), 201


@app.route('/api/instances/<int:instance_id>', methods=['DELETE'])
@login_required
def api_deregister_instance(instance_id):
    inst = ServiceInstance.query.get_or_404(instance_id)
    db.session.delete(inst)
    db.session.commit()
    return jsonify({'status': 'deregistered'}), 200


@app.route('/notifications')
@login_required
def notifications():
    user = User.query.get(session['user_id'])
    config = AlertConfig.query.first()
    logs = AlertLog.query.order_by(AlertLog.timestamp.desc()).limit(50).all()
    return render_template('notifications.html', user=user, config=config, logs=logs)


@app.route('/notifications/settings', methods=['GET', 'POST'])
@login_required
def notification_settings():
    user = User.query.get(session['user_id'])
    config = AlertConfig.query.first()

    if request.method == 'POST':
        recipients = request.form.get('recipients', '')
        sender = request.form.get('sender', '')
        subject_tpl = request.form.get('subject_template', '')
        body_tpl = request.form.get('body_template', '')
        enabled = request.form.get('enabled') == 'on'

        if config:
            config.recipients = recipients
            config.sender = sender
            config.subject_template = subject_tpl
            config.body_template = body_tpl
            config.enabled = enabled
        else:
            config = AlertConfig(
                recipients=recipients,
                sender=sender,
                subject_template=subject_tpl,
                body_template=body_tpl,
                enabled=enabled
            )
            db.session.add(config)

        db.session.commit()
        return redirect(url_for('notification_settings'))

    return render_template('notification_settings.html', user=user, config=config)


@app.route('/notifications/preview', methods=['POST'])
@login_required
def notification_preview():
    """Preview the rendered notification template with sample data."""
    config = AlertConfig.query.first()
    if not config:
        return jsonify({'error': 'No notification configuration found'}), 404

    sample_instance = ServiceInstance.query.first()
    if not sample_instance:
        sample_data = {
            'instance_name': 'sample-service',
            'instance_url': 'http://localhost:8081',
            'previous_status': 'UP',
            'current_status': 'DOWN',
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'health_url': 'http://localhost:8081/actuator/health'
        }
    else:
        sample_data = {
            'instance_name': sample_instance.name,
            'instance_url': sample_instance.service_url,
            'previous_status': 'UP',
            'current_status': 'DOWN',
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'health_url': sample_instance.health_url
        }

    try:
        rendered_subject = render_template_string(
            config.subject_template, **sample_data)
        rendered_body = render_template_string(
            config.body_template, **sample_data)
    except Exception as e:
        return jsonify({'error': 'Template rendering failed', 'detail': str(e)}), 400

    return jsonify({
        'subject': rendered_subject,
        'body': rendered_body,
        'recipients': config.recipients,
        'sender': config.sender
    })


@app.route('/api/instances/<int:instance_id>/status', methods=['POST'])
@login_required
def update_instance_status(instance_id):
    """Simulate a status change event for a monitored instance."""
    inst = ServiceInstance.query.get_or_404(instance_id)
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Missing status field'}), 400

    old_status = inst.status
    new_status = data['status']
    inst.status = new_status
    inst.last_checked = datetime.utcnow()
    db.session.commit()

    if old_status != new_status:
        _process_status_alert(inst, old_status, new_status)

    return jsonify({'id': inst.id, 'status': inst.status})


def _process_status_alert(instance, old_status, new_status):
    """Process and render alert notification when instance status changes."""
    config = AlertConfig.query.first()
    if not config or not config.enabled:
        return

    template_vars = {
        'instance_name': instance.name,
        'instance_url': instance.service_url,
        'previous_status': old_status,
        'current_status': new_status,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'health_url': instance.health_url
    }

    try:
        rendered_body = render_template_string(config.body_template, **template_vars)
        rendered_subject = render_template_string(config.subject_template, **template_vars)
    except Exception:
        rendered_body = f"Alert: {instance.name} changed from {old_status} to {new_status}"
        rendered_subject = f"Status Alert: {instance.name}"

    alert_log = AlertLog(
        instance_id=instance.id,
        instance_name=instance.name,
        previous_status=old_status,
        current_status=new_status,
        rendered_subject=rendered_subject,
        rendered_body=rendered_body,
        recipients=config.recipients,
        timestamp=datetime.utcnow()
    )
    db.session.add(alert_log)
    db.session.commit()


@app.route('/alerts')
@login_required
def alert_history():
    user = User.query.get(session['user_id'])
    logs = AlertLog.query.order_by(AlertLog.timestamp.desc()).limit(100).all()
    return render_template('alert_history.html', user=user, logs=logs)


@app.route('/api/alerts/<int:alert_id>', methods=['GET'])
@login_required
def api_alert_detail(alert_id):
    alert = AlertLog.query.get_or_404(alert_id)
    return jsonify({
        'id': alert.id,
        'instance_name': alert.instance_name,
        'previous_status': alert.previous_status,
        'current_status': alert.current_status,
        'rendered_subject': alert.rendered_subject,
        'rendered_body': alert.rendered_body,
        'recipients': alert.recipients,
        'timestamp': alert.timestamp.isoformat() if alert.timestamp else None
    })


@app.route('/wallboard')
@login_required
def wallboard():
    user = User.query.get(session['user_id'])
    instances = ServiceInstance.query.all()
    return render_template('wallboard.html', user=user, instances=instances)
