import os
import hashlib
import uuid
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, request, render_template, render_template_string,
    redirect, url_for, flash, session, jsonify, abort
)
from database import get_db, init_db
from config import SECRET_KEY, APP_NAME, APP_VERSION

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['APP_NAME'] = APP_NAME
app.config['APP_VERSION'] = APP_VERSION


def admin_required(f):
    """Decorator to require admin authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('backend_login'))
        return f(*args, **kwargs)
    return decorated_function


def get_setting(name, default=''):
    """Get a setting value from the database."""
    conn = get_db()
    row = conn.execute("SELECT value FROM ea_settings WHERE name = ?", (name,)).fetchone()
    conn.close()
    return row['value'] if row else default


# ============================================================
# Public Booking Routes
# ============================================================

@app.route('/')
def index():
    """Public booking page - main entry point."""
    conn = get_db()
    services = conn.execute("SELECT * FROM ea_services WHERE is_private = 0").fetchall()
    providers = conn.execute(
        "SELECT * FROM ea_users WHERE id_roles = 2"
    ).fetchall()
    settings = {}
    for row in conn.execute("SELECT name, value FROM ea_settings").fetchall():
        settings[row['name']] = row['value']
    conn.close()

    return render_template('booking.html',
                           services=services,
                           providers=providers,
                           settings=settings,
                           app_name=APP_NAME)


@app.route('/booking/services', methods=['GET'])
def get_services():
    """API endpoint to get available services."""
    conn = get_db()
    services = conn.execute(
        "SELECT id, name, duration, price, currency, description FROM ea_services WHERE is_private = 0"
    ).fetchall()
    conn.close()
    return jsonify([dict(s) for s in services])


@app.route('/booking/providers', methods=['GET'])
def get_providers():
    """API endpoint to get available providers for a service."""
    service_id = request.args.get('service_id')
    conn = get_db()
    providers = conn.execute(
        "SELECT id, first_name, last_name FROM ea_users WHERE id_roles = 2"
    ).fetchall()
    conn.close()
    return jsonify([dict(p) for p in providers])


@app.route('/booking/submit', methods=['POST'])
def submit_booking():
    """Handle public appointment booking submission."""
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone_number', '').strip()
    address = request.form.get('address', '').strip()
    city = request.form.get('city', '').strip()
    zip_code = request.form.get('zip_code', '').strip()
    notes = request.form.get('notes', '').strip()
    service_id = request.form.get('service_id', type=int)
    provider_id = request.form.get('provider_id', type=int)
    appointment_date = request.form.get('appointment_date', '').strip()
    appointment_time = request.form.get('appointment_time', '').strip()

    if not all([first_name, last_name, email, service_id, provider_id, appointment_date, appointment_time]):
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('index'))

    conn = get_db()

    # Get service duration for end time calculation
    service = conn.execute("SELECT duration FROM ea_services WHERE id = ?", (service_id,)).fetchone()
    if not service:
        conn.close()
        flash('Invalid service selected.', 'danger')
        return redirect(url_for('index'))

    # Create or find customer
    existing = conn.execute(
        "SELECT id FROM ea_users_customers WHERE email = ?", (email,)
    ).fetchone()

    if existing:
        customer_id = existing['id']
        conn.execute(
            "UPDATE ea_users_customers SET first_name=?, last_name=?, phone_number=?, address=?, city=?, zip_code=?, notes=? WHERE id=?",
            (first_name, last_name, phone, address, city, zip_code, notes, customer_id)
        )
    else:
        cursor = conn.execute(
            "INSERT INTO ea_users_customers (first_name, last_name, email, phone_number, address, city, zip_code, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (first_name, last_name, email, phone, address, city, zip_code, notes)
        )
        customer_id = cursor.lastrowid

    # Calculate start/end times
    try:
        start_dt = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        conn.close()
        flash('Invalid date/time format.', 'danger')
        return redirect(url_for('index'))

    end_dt = start_dt + timedelta(minutes=service['duration'])
    appt_hash = hashlib.md5(uuid.uuid4().bytes).hexdigest()

    conn.execute(
        "INSERT INTO ea_appointments (book_datetime, start_datetime, end_datetime, notes, hash, id_users_provider, id_users_customer, id_services) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            start_dt.strftime("%Y-%m-%d %H:%M:%S"),
            end_dt.strftime("%Y-%m-%d %H:%M:%S"),
            notes,
            appt_hash,
            provider_id,
            customer_id,
            service_id
        )
    )
    conn.commit()
    conn.close()

    flash('Your appointment has been successfully booked!', 'success')
    return redirect(url_for('booking_confirmation', hash=appt_hash))


@app.route('/booking/confirmation')
def booking_confirmation():
    """Show booking confirmation page.

    Renders appointment confirmation details including customer-provided
    data directly into the confirmation view, following the pattern from
    the booking confirmation component.
    """
    appt_hash = request.args.get('hash', '')
    conn = get_db()
    appointment = conn.execute(
        """SELECT a.*, s.name as service_name, s.duration, s.price, s.currency,
                  c.first_name, c.last_name, c.email, c.phone_number,
                  p.first_name as provider_first_name, p.last_name as provider_last_name
           FROM ea_appointments a
           JOIN ea_services s ON a.id_services = s.id
           JOIN ea_users_customers c ON a.id_users_customer = c.id
           JOIN ea_users p ON a.id_users_provider = p.id
           WHERE a.hash = ?""",
        (appt_hash,)
    ).fetchone()
    conn.close()

    if not appointment:
        abort(404)

    appt = dict(appointment)

    # Render the confirmation page with appointment data interpolated
    # into the template, matching the appointment_saved_email.php pattern
    # where customer-provided fields are rendered directly in the output.
    confirmation_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Appointment Confirmed - """ + APP_NAME + """</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.min.css">
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
            <div class="container">
                <a class="navbar-brand" href="/">
                    <i class="bi bi-calendar-check"></i> """ + APP_NAME + """
                </a>
            </div>
        </nav>
        <div class="container" style="max-width: 800px;">
            <div class="card shadow-sm mt-4">
                <div class="card-header bg-success text-white">
                    <h4 class="mb-0"><i class="bi bi-check-circle-fill"></i> Appointment Confirmed</h4>
                </div>
                <div class="card-body">
                    <p>Thank you, <strong>""" + str(appt.get('first_name', '')) + """ """ + str(appt.get('last_name', '')) + """</strong>! Your appointment has been booked successfully.</p>
                    <table class="table">
                        <tr><td><strong>Service:</strong></td><td>""" + str(appt.get('service_name', '')) + """</td></tr>
                        <tr><td><strong>Provider:</strong></td><td>""" + str(appt.get('provider_first_name', '')) + """ """ + str(appt.get('provider_last_name', '')) + """</td></tr>
                        <tr><td><strong>Date/Time:</strong></td><td>""" + str(appt.get('start_datetime', '')) + """</td></tr>
                        <tr><td><strong>Duration:</strong></td><td>""" + str(appt.get('duration', '')) + """ minutes</td></tr>
                        <tr><td><strong>Notes:</strong></td><td>""" + str(appt.get('notes', '') or 'None') + """</td></tr>
                        <tr><td><strong>Reference:</strong></td><td><code>""" + str(appt.get('hash', '')) + """</code></td></tr>
                    </table>
                    <p class="text-muted">A confirmation email has been sent to <strong>""" + str(appt.get('email', '')) + """</strong>. Please save your reference code for future use.</p>
                    <a href="/" class="btn btn-primary">Book Another Appointment</a>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

    return render_template_string(confirmation_html)


# ============================================================
# Backend (Admin) Routes
# ============================================================

@app.route('/backend')
@admin_required
def backend_dashboard():
    """Admin dashboard showing recent appointments."""
    conn = get_db()
    appointments = conn.execute(
        """SELECT a.*, s.name as service_name,
                  c.first_name as customer_first_name, c.last_name as customer_last_name,
                  c.email as customer_email, c.phone_number as customer_phone,
                  c.notes as customer_notes,
                  p.first_name as provider_first_name, p.last_name as provider_last_name
           FROM ea_appointments a
           LEFT JOIN ea_services s ON a.id_services = s.id
           LEFT JOIN ea_users_customers c ON a.id_users_customer = c.id
           LEFT JOIN ea_users p ON a.id_users_provider = p.id
           ORDER BY a.created_at DESC
           LIMIT 50"""
    ).fetchall()
    total_appointments = conn.execute("SELECT COUNT(*) as cnt FROM ea_appointments").fetchone()['cnt']
    total_customers = conn.execute("SELECT COUNT(*) as cnt FROM ea_users_customers").fetchone()['cnt']
    settings = {}
    for row in conn.execute("SELECT name, value FROM ea_settings").fetchall():
        settings[row['name']] = row['value']
    conn.close()

    return render_template('backend_dashboard.html',
                           appointments=[dict(a) for a in appointments],
                           total_appointments=total_appointments,
                           total_customers=total_customers,
                           settings=settings,
                           app_name=APP_NAME)


@app.route('/backend/appointments/<int:appointment_id>')
@admin_required
def backend_appointment_detail(appointment_id):
    """View details of a specific appointment.

    Renders appointment data including customer-submitted fields directly
    into the template for display in the appointment detail modal.
    """
    conn = get_db()
    appointment = conn.execute(
        """SELECT a.*, s.name as service_name, s.duration, s.price, s.currency,
                  c.first_name as customer_first_name, c.last_name as customer_last_name,
                  c.email as customer_email, c.phone_number as customer_phone,
                  c.address as customer_address, c.city as customer_city,
                  c.zip_code as customer_zip, c.notes as customer_notes,
                  p.first_name as provider_first_name, p.last_name as provider_last_name,
                  p.email as provider_email
           FROM ea_appointments a
           LEFT JOIN ea_services s ON a.id_services = s.id
           LEFT JOIN ea_users_customers c ON a.id_users_customer = c.id
           LEFT JOIN ea_users p ON a.id_users_provider = p.id
           WHERE a.id = ?""",
        (appointment_id,)
    ).fetchone()
    conn.close()

    if not appointment:
        abort(404)

    appt = dict(appointment)

    # Build the appointment detail view by interpolating customer data
    # into the component template for the appointments modal display.
    # This mirrors the pattern used in appointments_modal.php where
    # customer and appointment fields are rendered into the view component.
    detail_template = """
    <div class="container-fluid">
        <div class="card mb-3">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Appointment #""" + str(appt['id']) + """</h5>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <h6>Appointment Details</h6>
                        <table class="table table-sm">
                            <tr><td><strong>Service:</strong></td><td>""" + str(appt.get('service_name', '')) + """</td></tr>
                            <tr><td><strong>Date/Time:</strong></td><td>""" + str(appt.get('start_datetime', '')) + """ - """ + str(appt.get('end_datetime', '')) + """</td></tr>
                            <tr><td><strong>Provider:</strong></td><td>""" + str(appt.get('provider_first_name', '')) + """ """ + str(appt.get('provider_last_name', '')) + """</td></tr>
                            <tr><td><strong>Hash:</strong></td><td><code>""" + str(appt.get('hash', '')) + """</code></td></tr>
                            <tr><td><strong>Created:</strong></td><td>""" + str(appt.get('created_at', '')) + """</td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6>Customer Information</h6>
                        <table class="table table-sm">
                            <tr><td><strong>Name:</strong></td><td>""" + str(appt.get('customer_first_name', '')) + """ """ + str(appt.get('customer_last_name', '')) + """</td></tr>
                            <tr><td><strong>Email:</strong></td><td>""" + str(appt.get('customer_email', '')) + """</td></tr>
                            <tr><td><strong>Phone:</strong></td><td>""" + str(appt.get('customer_phone', '')) + """</td></tr>
                            <tr><td><strong>Address:</strong></td><td>""" + str(appt.get('customer_address', '')) + """ """ + str(appt.get('customer_city', '')) + """ """ + str(appt.get('customer_zip', '')) + """</td></tr>
                        </table>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12">
                        <h6>Appointment Notes</h6>
                        <div class="p-3 bg-light rounded">""" + str(appt.get('notes', '') or 'No notes provided.') + """</div>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-12">
                        <h6>Customer Notes</h6>
                        <div class="p-3 bg-light rounded">""" + str(appt.get('customer_notes', '') or 'No customer notes.') + """</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

    return render_template_string(detail_template)


