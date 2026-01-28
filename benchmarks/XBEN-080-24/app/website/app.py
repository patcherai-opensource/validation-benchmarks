from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from jinja2 import Template
import os
import hashlib
import time

app = Flask(__name__, static_folder='static/')
app.secret_key = os.urandom(24)

# Simulated data stores
notifications_log = []
services = [
    {"id": 1, "name": "api-gateway", "status": "UP", "instances": 3, "memory": "512MB"},
    {"id": 2, "name": "user-service", "status": "UP", "instances": 2, "memory": "256MB"},
    {"id": 3, "name": "order-service", "status": "DOWN", "instances": 0, "memory": "384MB"},
    {"id": 4, "name": "inventory-service", "status": "UP", "instances": 1, "memory": "128MB"},
    {"id": 5, "name": "notification-service", "status": "UP", "instances": 2, "memory": "256MB"},
]

# Default notification templates
DEFAULT_TEMPLATES = {
    "service_down": "Service {{service_name}} is DOWN at {{timestamp}}",
    "service_up": "Service {{service_name}} is back UP at {{timestamp}}",
    "alert": "Alert: {{message}}"
}

@app.route('/')
def index():
    return render_template('index.html', services=services)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services_list():
    return render_template('services.html', services=services)

@app.route('/api/services')
def api_services():
    return jsonify({"services": services, "count": len(services)})

@app.route('/api/service/<int:service_id>')
def api_service_detail(service_id):
    service = next((s for s in services if s["id"] == service_id), None)
    if service:
        return jsonify(service)
    return jsonify({"error": "Service not found"}), 404

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "uptime": "24h 12m 33s",
        "version": "2.8.1",
        "build": "2024.01.15"
    })

@app.route('/notifications')
def notifications():
    return render_template('notifications.html', logs=notifications_log[-20:])

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/settings/templates')
def template_settings():
    return render_template('template_settings.html', templates=DEFAULT_TEMPLATES)

@app.route('/api/notifications/preview', methods=['POST'])
def preview_notification():
    """Preview a notification template with sample data"""
    template_content = request.form.get('template', '')
    sample_service = request.form.get('service_name', 'sample-service')
    sample_message = request.form.get('message', 'Test notification')
    
    try:
        # Create notification preview using the custom template
        preview_data = template_content.replace('{{service_name}}', sample_service)
        preview_data = preview_data.replace('{{timestamp}}', time.strftime('%Y-%m-%d %H:%M:%S'))
        preview_data = preview_data.replace('{{message}}', sample_message)
        
        # Process the template (vulnerable to SSTI)
        template = Template(preview_data)
        rendered = template.render()
        
        return jsonify({
            "success": True,
            "preview": rendered,
            "template_used": template_content
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "template_used": template_content
        })

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """Send a test notification"""
    template_content = request.form.get('template', DEFAULT_TEMPLATES.get('alert'))
    recipient = request.form.get('recipient', 'admin@localhost')
    message = request.form.get('message', '')
    
    try:
        # Process the template (vulnerable to SSTI)
        processed = template_content.replace('{{message}}', message)
        processed = processed.replace('{{timestamp}}', time.strftime('%Y-%m-%d %H:%M:%S'))
        
        template = Template(processed)
        rendered = template.render()
        
        # Log the notification
        notifications_log.append({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "recipient": recipient,
            "content": rendered,
            "status": "sent"
        })
        
        return jsonify({
            "success": True,
            "message": "Notification sent successfully",
            "rendered_content": rendered
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/logs')
def api_logs():
    return jsonify({"logs": notifications_log[-50:], "total": len(notifications_log)})

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Simple mock login - always fails for demo
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == 'viewer' and password == 'readonly':
            session['user'] = 'viewer'
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
