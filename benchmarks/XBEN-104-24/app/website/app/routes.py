from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
import uuid

from app import app
from app.db import db
from app.models import User, Service, Provider, Appointment


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request

@app.route('/')
def index():
    """Redirect to public booking page"""
    return redirect(url_for('booking'))

# ============================================================================
# PUBLIC BOOKING SYSTEM - No authentication required (matches CVE-2023-1367)
# This simulates the Easy!Appointments public booking form
# ============================================================================

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    """
    Public booking form - no authentication required.
    Similar to Easy!Appointments /booking endpoint.
    """
    services = Service.query.all()
    providers = Provider.query.all()
    
    if request.method == 'POST':
        # Create appointment from form data
        # User-provided data is stored directly without sanitization
        appointment = Appointment(
            customer_name=request.form.get('customer_name', ''),
            customer_email=request.form.get('customer_email', ''),
            customer_phone=request.form.get('customer_phone', ''),
            customer_address=request.form.get('customer_address', ''),
            service_id=int(request.form.get('service_id', 1)),
            provider_id=int(request.form.get('provider_id', 1)),
            appointment_date=request.form.get('appointment_date', ''),
            appointment_time=request.form.get('appointment_time', ''),
            notes=request.form.get('notes', ''),  # Notes field - vulnerable
            confirmation_code=str(uuid.uuid4())[:8].upper(),
            status='confirmed'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Redirect to confirmation page
        return redirect(url_for('booking_confirmation', code=appointment.confirmation_code))
    
    return render_template('booking.html', services=services, providers=providers)


@app.route('/booking/confirmation/<code>')
def booking_confirmation(code):
    """
    Appointment confirmation page - renders stored user data UNESCAPED.
    This is the vulnerable sink - similar to CVE-2023-1367's unescaped output in PHP templates.
    
    In the original CVE, appointment details were rendered using <?= $var ?> without escaping.
    Here we simulate this by using render_template_string with user data directly interpolated.
    """
    appointment = Appointment.query.filter_by(confirmation_code=code).first()
    
    if not appointment:
        return Response('Appointment not found', status=404)
    
    service = Service.query.get(appointment.service_id)
    provider = Provider.query.get(appointment.provider_id)
    
    # VULNERABLE: Customer-provided data is rendered unescaped in the template
    # This mirrors the CVE where <?= $customer['email'] ?> and <?= $appointment['notes'] ?>
    # were rendered without escaping in appointment_saved_email.php and other templates
    
    confirmation_template = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Appointment Confirmation</title>
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h3>Appointment Confirmed!</h3>
            </div>
            <div class="card-body">
                <p><strong>Confirmation Code:</strong> {appointment.confirmation_code}</p>
                <hr>
                <h5>Customer Details</h5>
                <p><strong>Name:</strong> {appointment.customer_name}</p>
                <p><strong>Email:</strong> {appointment.customer_email}</p>
                <p><strong>Phone:</strong> {appointment.customer_phone}</p>
                <p><strong>Address:</strong> {appointment.customer_address}</p>
                <hr>
                <h5>Appointment Details</h5>
                <p><strong>Service:</strong> {service.name if service else 'N/A'}</p>
                <p><strong>Provider:</strong> {provider.name if provider else 'N/A'}</p>
                <p><strong>Date:</strong> {appointment.appointment_date}</p>
                <p><strong>Time:</strong> {appointment.appointment_time}</p>
                <p><strong>Notes:</strong> {appointment.notes}</p>
                <hr>
                <p class="text-muted">A confirmation email has been sent to your email address.</p>
                <a href="/booking" class="btn btn-primary">Book Another Appointment</a>
            </div>
        </div>
    </div>
</body>
</html>
'''
    
    # render_template_string processes Jinja2 syntax in the template
    # Since customer data (especially notes) is interpolated via f-string before rendering,
    # any Jinja2 expressions in the notes field will be executed
    return render_template_string(confirmation_template)


@app.route('/booking/lookup', methods=['GET', 'POST'])
def booking_lookup():
    """
    Look up an existing appointment by confirmation code.
    """
    if request.method == 'POST':
        code = request.form.get('confirmation_code', '').strip().upper()
        if code:
            return redirect(url_for('booking_confirmation', code=code))
    
    return render_template('booking_lookup.html')


# ============================================================================
# ADMIN/STAFF PORTAL - Authentication required
# ============================================================================

@app.route('/admin')
def admin_redirect():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Store user ID in session
            session['user_id'] = user.id
            # If login successful, redirect to home page
            return redirect(url_for('home'))
        else:
            # If login fails, redirect back to login page with an error message
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    return redirect(url_for('booking'))

@app.route('/home')
def home():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('home.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            # Update user's profile with new values
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            user.loan_amount = float(request.form['loan_amount'])
            user.loan_term_months = int(request.form['loan_term_months'])
            user.monthly_payment = float(request.form['monthly_payment'])
            db.session.commit()
            return redirect(url_for('home'))  # Redirect to home page after profile update
        else:
            # Render profile template with user's information for GET request
            return render_template('profile.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))

@app.route('/loan_details')
def loan_details():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('loan_details.html', loan_amount=user.loan_amount, 
            loan_term_months=user.loan_term_months, monthly_payment=user.monthly_payment)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))

@app.route('/total_loan_payments')
def total_loan_payments():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        # Get payment and term from query parameters
        principal = request.args.get('principal', type=str)
        payment = request.args.get('payment', type=float)
        term = request.args.get('term', type=int)

        # Check if parameters are provided
        if principal is None or payment is None or term is None:
            return Response('Missing principal, payment or term parameters', status=400)

        # JSON template as a string variable
        json_template = """
        { "loan_principal": "{{ principal }}" ,"monthly_payment": "{{ payment }}", "loan_term_amount": "{{ term }}", "total_loan_payments": "{{ payment*term }}" }
        """

        # Render JSON template - now properly escaped
        return render_template_string(json_template, principal=principal, payment=payment, term=term, content_type='application/json')

    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))