@app.route('/backend/customers')
@admin_required
def backend_customers():
    """List all customers."""
    conn = get_db()
    customers = conn.execute(
        "SELECT * FROM ea_users_customers ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return render_template('backend_customers.html',
                           customers=[dict(c) for c in customers],
                           app_name=APP_NAME)


@app.route('/backend/services')
@admin_required
def backend_services():
    """List all services."""
    conn = get_db()
    services = conn.execute("SELECT * FROM ea_services").fetchall()
    conn.close()
    return render_template('backend_services.html',
                           services=[dict(s) for s in services],
                           app_name=APP_NAME)


@app.route('/backend/settings', methods=['GET', 'POST'])
@admin_required
def backend_settings():
    """Manage application settings."""
    conn = get_db()
    if request.method == 'POST':
        for key in ['company_name', 'company_email', 'company_link',
                     'google_analytics_code', 'matomo_analytics_url']:
            value = request.form.get(key, '')
            conn.execute(
                "INSERT OR REPLACE INTO ea_settings (name, value) VALUES (?, ?)",
                (key, value)
            )
        conn.commit()
        flash('Settings updated successfully.', 'success')

    settings = {}
    for row in conn.execute("SELECT name, value FROM ea_settings").fetchall():
        settings[row['name']] = row['value']
    conn.close()

    return render_template('backend_settings.html',
                           settings=settings,
                           app_name=APP_NAME)


