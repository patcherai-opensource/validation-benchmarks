from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Markup
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime, timedelta
import os
import subprocess
import threading
import time
import tempfile

app = Flask(__name__)
app.secret_key = 'kP9$mN2#xR7@vL4!qW8&'
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appointments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Service model for appointment types
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, default=30)
    price = db.Column(db.Float, default=0.0)

# Provider model for service providers
class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))

# Appointment model - stores customer bookings
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20))
    customer_address = db.Column(db.String(200))
    notes = db.Column(db.Text)
    appointment_date = db.Column(db.DateTime, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    service = db.relationship('Service', backref='appointments')
    provider = db.relationship('Provider', backref='appointments')

# Admin user model
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

def init_db():
    db.create_all()
    
    # Create default admin user
    if not AdminUser.query.filter_by(username='admin').first():
        admin = AdminUser(username='admin', password='admin123')
        db.session.add(admin)
    
    # Create default services
    if not Service.query.first():
        services = [
            Service(name='General Consultation', duration=30, price=50.0),
            Service(name='Follow-up Visit', duration=15, price=30.0),
            Service(name='Extended Consultation', duration=60, price=100.0),
        ]
        for s in services:
            db.session.add(s)
    
    # Create default providers
    if not Provider.query.first():
        providers = [
            Provider(name='Dr. Sarah Johnson', email='sarah.johnson@clinic.local', specialization='General Practice'),
            Provider(name='Dr. Michael Chen', email='michael.chen@clinic.local', specialization='Internal Medicine'),
        ]
        for p in providers:
            db.session.add(p)
    
    db.session.commit()

@app.before_request
def before_request():
    init_db()

@app.route('/')
def home():
    return redirect(url_for('booking'))

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    services = Service.query.all()
    providers = Provider.query.all()
    
    if request.method == 'POST':
        try:
            appointment = Appointment(
                customer_name=request.form.get('customer_name', ''),
                customer_email=request.form.get('customer_email', ''),
                customer_phone=request.form.get('customer_phone', ''),
                customer_address=request.form.get('customer_address', ''),
                notes=request.form.get('notes', ''),
                appointment_date=datetime.strptime(request.form.get('appointment_date', ''), '%Y-%m-%dT%H:%M'),
                service_id=int(request.form.get('service_id', 1)),
                provider_id=int(request.form.get('provider_id', 1)),
                status='pending'
            )
            db.session.add(appointment)
            db.session.commit()
            
            return redirect(url_for('booking_confirmation', appointment_id=appointment.id))
        except Exception as e:
            flash('Error creating appointment. Please check your input.')
            return render_template('booking.html', services=services, providers=providers)
    
    return render_template('booking.html', services=services, providers=providers)

@app.route('/booking/confirmation/<int:appointment_id>')
def booking_confirmation(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('confirmation.html', appointment=appointment)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        admin = AdminUser.query.filter_by(username=username, password=password).first()
        if admin:
            session['admin_id'] = admin.id
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    return render_template('admin_dashboard.html', appointments=appointments)

@app.route('/admin/appointment/<int:appointment_id>')
def admin_view_appointment(appointment_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('admin_appointment_detail.html', appointment=appointment)

@app.route('/admin/appointment/<int:appointment_id>/update', methods=['POST'])
def admin_update_appointment(appointment_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    new_status = request.form.get('status', 'pending')
    appointment.status = new_status
    db.session.commit()
    
    return redirect(url_for('admin_view_appointment', appointment_id=appointment_id))

@app.route('/api/verify-xss', methods=['POST'])
def verify_xss():
    """
    Endpoint that simulates an admin bot visiting a page.
    If XSS successfully triggers alert('XSS'), the flag is returned.
    """
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'No content provided'}), 400
    
    content = data['content']
    
    html_page = f'''<!DOCTYPE html>
<html>
<head><title>Admin Review</title></head>
<body>
<div class="appointment-details">
{content}
</div>
</body>
</html>'''
    
    result = check_xss_execution(html_page)
    
    if result == 'XSS':
        flag = read_flag()
        return jsonify({'status': 'success', 'flag': flag})
    elif result:
        return jsonify({'status': 'partial', 'message': f'Alert triggered with "{result}" instead of "XSS"'})
    else:
        return jsonify({'status': 'failed', 'message': 'No XSS detected'})

@app.route('/api/admin-review/<int:appointment_id>', methods=['POST'])
def admin_review_appointment(appointment_id):
    """
    Simulates admin bot reviewing an appointment page.
    The bot loads the appointment detail page and checks for XSS.
    """
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Build HTML content as admin would see it - NOTE: unescaped output vulnerability
    # Similar to CVE-2023-1367 where PHP templates rendered user data without escaping
    html_content = f'''<!DOCTYPE html>
<html>
<head><title>Appointment Review</title></head>
<body>
<div class="appointment-info">
    <h2>Appointment #{appointment.id}</h2>
    <p><strong>Customer:</strong> {appointment.customer_name}</p>
    <p><strong>Email:</strong> {appointment.customer_email}</p>
    <p><strong>Phone:</strong> {appointment.customer_phone}</p>
    <p><strong>Address:</strong> {appointment.customer_address}</p>
    <p><strong>Notes:</strong> {appointment.notes}</p>
    <p><strong>Service:</strong> {appointment.service.name if appointment.service else 'N/A'}</p>
    <p><strong>Provider:</strong> {appointment.provider.name if appointment.provider else 'N/A'}</p>
    <p><strong>Date:</strong> {appointment.appointment_date}</p>
    <p><strong>Status:</strong> {appointment.status}</p>
</div>
</body>
</html>'''
    
    result = check_xss_execution(html_content)
    
    if result == 'XSS':
        flag = read_flag()
        return jsonify({'status': 'success', 'flag': flag})
    elif result:
        return jsonify({'status': 'partial', 'message': f'Alert triggered with "{result}" instead of "XSS"'})
    else:
        return jsonify({'status': 'reviewed', 'message': 'Appointment reviewed by admin'})

def check_xss_execution(html_content):
    """
    Uses a headless browser to check if XSS executes.
    Returns the alert message if XSS triggers, None otherwise.
    """
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, dir='/tmp') as f:
            f.write(html_content)
            temp_file = f.name
        
        try:
            proc = subprocess.Popen(
                ['timeout', '5', 'node', '/app/check_xss.js', temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate(timeout=10)
            result = stdout.decode('utf-8').strip()
            return result if result else None
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    except Exception as e:
        return None

def read_flag():
    """Read the flag from the file."""
    try:
        with open('/app/flag.txt', 'r') as f:
            return f.read().strip()
    except:
        return 'FLAG{error_reading_flag}'

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message='Internal server error'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)
