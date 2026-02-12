import hashlib
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, render_template_string,
    redirect, url_for, request, session, Response, jsonify, flash
)

from app import app
from app.db import db
from app.models import User, ServiceInstance, NotificationChannel, NotificationLog


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return Response('Forbidden', status=403)
        return f(*args, **kwargs)
    return decorated


@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


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
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    services = ServiceInstance.query.all()
    up_count = sum(1 for s in services if s.status == 'UP')
    down_count = sum(1 for s in services if s.status == 'DOWN')
    return render_template('dashboard.html', user=user, services=services,
                           up_count=up_count, down_count=down_count)


@app.route('/applications')
@login_required
def applications():
    user = User.query.get(session['user_id'])
    services = ServiceInstance.query.order_by(ServiceInstance.group_name, ServiceInstance.name).all()
    groups = {}
    for svc in services:
        gname = svc.group_name or 'default'
        if gname not in groups:
            groups[gname] = []
        groups[gname].append(svc)
    return render_template('applications.html', user=user, groups=groups)


@app.route('/applications/<int:service_id>')
@login_required
def service_detail(service_id):
    user = User.query.get(session['user_id'])
    service = ServiceInstance.query.get_or_404(service_id)
    logs = NotificationLog.query.filter_by(service_id=service_id).order_by(
        NotificationLog.created_at.desc()).limit(20).all()
    return render_template('service_detail.html', user=user, service=service, logs=logs)


@app.route('/journal')
@login_required
def journal():
    user = User.query.get(session['user_id'])
    logs = NotificationLog.query.order_by(NotificationLog.created_at.desc()).limit(100).all()
    return render_template('journal.html', user=user, logs=logs)


@app.route('/notifications', methods=['GET'])
@admin_required
def notifications():
    user = User.query.get(session['user_id'])
    channels = NotificationChannel.query.all()
    return render_template('notifications.html', user=user, channels=channels)


@app.route('/notifications/<int:channel_id>', methods=['GET', 'POST'])
@admin_required
def notification_settings(channel_id):
    user = User.query.get(session['user_id'])
    channel = NotificationChannel.query.get_or_404(channel_id)

    if request.method == 'POST':
        channel.enabled = 'enabled' in request.form
        channel.smtp_host = request.form.get('smtp_host', channel.smtp_host)
        channel.smtp_port = int(request.form.get('smtp_port', channel.smtp_port or 587))
        channel.sender_address = request.form.get('sender_address', channel.sender_address)
        channel.recipients = request.form.get('recipients', channel.recipients)
        channel.subject_template = request.form.get('subject_template', channel.subject_template)
        channel.template = request.form.get('template', channel.template)
        channel.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Notification settings updated successfully.', 'success')
        return redirect(url_for('notification_settings', channel_id=channel_id))

    return render_template('notification_settings.html', user=user, channel=channel)


@app.route('/notifications/<int:channel_id>/test', methods=['POST'])
@admin_required
def test_notification(channel_id):
    """Send a test notification using the configured template."""
    channel = NotificationChannel.query.get_or_404(channel_id)

    if not channel.enabled:
        return jsonify({'status': 'error', 'message': 'Channel is disabled'}), 400

    # Pick a service instance for the test notification
    service = ServiceInstance.query.first()
    if not service:
        return jsonify({'status': 'error', 'message': 'No service instances registered'}), 400

    # Build event context similar to Spring Boot Admin MailNotifier
    event_context = {
        'from_status': 'UP',
        'to_status': 'DOWN',
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
    }

    instance_context = {
        'name': service.name,
        'url': service.url,
        'group': service.group_name or 'default',
        'status': service.status,
    }

    class AttrDict(dict):
        def __getattr__(self, key):
            try:
                return self[key]
            except KeyError:
                raise AttributeError(key)

    ctx = {
        'instance': AttrDict(instance_context),
        'event': AttrDict(event_context),
    }

    try:
        # Process the template - this mirrors Thymeleaf's templateEngine.process()
        rendered_body = render_template_string(channel.template, **ctx)
        rendered_subject = render_template_string(channel.subject_template, **ctx) if channel.subject_template else ''
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Template rendering failed'}), 500

    # Log the notification
    log_entry = NotificationLog(
        channel_id=channel.id,
        service_id=service.id,
        event_type='STATUS_CHANGE',
        rendered_body=rendered_body,
        rendered_subject=rendered_subject,
        status='sent',
    )
    db.session.add(log_entry)
    db.session.commit()

    return jsonify({
        'status': 'ok',
        'message': 'Test notification sent successfully',
        'preview': {
            'subject': rendered_subject,
            'body': rendered_body,
        }
    })


@app.route('/api/instances', methods=['GET'])
@login_required
def api_instances():
    services = ServiceInstance.query.all()
    result = []
    for s in services:
        result.append({
            'id': s.id,
            'name': s.name,
            'url': s.url,
            'status': s.status,
            'group': s.group_name,
            'lastChecked': s.last_checked.isoformat() if s.last_checked else None,
        })
    return jsonify(result)


@app.route('/api/instances/<int:instance_id>/status', methods=['POST'])
@admin_required
def update_instance_status(instance_id):
    service = ServiceInstance.query.get_or_404(instance_id)
    data = request.get_json(silent=True) or {}
    new_status = data.get('status', '').upper()
    if new_status not in ('UP', 'DOWN', 'OFFLINE', 'UNKNOWN'):
        return jsonify({'error': 'Invalid status value'}), 400

    old_status = service.status
    service.status = new_status
    service.last_checked = datetime.utcnow()
    db.session.commit()

    # Trigger notifications on status change
    if old_status != new_status:
        _trigger_notifications(service, old_status, new_status)

    return jsonify({'id': service.id, 'name': service.name, 'status': service.status})


def _trigger_notifications(service, from_status, to_status):
    """Process notification templates for all enabled channels."""
    channels = NotificationChannel.query.filter_by(enabled=True).all()

    class AttrDict(dict):
        def __getattr__(self, key):
            try:
                return self[key]
            except KeyError:
                raise AttributeError(key)

    event_context = AttrDict({
        'from_status': from_status,
        'to_status': to_status,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
    })

    instance_context = AttrDict({
        'name': service.name,
        'url': service.url,
        'group': service.group_name or 'default',
        'status': service.status,
    })

    for channel in channels:
        try:
            rendered_body = render_template_string(
                channel.template,
                instance=instance_context,
                event=event_context,
            )
            rendered_subject = ''
            if channel.subject_template:
                rendered_subject = render_template_string(
                    channel.subject_template,
                    instance=instance_context,
                    event=event_context,
                )
        except Exception:
            rendered_body = '[Template Error]'
            rendered_subject = '[Template Error]'

        log_entry = NotificationLog(
            channel_id=channel.id,
            service_id=service.id,
            event_type='STATUS_CHANGE',
            rendered_body=rendered_body,
            rendered_subject=rendered_subject,
            status='sent',
        )
        db.session.add(log_entry)

    db.session.commit()
