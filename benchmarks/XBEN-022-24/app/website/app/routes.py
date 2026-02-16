from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, NotificationConfig

import os
import json
from datetime import datetime

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return render_template('templates/login.html', error='Invalid username or password')
    return render_template('templates/login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    user = get_current_user()
    if user:
        return render_template('templates/home.html', user=user)
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = get_current_user()
    if user:
        if request.method == 'POST':
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            user.loan_amount = float(request.form['loan_amount'])
            user.loan_term_months = int(request.form['loan_term_months'])
            user.monthly_payment = float(request.form['monthly_payment'])
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('templates/profile.html', user=user)
    return redirect(url_for('login'))


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    user = get_current_user()
    if user:
        if request.method == 'POST':
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            user.loan_amount = float(request.form['loan_amount'])
            user.loan_term_months = int(request.form['loan_term_months'])
            user.monthly_payment = float(request.form['monthly_payment'])

            if 'image_profile' in request.files:
                image_profile = request.files['image_profile']
                if image_profile.filename != '':
                    safe_dir = '/var/www/ssti_include_loan_calculator/app/static/images/'
                    final_path = os.path.realpath(os.path.join(safe_dir, image_profile.filename))
                    if os.path.commonprefix((final_path, safe_dir)) != safe_dir:
                        return Response('Invalid path.', status=400)
                    image_profile.save(final_path)
                    user.image_profile_filename = image_profile.filename

            db.session.commit()
        return render_template('templates/profile.html', user=user)
    return redirect(url_for('login'))


@app.route('/error')
def error():
    error_message = request.args.get('message', 'An error occurred.')
    error_type = request.args.get('error_type', None)
    if error_type:
        allowed_templates = ['not_implemented.html']
        if error_type not in allowed_templates:
            return Response('Invalid error type.', status=400)
        return render_template('templates/error.html', error_message=error_message, error_type='templates/' + error_type)
    return render_template('templates/error.html', error_message=error_message, error_type=None)


@app.route('/loan_details')
def loan_details():
    user = get_current_user()
    if user:
        return render_template('templates/loan_details.html', loan_amount=user.loan_amount,
            loan_term_months=user.loan_term_months, monthly_payment=user.monthly_payment)
    return redirect(url_for('login'))


@app.route('/total_loan_payments')
def total_loan_payments():
    user = get_current_user()
    if user:
        principal = request.args.get('principal', type=float)
        payment = request.args.get('payment', type=float)
        term = request.args.get('term', type=int)

        if principal is None or payment is None or term is None:
            return Response('Missing principal, payment or term parameters', status=400)

        result = {
            "loan_principal": principal,
            "monthly_payment": payment,
            "loan_term_amount": term,
            "total_loan_payments": round(payment * term, 2)
        }
        return jsonify(result)
    return redirect(url_for('login'))


@app.route('/notifications')
def notifications():
    user = get_current_user()
    if user:
        configs = NotificationConfig.query.filter_by(user_id=user.id).all()
        return render_template('templates/notifications.html', user=user, configs=configs)
    return redirect(url_for('login'))


@app.route('/api/notifications/list', methods=['POST'])
def api_notifications_list():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    configs = NotificationConfig.query.filter_by(user_id=user.id).all()
    result = []
    for c in configs:
        result.append({
            "id": c.id,
            "configName": c.config_name,
            "notificationType": c.notification_type,
            "webhookUrl": c.webhook_url,
            "requestTemplate": c.request_template,
            "enabled": c.enabled
        })
    return jsonify({"success": True, "data": result})


@app.route('/api/notifications/get', methods=['POST'])
def api_notifications_get():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    data = request.get_json(silent=True) or {}
    config_id = data.get('id')
    if not config_id:
        return jsonify({"success": False, "message": "Missing id parameter"}), 400

    config = NotificationConfig.query.filter_by(id=config_id, user_id=user.id).first()
    if not config:
        return jsonify({"success": False, "message": "Configuration not found"}), 404

    return jsonify({
        "success": True,
        "data": {
            "id": config.id,
            "configName": config.config_name,
            "notificationType": config.notification_type,
            "webhookUrl": config.webhook_url,
            "requestTemplate": config.request_template,
            "enabled": config.enabled
        }
    })


@app.route('/api/notifications/create', methods=['POST'])
def api_notifications_create():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    data = request.get_json(silent=True) or {}
    config_name = data.get('configName')
    notification_type = data.get('notificationType', 'webhook')
    webhook_url = data.get('webhookUrl', '')
    request_template = data.get('requestTemplate', '')
    enabled = data.get('enabled', True)

    if not config_name:
        return jsonify({"success": False, "message": "configName is required"}), 400

    if notification_type not in ('email', 'webhook', 'slack'):
        return jsonify({"success": False, "message": "Invalid notification type"}), 400

    config = NotificationConfig(
        user_id=user.id,
        config_name=config_name,
        notification_type=notification_type,
        webhook_url=webhook_url,
        request_template=request_template,
        enabled=enabled
    )
    db.session.add(config)
    db.session.commit()

    return jsonify({"success": True, "data": {"id": config.id}})


@app.route('/api/notifications/update', methods=['POST'])
def api_notifications_update():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    data = request.get_json(silent=True) or {}
    config_id = data.get('id')
    if not config_id:
        return jsonify({"success": False, "message": "Missing id parameter"}), 400

    config = NotificationConfig.query.filter_by(id=config_id, user_id=user.id).first()
    if not config:
        return jsonify({"success": False, "message": "Configuration not found"}), 404

    if 'configName' in data:
        config.config_name = data['configName']
    if 'notificationType' in data:
        config.notification_type = data['notificationType']
    if 'webhookUrl' in data:
        config.webhook_url = data['webhookUrl']
    if 'requestTemplate' in data:
        config.request_template = data['requestTemplate']
    if 'enabled' in data:
        config.enabled = data['enabled']

    db.session.commit()
    return jsonify({"success": True, "data": {"id": config.id}})


@app.route('/api/notifications/delete', methods=['POST'])
def api_notifications_delete():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    data = request.get_json(silent=True) or {}
    config_id = data.get('id')
    if not config_id:
        return jsonify({"success": False, "message": "Missing id parameter"}), 400

    config = NotificationConfig.query.filter_by(id=config_id, user_id=user.id).first()
    if not config:
        return jsonify({"success": False, "message": "Configuration not found"}), 404

    db.session.delete(config)
    db.session.commit()
    return jsonify({"success": True})


@app.route('/api/notifications/test', methods=['POST'])
def api_notifications_test():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    data = request.get_json(silent=True) or {}
    config_id = data.get('id')
    if not config_id:
        return jsonify({"success": False, "message": "Missing id parameter"}), 400

    config = NotificationConfig.query.filter_by(id=config_id, user_id=user.id).first()
    if not config:
        return jsonify({"success": False, "message": "Configuration not found"}), 404

    if not config.request_template:
        return jsonify({"success": False, "message": "No request template configured"}), 400

    template_context = {
        "event": "test_notification",
        "user": user.username,
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "config_name": config.config_name,
        "status": "OK"
    }

    try:
        rendered = render_template_string(config.request_template, **template_context)
    except Exception:
        return jsonify({"success": False, "message": "Template rendering failed"}), 400

    return jsonify({
        "success": True,
        "message": "Test notification processed",
        "preview": rendered
    })
