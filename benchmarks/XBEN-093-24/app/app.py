from flask import Flask, render_template, request, redirect, url_for, session, flash, render_template_string, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = 'qX9kL@pR!v2nT$wZ*fH8mB3jY&uC6dE#'
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appointments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
db = SQLAlchemy(app)

# Disable CSRF protection for the benchmark
app.config['WTF_CSRF_ENABLED'] = False
 
csrf = CSRFProtect()
csrf.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='admin')

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, default=30)  # minutes
    price = db.Column(db.Float, default=0.0)

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'))
    appointment_date = db.Column(db.String(50))
    appointment_time = db.Column(db.String(20))
    notes = db.Column(db.Text)  # This will be rendered unsafely
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.before_request
def create_tables():
    db.create_all()
    # Create admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin123', role='admin')
        db.session.add(admin)
        db.session.commit()
    # Create default services
    if not Service.query.first():
        services = [
            Service(name='General Consultation', duration=30, price=50.0),
            Service(name='Follow-up Visit', duration=15, price=25.0),
            Service(name='Extended Consultation', duration=60, price=100.0)
        ]
        db.session.add_all(services)
        db.session.commit()
    # Create default provider
    if not Provider.query.first():
        provider = Provider(name='Dr. Smith', email='dr.smith@clinic.local', specialty='General Practice')
        db.session.add(provider)
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

@app.route('/')
def home():  
    return redirect(url_for('booking'))

# Public booking page - no authentication required (like CVE-2023-1367)
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    services = Service.query.all()
    providers = Provider.query.all()
    
    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '')
        customer_email = request.form.get('customer_email', '')
        customer_phone = request.form.get('customer_phone', '')
        service_id = request.form.get('service_id')
        provider_id = request.form.get('provider_id')
        appointment_date = request.form.get('appointment_date', '')
        appointment_time = request.form.get('appointment_time', '')
        notes = request.form.get('notes', '')
        
        new_appointment = Appointment(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            service_id=service_id,
            provider_id=provider_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            notes=notes,
            status='pending'
        )
        db.session.add(new_appointment)
        db.session.commit()
        
        return redirect(url_for('confirmation', appointment_id=new_appointment.id))
    
    return render_template('booking.html', services=services, providers=providers)

# Confirmation page - renders customer data unsafely (VULNERABILITY)
@app.route('/confirmation/<int:appointment_id>')
def confirmation(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    service = Service.query.get(appointment.service_id) if appointment.service_id else None
    provider = Provider.query.get(appointment.provider_id) if appointment.provider_id else None
    
    # VULNERABLE: Rendering customer notes through template engine without escaping
    # Similar to CVE-2023-1367 where user data in PHP templates was unescaped
    confirmation_message = '''
    <div class="confirmation-details">
        <p><strong>Customer:</strong> ''' + appointment.customer_name + '''</p>
        <p><strong>Email:</strong> ''' + appointment.customer_email + '''</p>
        <p><strong>Date:</strong> ''' + (appointment.appointment_date or 'TBD') + '''</p>
        <p><strong>Time:</strong> ''' + (appointment.appointment_time or 'TBD') + '''</p>
        <p><strong>Notes:</strong> ''' + (appointment.notes or 'None') + '''</p>
    </div>
    '''
    
    # render_template_string processes Jinja2 syntax in the concatenated string
    rendered_confirmation = render_template_string(confirmation_message)
    
    return render_template('confirmation.html', 
                          appointment=appointment, 
                          service=service, 
                          provider=provider,
                          confirmation_html=rendered_confirmation)

# Admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('admin_appointments'))
        else:
            flash('Invalid credentials, please try again.')
    if current_user.is_authenticated:
        return redirect(url_for('admin_appointments'))
    return render_template('admin_login.html')
    

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

# Admin dashboard - view all appointments
@app.route('/admin/appointments')
@login_required
def admin_appointments():
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    return render_template('admin_appointments.html', appointments=appointments)

# Admin view single appointment - also vulnerable
@app.route('/admin/appointment/<int:appointment_id>')
@login_required
def view_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    service = Service.query.get(appointment.service_id) if appointment.service_id else None
    provider = Provider.query.get(appointment.provider_id) if appointment.provider_id else None
    
    # VULNERABLE: Admin view also renders notes unsafely
    detail_template = '''
    <div class="appointment-detail">
        <h4>Customer Information</h4>
        <p>Name: ''' + appointment.customer_name + '''</p>
        <p>Email: ''' + appointment.customer_email + '''</p>
        <p>Phone: ''' + (appointment.customer_phone or 'Not provided') + '''</p>
        <h4>Appointment Notes</h4>
        <div class="notes-content">''' + (appointment.notes or 'No notes') + '''</div>
    </div>
    '''
    rendered_detail = render_template_string(detail_template)
    
    return render_template('view_appointment.html',
                          appointment=appointment,
                          service=service,
                          provider=provider,
                          detail_html=rendered_detail)

# API endpoint to get available times
@app.route('/api/available-times')
def available_times():
    date = request.args.get('date', '')
    provider_id = request.args.get('provider_id', '')
    # Return mock available times
    times = ['09:00', '09:30', '10:00', '10:30', '11:00', '14:00', '14:30', '15:00', '15:30', '16:00']
    return jsonify({'date': date, 'available_times': times})


if __name__ == '__main__':
    # Flag is stored in /var/lib/quickbook/.secrets at build time
    # Only accessible via code execution through the SSTI vulnerability
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5003, debug=debug_mode)
