from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, flash
from datetime import datetime

from app import app
from app.db import db
from app.models import Staff, Service, Provider, Appointment


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500


@app.route('/')
def index():
    return redirect(url_for('booking'))


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    services = Service.query.all()
    providers = Provider.query.all()
    
    if request.method == 'POST':
        try:
            customer_name = request.form.get('customer_name', '').strip()
            customer_email = request.form.get('customer_email', '').strip()
            customer_phone = request.form.get('customer_phone', '').strip()
            service_id = request.form.get('service_id', type=int)
            provider_id = request.form.get('provider_id', type=int)
            appointment_date_str = request.form.get('appointment_date', '')
            notes = request.form.get('notes', '').strip()
            
            if not customer_name or not customer_email or not service_id or not provider_id or not appointment_date_str:
                return render_template('booking.html', services=services, providers=providers,
                                     error='Please fill in all required fields')
            
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M')
            
            appointment = Appointment(
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                service_id=service_id,
                provider_id=provider_id,
                appointment_date=appointment_date,
                notes=notes,
                status='pending'
            )
            db.session.add(appointment)
            db.session.commit()
            
            service = Service.query.get(service_id)
            provider = Provider.query.get(provider_id)
            
            confirmation_template = f'''
            <div class="confirmation-details">
                <p><strong>Name:</strong> {customer_name}</p>
                <p><strong>Email:</strong> {{{{ email }}}}</p>
                <p><strong>Phone:</strong> {{{{ phone }}}}</p>
                <p><strong>Service:</strong> {{{{ service_name }}}}</p>
                <p><strong>Provider:</strong> {{{{ provider_name }}}}</p>
                <p><strong>Date:</strong> {{{{ appointment_date }}}}</p>
                <p><strong>Notes:</strong> {notes}</p>
            </div>
            '''
            
            rendered_confirmation = render_template_string(
                confirmation_template,
                email=customer_email,
                phone=customer_phone or 'Not provided',
                service_name=service.name if service else 'Unknown',
                provider_name=provider.name if provider else 'Unknown',
                appointment_date=appointment_date.strftime('%B %d, %Y at %H:%M')
            )
            
            return render_template('booking_success.html', 
                                 appointment=appointment,
                                 rendered_confirmation=rendered_confirmation)
            
        except Exception as e:
            db.session.rollback()
            return render_template('booking.html', services=services, providers=providers,
                                 error='An error occurred while processing your booking')
    
    return render_template('booking.html', services=services, providers=providers)


@app.route('/backend/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        staff = Staff.query.filter_by(username=username, password=password).first()
        if staff:
            session['staff_id'] = staff.id
            session['staff_name'] = staff.name
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')


@app.route('/backend/logout')
def admin_logout():
    session.pop('staff_id', None)
    session.pop('staff_name', None)
    return redirect(url_for('admin_login'))


@app.route('/backend')
def admin_dashboard():
    staff_id = session.get('staff_id')
    if not staff_id:
        return redirect(url_for('admin_login'))
    
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return render_template('admin_dashboard.html', appointments=appointments)


@app.route('/backend/appointments')
def admin_appointments():
    staff_id = session.get('staff_id')
    if not staff_id:
        return redirect(url_for('admin_login'))
    
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return render_template('admin_appointments.html', appointments=appointments)


@app.route('/backend/appointment/<int:appointment_id>')
def view_appointment(appointment_id):
    staff_id = session.get('staff_id')
    if not staff_id:
        return redirect(url_for('admin_login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    service = Service.query.get(appointment.service_id)
    provider = Provider.query.get(appointment.provider_id)
    
    detail_template = f'''
    <div class="appointment-detail">
        <h4>Appointment #{appointment.id}</h4>
        <table class="table">
            <tr><td><strong>Customer Name:</strong></td><td>{appointment.customer_name}</td></tr>
            <tr><td><strong>Email:</strong></td><td>{appointment.customer_email}</td></tr>
            <tr><td><strong>Phone:</strong></td><td>{appointment.customer_phone or 'N/A'}</td></tr>
            <tr><td><strong>Service:</strong></td><td>{{{{ service_name }}}}</td></tr>
            <tr><td><strong>Provider:</strong></td><td>{{{{ provider_name }}}}</td></tr>
            <tr><td><strong>Date/Time:</strong></td><td>{{{{ appointment_date }}}}</td></tr>
            <tr><td><strong>Status:</strong></td><td>{{{{ status }}}}</td></tr>
            <tr><td><strong>Notes:</strong></td><td>{appointment.notes or 'None'}</td></tr>
        </table>
    </div>
    '''
    
    rendered_detail = render_template_string(
        detail_template,
        service_name=service.name if service else 'Unknown',
        provider_name=provider.name if provider else 'Unknown',
        appointment_date=appointment.appointment_date.strftime('%Y-%m-%d %H:%M'),
        status=appointment.status
    )
    
    return render_template('admin_appointment_detail.html', 
                         appointment=appointment,
                         rendered_detail=rendered_detail)


@app.route('/backend/appointment/<int:appointment_id>/update', methods=['POST'])
def update_appointment_status(appointment_id):
    staff_id = session.get('staff_id')
    if not staff_id:
        return redirect(url_for('admin_login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'confirmed', 'cancelled', 'completed']:
        appointment.status = new_status
        db.session.commit()
    
    return redirect(url_for('view_appointment', appointment_id=appointment_id))


@app.route('/api/services')
def api_services():
    services = Service.query.all()
    return Response(
        '[' + ','.join([f'{{"id":{s.id},"name":"{s.name}","duration":{s.duration},"price":{s.price}}}' for s in services]) + ']',
        mimetype='application/json'
    )


@app.route('/api/providers')
def api_providers():
    providers = Provider.query.all()
    return Response(
        '[' + ','.join([f'{{"id":{p.id},"name":"{p.name}","specialty":"{p.specialty or ""}"}}' for p in providers]) + ']',
        mimetype='application/json'
    )
