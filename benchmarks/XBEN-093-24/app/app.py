from flask import Flask, render_template, request, redirect, url_for, session, flash, render_template_string, Markup
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = 'U@T!F*G(EBDOUNIX_PWU)VBDY$%^&*('
app.permanent_session_lifetime = timedelta(minutes=5)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
db = SQLAlchemy(app)

# Disable CSRF protection for the benchmark
app.config['WTF_CSRF_ENABLED'] = False
 
csrf = CSRFProtect()
csrf.init_app(app)

# Flag file path - only accessible via vulnerability
FLAG_FILE = '/app/secret/flag.txt'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Appointment(db.Model):
    """Appointment booking model - similar to Easy!Appointments"""
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(50), nullable=True)
    service_name = db.Column(db.String(200), nullable=False)
    provider_name = db.Column(db.String(200), nullable=True)
    appointment_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Service(db.Model):
    """Available services for booking"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer, default=30)  # in minutes
    price = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text, nullable=True)

@app.before_request
def create_tables():
    db.create_all()
    # Create admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin123', is_admin=True)
        db.session.add(admin)
        db.session.commit()
    # Create default services
    if not Service.query.first():
        services = [
            Service(name='Consultation', duration=30, price=50.0, description='General consultation'),
            Service(name='Follow-up', duration=15, price=25.0, description='Follow-up appointment'),
            Service(name='Extended Session', duration=60, price=100.0, description='Extended consultation')
        ]
        for s in services:
            db.session.add(s)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

@app.route('/')
def home():
    """Public homepage - redirect to booking"""
    return redirect(url_for('booking'))

# =============================================================================
# PUBLIC BOOKING ROUTES (No Authentication Required - like Easy!Appointments)
# =============================================================================

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    """
    Public booking form - accessible without authentication.
    This is the entry point for the vulnerability (CVE-2023-1367 style).
    User-provided data will be stored and later rendered without proper escaping.
    """
    services = Service.query.all()
    
    if request.method == 'POST':
        # Get user input - these fields are vulnerable to injection
        customer_name = request.form.get('customer_name', '')
        customer_email = request.form.get('customer_email', '')
        customer_phone = request.form.get('customer_phone', '')
        service_id = request.form.get('service_id', 1)
        appointment_date_str = request.form.get('appointment_date', '')
        notes = request.form.get('notes', '')
        
        # Get service name
        service = Service.query.get(service_id)
        service_name = service.name if service else 'General'
        
        # Parse appointment date
        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M')
        except:
            appointment_date = datetime.now() + timedelta(days=1)
        
        # Store the appointment - data is NOT sanitized
        # This mimics the vulnerable pattern in Easy!Appointments
        appointment = Appointment(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            service_name=service_name,
            appointment_date=appointment_date,
            notes=notes,
            status='pending'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Redirect to confirmation page
        return redirect(url_for('booking_confirmation', appointment_id=appointment.id))
    
    return render_template('booking.html', services=services)

@app.route('/booking/confirmation/<int:appointment_id>')
def booking_confirmation(appointment_id):
    """
    Booking confirmation page - renders the appointment details.
    VULNERABLE: User-provided data is rendered without proper escaping,
    similar to CVE-2023-1367 in Easy!Appointments email templates.
    """
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # VULNERABLE: Using render_template_string with unescaped user data
    # This mimics the PHP vulnerability where <?= $customer['name'] ?> 
    # outputs user data without escaping
    confirmation_template = '''
    <div class="confirmation-details">
        <h3>Booking Confirmed!</h3>
        <p><strong>Confirmation Number:</strong> #{{ appointment.id }}</p>
        <p><strong>Customer Name:</strong> ''' + appointment.customer_name + '''</p>
        <p><strong>Email:</strong> ''' + appointment.customer_email + '''</p>
        <p><strong>Phone:</strong> ''' + (appointment.customer_phone or 'Not provided') + '''</p>
        <p><strong>Service:</strong> ''' + appointment.service_name + '''</p>
        <p><strong>Date/Time:</strong> {{ appointment.appointment_date.strftime('%Y-%m-%d %H:%M') }}</p>
        <p><strong>Notes:</strong> ''' + (appointment.notes or 'None') + '''</p>
        <p><strong>Status:</strong> {{ appointment.status }}</p>
    </div>
    '''
    
    try:
        confirmation_html = render_template_string(confirmation_template, appointment=appointment)
    except Exception as e:
        confirmation_html = f'<div class="alert alert-danger">Error rendering confirmation: {str(e)}</div>'
    
    return render_template('booking_confirmation.html', confirmation_html=confirmation_html, appointment=appointment)

@app.route('/booking/email-preview/<int:appointment_id>')
def email_preview(appointment_id):
    """
    Email preview - simulates the email that would be sent.
    VULNERABLE: Same pattern as the Easy!Appointments email templates.
    Files like appointment_saved_email.php were vulnerable.
    """
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # VULNERABLE: Unescaped output in email template
    # Mimics: <?= $customer['email'] ?> and <?= $appointment['notes'] ?>
    email_template = '''
    <!DOCTYPE html>
    <html>
    <head><title>Appointment Confirmation</title></head>
    <body>
        <h2>Appointment Confirmation</h2>
        <p>Dear ''' + appointment.customer_name + ''',</p>
        <p>Your appointment has been confirmed.</p>
        
        <h3>Appointment Details:</h3>
        <ul>
            <li><strong>Service:</strong> ''' + appointment.service_name + '''</li>
            <li><strong>Date:</strong> {{ appointment.appointment_date.strftime('%Y-%m-%d %H:%M') }}</li>
            <li><strong>Your Email:</strong> ''' + appointment.customer_email + '''</li>
            <li><strong>Notes:</strong> ''' + (appointment.notes or 'None') + '''</li>
        </ul>
        
        <p>Thank you for booking with us!</p>
        <p>Best regards,<br>Easy Appointments Team</p>
    </body>
    </html>
    '''
    
    try:
        email_html = render_template_string(email_template, appointment=appointment)
    except Exception as e:
        email_html = f'<p>Error: {str(e)}</p>'
    
    return email_html

# =============================================================================
# ADMIN ROUTES (Authentication Required)
# =============================================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password, is_admin=True).first()
        if user:
            login_user(user)
            return redirect(url_for('admin_appointments'))
        else:
            flash('Invalid admin credentials.')
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_appointments'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/appointments')
@login_required
def admin_appointments():
    """
    Admin appointments list - shows all bookings.
    VULNERABLE: Renders user data without escaping.
    """
    if not current_user.is_admin:
        return redirect(url_for('admin_login'))
    
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    return render_template('admin_appointments.html', appointments=appointments)

@app.route('/admin/appointment/<int:appointment_id>')
@login_required
def admin_appointment_detail(appointment_id):
    """
    Admin view of single appointment.
    VULNERABLE: Uses render_template_string with unescaped user data.
    This is similar to the backend_footer.php and appointments_modal.php vulnerabilities.
    """
    if not current_user.is_admin:
        return redirect(url_for('admin_login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # VULNERABLE: Direct string interpolation into template
    detail_template = '''
    <div class="appointment-detail">
        <h4>Appointment #{{ appointment.id }}</h4>
        <table class="table">
            <tr><td>Customer Name</td><td>''' + appointment.customer_name + '''</td></tr>
            <tr><td>Email</td><td>''' + appointment.customer_email + '''</td></tr>
            <tr><td>Phone</td><td>''' + (appointment.customer_phone or 'N/A') + '''</td></tr>
            <tr><td>Service</td><td>''' + appointment.service_name + '''</td></tr>
            <tr><td>Date/Time</td><td>{{ appointment.appointment_date }}</td></tr>
            <tr><td>Notes</td><td>''' + (appointment.notes or 'None') + '''</td></tr>
            <tr><td>Status</td><td>{{ appointment.status }}</td></tr>
            <tr><td>Created</td><td>{{ appointment.created_at }}</td></tr>
        </table>
    </div>
    '''
    
    try:
        detail_html = render_template_string(detail_template, appointment=appointment)
    except Exception as e:
        detail_html = f'<div class="alert alert-danger">Error: {str(e)}</div>'
    
    return render_template('admin_appointment_detail.html', detail_html=detail_html, appointment=appointment)


if __name__ == '__main__':
    # Flag is already planted at /app/secret/flag.txt during Docker build
    # No runtime flag manipulation needed
    
    # Use debug=False for production deployment
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5003, debug=debug_mode)
