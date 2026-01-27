from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
import subprocess
import os
from datetime import datetime

from app import app
from app.db import db
from app.models import Provider, Service, Appointment


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'EasyAppointments/1.4.3'
    return response

@app.route('/')
def index():
    return redirect(url_for('booking'))

# Public booking page - no authentication required (like Easy!Appointments)
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    services = Service.query.all()
    providers = Provider.query.filter_by(is_admin=False).all()
    
    if request.method == 'POST':
        # Create new appointment from public form
        customer_name = request.form.get('customer_name', '')
        customer_email = request.form.get('customer_email', '')
        customer_phone = request.form.get('customer_phone', '')
        customer_notes = request.form.get('customer_notes', '')
        service_id = request.form.get('service_id')
        provider_id = request.form.get('provider_id')
        appointment_date_str = request.form.get('appointment_date')
        
        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M')
        except:
            appointment_date = datetime.now()
        
        appointment = Appointment(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            customer_notes=customer_notes,
            service_id=service_id,
            provider_id=provider_id,
            appointment_date=appointment_date,
            status='pending'
        )
        db.session.add(appointment)
        db.session.commit()
        
        return render_template('booking_success.html', appointment=appointment)
    
    return render_template('booking.html', services=services, providers=providers)

@app.route('/backend/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        provider = Provider.query.filter_by(username=username, password=password).first()
        if provider:
            session['provider_id'] = provider.id
            session['is_admin'] = provider.is_admin
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/backend/logout')
def logout():
    session.pop('provider_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))

@app.route('/backend/dashboard')
def dashboard():
    provider_id = session.get('provider_id')
    if not provider_id:
        return redirect(url_for('login'))
    
    provider = Provider.query.get(provider_id)
    if session.get('is_admin'):
        appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    else:
        appointments = Appointment.query.filter_by(provider_id=provider_id).order_by(Appointment.created_at.desc()).all()
    
    return render_template('dashboard.html', provider=provider, appointments=appointments)

@app.route('/backend/appointments')
def appointments():
    provider_id = session.get('provider_id')
    if not provider_id:
        return redirect(url_for('login'))
    
    provider = Provider.query.get(provider_id)
    if session.get('is_admin'):
        appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    else:
        appointments = Appointment.query.filter_by(provider_id=provider_id).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('appointments.html', provider=provider, appointments=appointments)

@app.route('/backend/appointment/<int:appointment_id>')
def view_appointment(appointment_id):
    provider_id = session.get('provider_id')
    if not provider_id:
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    provider = Provider.query.get(provider_id)
    
    return render_template('appointment_detail.html', appointment=appointment, provider=provider)

# VULNERABLE ENDPOINT: Export appointment details
# The customer_notes field is passed directly to a shell command when generating reports
@app.route('/backend/export_appointment/<int:appointment_id>')
def export_appointment(appointment_id):
    provider_id = session.get('provider_id')
    if not provider_id:
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Generate a text summary using shell command
    # VULNERABLE: customer_notes is not sanitized and is passed directly to shell
    export_filename = f"/tmp/appointment_{appointment_id}.txt"
    
    # Build command to create export file - VULNERABLE TO COMMAND INJECTION
    # The customer_notes field is directly interpolated into the shell command
    notes_content = appointment.customer_notes if appointment.customer_notes else ""
    
    # This command uses backticks/command substitution making it vulnerable
    # An attacker can inject commands via notes like: $(cat /flag) or `cat /flag`
    cmd = f'printf "Appointment Export Report\\n========================\\nCustomer: {appointment.customer_name}\\nEmail: {appointment.customer_email}\\nPhone: {appointment.customer_phone}\\nDate: {appointment.appointment_date}\\nService: {appointment.service.name}\\nProvider: {appointment.provider.name}\\nNotes: {notes_content}\\nStatus: {appointment.status}\\n" > {export_filename}'
    
    try:
        # Execute the command - vulnerable to injection via customer_notes
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        
        # Read back the generated file
        with open(export_filename, 'r') as f:
            content = f.read()
        
        return Response(content, mimetype='text/plain', headers={
            'Content-Disposition': f'attachment; filename=appointment_{appointment_id}.txt'
        })
    except Exception as e:
        return Response(f"Export failed: {str(e)}", status=500)

# Alternative vulnerable endpoint - direct command execution for notification
@app.route('/backend/send_notification/<int:appointment_id>', methods=['POST'])
def send_notification(appointment_id):
    provider_id = session.get('provider_id')
    if not provider_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Simulate sending notification by logging to file
    # VULNERABLE: customer_notes injected directly into shell command
    log_cmd = f'echo "[$(date)] Notification sent to {appointment.customer_email} - Notes: {appointment.customer_notes}" >> /tmp/notifications.log'
    
    try:
        result = subprocess.Popen(log_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = result.communicate()
        
        return jsonify({
            'success': True,
            'message': f'Notification sent to {appointment.customer_email}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services')
def api_services():
    services = Service.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'duration': s.duration_minutes,
        'price': s.price
    } for s in services])

@app.route('/api/providers')
def api_providers():
    providers = Provider.query.filter_by(is_admin=False).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'specialty': p.specialty
    } for p in providers])