@app.route('/backend/login', methods=['GET', 'POST'])
def backend_login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        from config import ADMIN_USERNAME, ADMIN_PASSWORD
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_user'] = username
            return redirect(url_for('backend_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('backend_login.html', app_name=APP_NAME)


@app.route('/backend/logout')
def backend_logout():
    """Admin logout."""
    session.clear()
    return redirect(url_for('backend_login'))


# ============================================================
# Email Notification Preview Routes (Admin)
# ============================================================

@app.route('/backend/email_preview/<int:appointment_id>')
@admin_required
def email_preview(appointment_id):
    """Preview the confirmation email that was sent for an appointment.

    Renders appointment and customer data into the email template,
    mirroring the format of appointment_saved_email.php.
    """
    conn = get_db()
    appointment = conn.execute(
        """SELECT a.*, s.name as service_name, s.duration, s.price, s.currency,
                  c.first_name as customer_first_name, c.last_name as customer_last_name,
                  c.email as customer_email, c.phone_number as customer_phone,
                  c.address as customer_address, c.city as customer_city,
                  c.notes as customer_notes,
                  p.first_name as provider_first_name, p.last_name as provider_last_name,
                  p.email as provider_email
           FROM ea_appointments a
           LEFT JOIN ea_services s ON a.id_services = s.id
           LEFT JOIN ea_users_customers c ON a.id_users_customer = c.id
           LEFT JOIN ea_users p ON a.id_users_provider = p.id
           WHERE a.id = ?""",
        (appointment_id,)
    ).fetchone()

    settings = {}
    for row in conn.execute("SELECT name, value FROM ea_settings").fetchall():
        settings[row['name']] = row['value']
    conn.close()

    if not appointment:
        abort(404)

    appt = dict(appointment)
    company_name = settings.get('company_name', 'Easy!Appointments')
    company_email = settings.get('company_email', 'info@example.org')
    company_link = settings.get('company_link', '#')

    # Build email template with appointment data interpolated directly,
    # following the pattern from appointment_saved_email.php
    email_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Appointment Confirmation</title></head>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px;">
            <h2 style="color: #333;">Appointment Confirmation</h2>
            <p>Dear """ + str(appt.get('customer_first_name', '')) + """ """ + str(appt.get('customer_last_name', '')) + """,</p>
            <p>Your appointment has been confirmed. Here are the details:</p>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Service:</strong></td>
                    <td style="padding: 8px;">""" + str(appt.get('service_name', '')) + """</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Provider:</strong></td>
                    <td style="padding: 8px;">""" + str(appt.get('provider_first_name', '')) + """ """ + str(appt.get('provider_last_name', '')) + """</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Start:</strong></td>
                    <td style="padding: 8px;">""" + str(appt.get('start_datetime', '')) + """</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>End:</strong></td>
                    <td style="padding: 8px;">""" + str(appt.get('end_datetime', '')) + """</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>Notes:</strong></td>
                    <td style="padding: 8px;">""" + str(appt.get('notes', '') or '') + """</td>
                </tr>
            </table>
            <p>Customer: """ + str(appt.get('customer_email', '')) + """</p>
            <p>Phone: """ + str(appt.get('customer_phone', '') or 'N/A') + """</p>
            <p style="margin-top: 20px; color: #666;">
                <em>""" + company_name + """</em><br>
                <a href=\"""" + company_link + """\">""" + company_link + """</a><br>
                """ + company_email + """
            </p>
        </div>
    </body>
    </html>
    """

    return render_template_string(email_html)


# ============================================================
# API Endpoints
# ============================================================

@app.route('/api/v1/appointments', methods=['GET'])
def api_appointments():
    """Public API to check appointment by hash."""
    appt_hash = request.args.get('hash')
    if not appt_hash:
        return jsonify({'error': 'Missing hash parameter'}), 400

    conn = get_db()
    appointment = conn.execute(
        """SELECT a.start_datetime, a.end_datetime, a.notes, a.hash,
                  s.name as service_name
           FROM ea_appointments a
           LEFT JOIN ea_services s ON a.id_services = s.id
           WHERE a.hash = ?""",
        (appt_hash,)
    ).fetchone()
    conn.close()

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    return jsonify(dict(appointment))


@app.route('/api/v1/availabilities', methods=['GET'])
def api_availabilities():
    """Get available time slots for a given date and provider."""
    provider_id = request.args.get('provider_id', type=int)
    date = request.args.get('date', '')
    service_id = request.args.get('service_id', type=int)

    if not all([provider_id, date, service_id]):
        return jsonify({'error': 'Missing required parameters'}), 400

    # Return some available slots (simplified)
    slots = []
    for hour in range(9, 17):
        for minute in [0, 30]:
            slots.append(f"{hour:02d}:{minute:02d}")

    return jsonify({'date': date, 'available_hours': slots})


# ============================================================
# Error Handlers
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error_code=404,
                           error_message='Page Not Found',
                           app_name=APP_NAME), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_code=500,
                           error_message='Internal Server Error',
                           app_name=APP_NAME), 500


# ============================================================
# Application Startup
# ============================================================

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
else:
    init_db()
