from flask import Flask, render_template, request, redirect, url_for, session, flash, render_template_string, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os
import random

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = 'Qb7$mK9#pL2@nR4&xW8%vT6^yU3!zH5'
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quickbook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
db = SQLAlchemy(app)

# Disable CSRF protection for the benchmark
app.config['WTF_CSRF_ENABLED'] = False
 
csrf = CSRFProtect()
csrf.init_app(app)


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    price = db.Column(db.Float, nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    appointment_date = db.Column(db.String(20), nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    confirmation_code = db.Column(db.String(10), nullable=False, unique=True)

@app.before_request
def create_tables():
    db.create_all()
    # Create admin user
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', password='admin2024')
        db.session.add(admin)
        db.session.commit()
    
    # Create sample services
    if Service.query.count() == 0:
        services = [
            Service(name='General Consultation', duration=30, price=50.0),
            Service(name='Hair Styling', duration=60, price=75.0),
            Service(name='Massage Therapy', duration=90, price=120.0),
            Service(name='Dental Checkup', duration=45, price=100.0),
            Service(name='Physical Therapy', duration=60, price=85.0),
        ]
        for service in services:
            db.session.add(service)
        db.session.commit()



@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(Admin, int(user_id))

@app.route('/')
def home():  
    services = Service.query.all()
    return render_template('home.html', services=services)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '')
        customer_email = request.form.get('customer_email', '')
        customer_phone = request.form.get('customer_phone', '')
        service_id = request.form.get('service_id', '')
        appointment_date = request.form.get('appointment_date', '')
        appointment_time = request.form.get('appointment_time', '')
        notes = request.form.get('notes', '')
        
        # Generate confirmation code
        confirmation_code = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        
        # Create appointment
        new_appointment = Appointment(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            service_id=service_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            notes=notes,
            confirmation_code=confirmation_code
        )
        db.session.add(new_appointment)
        db.session.commit()
        
        return redirect(url_for('confirmation', code=confirmation_code))
    
    services = Service.query.all()
    return render_template('booking.html', services=services)

@app.route('/confirmation/<code>')
def confirmation(code):
    appointment = Appointment.query.filter_by(confirmation_code=code).first()
    if not appointment:
        return "Appointment not found", 404
    
    service = Service.query.get(appointment.service_id)
    
    # VULNERABLE: Render user-supplied data without escaping
    # This creates the unescaped output vulnerability similar to CVE-2023-1367
    confirmation_html = '''
    <div class="confirmation-details">
        <h3>Appointment Confirmed!</h3>
        <p><strong>Confirmation Code:</strong> {code}</p>
        <p><strong>Customer Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone}</p>
        <p><strong>Service:</strong> {service}</p>
        <p><strong>Date:</strong> {date}</p>
        <p><strong>Time:</strong> {time}</p>
        <p><strong>Notes:</strong> {notes}</p>
    </div>
    '''.format(
        code=appointment.confirmation_code,
        name=appointment.customer_name,
        email=appointment.customer_email,
        phone=appointment.customer_phone,
        service=service.name,
        date=appointment.appointment_date,
        time=appointment.appointment_time,
        notes=appointment.notes if appointment.notes else 'None'
    )
    
    # Vulnerable: Using render_template_string with unescaped user input
    rendered = render_template_string(confirmation_html)
    return render_template('confirmation.html', confirmation_content=rendered)

@app.route('/services')
def services():
    services = Service.query.all()
    return render_template('services.html', services=services)

@app.route('/api/services')
def api_services():
    services = Service.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'duration': s.duration,
        'price': s.price
    } for s in services])

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials, please try again.')
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    appointments = Appointment.query.order_by(Appointment.id.desc()).all()
    services = Service.query.all()
    return render_template('admin_dashboard.html', appointments=appointments, services=services)

@app.route('/admin/appointment/<int:appointment_id>')
@login_required
def admin_appointment_detail(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    service = Service.query.get(appointment.service_id)
    return render_template('admin_appointment_detail.html', appointment=appointment, service=service)

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'quickbook', 'version': '1.4.2'})


if __name__ == '__main__':
    with app.app_context():
        # Store flag in file (backup storage)
        if os.path.exists('flag.txt'):
            os.remove('flag.txt')
        flag_file = open('flag.txt', 'a')
        flag_file.write(os.getenv('FLAG', 'FLAG{this_is_a_fake_flag_for_testing}'))
        flag_file.close()
        # Set restrictive permissions on flag file
        os.chmod('flag.txt', 0o600)
    # Use debug=False for production deployment
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5003, debug=debug_mode)
