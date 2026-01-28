from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
import subprocess
import os
import json

from app import app
from app.db import db
from app.models import User, Appointment, Service, Provider


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request

@app.route('/')
def index():
    return render_template('booking.html', services=Service.query.all(), providers=Provider.query.all())

@app.route('/api/services')
def api_services():
    """API endpoint to list available services"""
    services = Service.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'duration': s.duration, 'price': s.price, 'description': s.description} for s in services])

@app.route('/api/providers')
def api_providers():
    """API endpoint to list available providers"""
    providers = Provider.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'email': p.email, 'specialty': p.specialty} for p in providers])

@app.route('/api/appointments', methods=['GET'])
def api_appointments():
    """API endpoint to list appointments (admin only)"""
    # Check if admin session
    if not session.get('admin_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    appointments = Appointment.query.all()
    return jsonify([{
        'id': a.id, 
        'customer_name': a.customer_name,
        'customer_email': a.customer_email,
        'service_id': a.service_id,
        'provider_id': a.provider_id,
        'notes': a.notes,
        'date': a.date,
        'status': a.status
    } for a in appointments])

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    """Public booking form - allows customers to schedule appointments"""
    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '')
        customer_email = request.form.get('customer_email', '')
        customer_phone = request.form.get('customer_phone', '')
        service_id = request.form.get('service_id', type=int)
        provider_id = request.form.get('provider_id', type=int)
        date = request.form.get('date', '')
        notes = request.form.get('notes', '')
        
        if not all([customer_name, customer_email, service_id, provider_id, date]):
            return render_template('booking.html', 
                services=Service.query.all(), 
                providers=Provider.query.all(),
                error='Please fill in all required fields')
        
        # Create new appointment
        appointment = Appointment(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            service_id=service_id,
            provider_id=provider_id,
            date=date,
            notes=notes,
            status='pending'
        )
        db.session.add(appointment)
        db.session.commit()
        
        return render_template('booking_success.html', appointment=appointment)
    
    return render_template('booking.html', services=Service.query.all(), providers=Provider.query.all())

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password, is_admin=True).first()
        if user:
            session['admin_id'] = user.id
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard - shows pending appointments"""
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))
    
    appointments = Appointment.query.order_by(Appointment.id.desc()).all()
    return render_template('admin_dashboard.html', appointments=appointments)

@app.route('/admin/appointment/<int:appointment_id>')
def admin_appointment_detail(appointment_id):
    """View appointment details"""
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    service = Service.query.get(appointment.service_id)
    provider = Provider.query.get(appointment.provider_id)
    return render_template('admin_appointment.html', appointment=appointment, service=service, provider=provider)

@app.route('/admin/appointment/<int:appointment_id>/confirm', methods=['POST'])
def confirm_appointment(appointment_id):
    """Confirm an appointment and send notification"""
    if not session.get('admin_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'confirmed'
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Appointment confirmed'})

@app.route('/admin/reports')
def admin_reports():
    """Admin reports page"""
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))
    return render_template('admin_reports.html')

@app.route('/admin/settings')
def admin_settings():
    """Admin settings page"""
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))
    return render_template('admin_settings.html')

@app.route('/api/export/appointments')
def export_appointments():
    """Export appointments to CSV format"""
    if not session.get('admin_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    format_type = request.args.get('format', 'csv')
    appointments = Appointment.query.all()
    
    if format_type == 'csv':
        csv_data = "id,customer_name,customer_email,date,status,notes\n"
        for a in appointments:
            csv_data += f"{a.id},{a.customer_name},{a.customer_email},{a.date},{a.status},{a.notes}\n"
        return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=appointments.csv'})
    
    return jsonify({'error': 'Unsupported format'}), 400

@app.route('/api/backup/generate')
def generate_backup():
    """Generate system backup - admin utility endpoint"""
    if not session.get('admin_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    backup_name = request.args.get('name', 'backup')
    # Simple backup generation
    return jsonify({'status': 'success', 'backup_name': f'{backup_name}.tar.gz'})

@app.route('/api/notification/preview')
def notification_preview():
    """
    Preview notification message before sending.
    Uses system echo command to format the notification text.
    """
    # Get notification parameters
    recipient = request.args.get('recipient', '')
    subject = request.args.get('subject', 'Appointment Notification')
    template = request.args.get('template', 'default')
    
    if not recipient:
        return jsonify({'error': 'Recipient email is required'}), 400
    
    # Build notification preview using echo command
    # VULNERABLE: subject is not sanitized before being passed to shell
    try:
        cmd = f'echo "Subject: {subject}\nTo: {recipient}\n\nThis is a preview of your notification message."'
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
        preview_text = result.decode('utf-8')
        return jsonify({
            'status': 'success',
            'preview': preview_text,
            'template': template
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Preview generation timed out'}), 500
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Preview failed: {e.output.decode("utf-8")}'}), 500

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/services')
def services_page():
    """Services listing page"""
    services = Service.query.all()
    return render_template('services.html', services=services)

@app.route('/providers')
def providers_page():
    """Providers listing page"""
    providers = Provider.query.all()
    return render_template('providers.html', providers=providers)

# Legacy endpoints (kept for compatibility)
@app.route('/login', methods=['GET', 'POST'])
def login():
    return redirect(url_for('admin_login'))

@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('index'))

@app.route('/robots.txt')
def robots():
    """Serve robots.txt"""
    return app.send_static_file('robots.txt')
