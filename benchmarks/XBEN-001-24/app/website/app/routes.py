from flask import render_template, redirect, url_for, request, session, jsonify

from app import app
from app.db import db
from app.models import User, Instance, ActivityLog


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))
    instances = Instance.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', user=user, instances=instances)


@app.route('/instances')
def instances_list():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    instances = Instance.query.filter_by(user_id=user_id).all()
    return render_template('instances.html', user=user, instances=instances)


@app.route('/instance/<int:instance_id>/manage')
def instance_manage(instance_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    # Only show management page for instances owned by the user
    instance = Instance.query.filter_by(id=instance_id, user_id=user_id).first()
    if not instance:
        return render_template('error.html', message='Instance not found'), 404
    logs = ActivityLog.query.filter_by(instance_id=instance_id).order_by(ActivityLog.id.desc()).limit(10).all()
    return render_template('manage.html', user=user, instance=instance, logs=logs)


@app.route('/instance/<int:instance_id>/details')
def instance_details(instance_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    # Only return details for instances owned by the user
    instance = Instance.query.filter_by(id=instance_id, user_id=user_id).first()
    if not instance:
        return jsonify({'success': False, 'msg': 'Instance not found'}), 404
    return jsonify({
        'success': True,
        'data': {
            'id': instance.id,
            'label': instance.label,
            'hostname': instance.hostname,
            'ip_address': instance.ip_address,
            'status': instance.status,
            'plan': instance.plan,
            'os_template': instance.os_template,
            'node': instance.node,
            'bandwidth_used': instance.bandwidth_used,
            'bandwidth_limit': instance.bandwidth_limit,
            'disk_used': instance.disk_used,
            'disk_limit': instance.disk_limit,
            'memory_mb': instance.memory_mb,
        }
    })


@app.route('/clientarea/settings', methods=['GET'])
def instance_settings():
    """Handle instance settings operations via query parameters."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'msg': 'Unauthorized'}), 401

    action = request.args.get('op')
    instance_id = request.args.get('instance_id', type=int)

    if not action or not instance_id:
        return jsonify({'success': False, 'msg': 'Missing parameters'}), 400

    # Retrieve the instance without verifying ownership
    instance = Instance.query.get(instance_id)
    if not instance:
        return jsonify({'success': False, 'msg': 'Instance not found'}), 404

    if action == 'UpdateHostname':
        new_hostname = request.args.get('newhostname', '').strip()
        if not new_hostname or len(new_hostname) < 3 or len(new_hostname) > 255:
            return jsonify({'success': False, 'msg': 'Invalid hostname'})
        if not all(c.isalnum() or c in '.-_' for c in new_hostname):
            return jsonify({'success': False, 'msg': 'Invalid hostname format'})
        instance.hostname = new_hostname
        log = ActivityLog(
            instance_id=instance.id,
            action='hostname_change',
            details='Hostname updated to {}'.format(new_hostname),
            timestamp=__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'success': True, 'msg': 'Hostname updated'})

    elif action == 'UpdateRootPassword':
        new_password = request.args.get('newpassword', '').strip()
        if not new_password or len(new_password) < 6:
            return jsonify({'success': False, 'msg': 'Password must be at least 6 characters'})
        instance.root_password = new_password
        log = ActivityLog(
            instance_id=instance.id,
            action='rootpassword_change',
            details='Root password updated',
            timestamp=__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'success': True, 'msg': 'Root password updated'})

    elif action == 'UpdateConsolePassword':
        new_vnc = request.args.get('newvncpass', '').strip()
        if not new_vnc or len(new_vnc) < 6 or len(new_vnc) > 8:
            return jsonify({'success': False, 'msg': 'Console password must be 6-8 characters'})
        instance.vnc_password = new_vnc
        log = ActivityLog(
            instance_id=instance.id,
            action='vncpassword_change',
            details='Console password updated',
            timestamp=__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'success': True, 'msg': 'Console password updated'})

    elif action == 'GetCredentials':
        return jsonify({
            'success': True,
            'data': {
                'root_password': instance.root_password,
                'vnc_password': instance.vnc_password,
                'hostname': instance.hostname,
                'ip_address': instance.ip_address,
            }
        })

    elif action == 'ServerStatus':
        return jsonify({
            'success': True,
            'data': {
                'status': instance.status,
                'hostname': instance.hostname,
                'node': instance.node,
                'bandwidth_used': instance.bandwidth_used,
                'bandwidth_limit': instance.bandwidth_limit,
            }
        })

    else:
        return jsonify({'success': False, 'msg': 'Unknown operation'}), 400


@app.route('/support')
def support():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    return render_template('support.html', user=user)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message='Internal server error'), 500
