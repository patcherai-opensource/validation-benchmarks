import sqlite3
import os
import hashlib
import time
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, render_template_string, redirect, url_for, jsonify, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_PATH = '/tmp/scheduler.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        duration INTEGER NOT NULL DEFAULT 30,
        description TEXT,
        color TEXT DEFAULT '#2c8c6c',
        is_active INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS providers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        is_active INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE,
        start_datetime TEXT NOT NULL,
        end_datetime TEXT NOT NULL,
        location TEXT,
        notes TEXT,
        color TEXT DEFAULT '#2c8c6c',
        status TEXT DEFAULT 'pending',
        id_services INTEGER,
        id_providers INTEGER,
        id_customers INTEGER,
        is_unavailability INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone_number TEXT,
        address TEXT,
        city TEXT,
        zip_code TEXT,
        notes TEXT,
        language TEXT DEFAULT 'english',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        role TEXT DEFAULT 'admin',
        language TEXT DEFAULT 'english',
        is_active INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        value TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS consents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        ip TEXT,
        type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Default settings
    defaults = [
        ('company_name', 'QuickSchedule'),
        ('company_email', 'info@quickschedule.local'),
        ('company_link', 'https://quickschedule.local'),
        ('date_format', 'DMY'),
        ('time_format', '24h'),
        ('display_cookie_notice', '0'),
        ('require_captcha', '0'),
        ('booking_field_notes', '1'),
    ]
    for name, value in defaults:
        c.execute("INSERT OR IGNORE INTO settings (name, value) VALUES (?, ?)", (name, value))

    # Default admin
    c.execute("INSERT OR IGNORE INTO users (username, password, first_name, last_name, email, role) "
              "VALUES ('admin', 'admin123', 'System', 'Administrator', 'admin@quickschedule.local', 'admin')")

    # Default services
    c.execute("INSERT OR IGNORE INTO services (id, name, duration, description) VALUES "
              "(1, 'General Consultation', 30, 'Standard 30-minute consultation session')")
    c.execute("INSERT OR IGNORE INTO services (id, name, duration, description) VALUES "
              "(2, 'Follow-up Session', 20, 'Quick follow-up and status check')")
    c.execute("INSERT OR IGNORE INTO services (id, name, duration, description) VALUES "
              "(3, 'Extended Consultation', 60, 'In-depth extended consultation')")

    # Default provider
    c.execute("INSERT OR IGNORE INTO providers (id, first_name, last_name, email) VALUES "
              "(1, 'Dr. Sarah', 'Mitchell', 'sarah.mitchell@quickschedule.local')")

    conn.commit()
    conn.close()


init_db()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated


def get_setting(name, default=''):
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE name=?", (name,)).fetchone()
    conn.close()
    return row['value'] if row else default


# ──────────────────── Public pages ────────────────────

@app.route('/')
def index():
    company_name = get_setting('company_name')
    conn = get_db()
    services = conn.execute("SELECT * FROM services WHERE is_active=1").fetchall()
    conn.close()

    service_cards = ''
    for svc in services:
        service_cards += f'''
            <div class="service-card">
                <h3>{svc['name']}</h3>
                <p>{svc['duration']} minutes</p>
                <p>{svc['description']}</p>
                <a href="/schedule?service_id={svc['id']}" class="btn-book">Book Now</a>
            </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - Online Scheduling</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; color: #333; }}
        .site-header {{ background: #2c8c6c; color: #fff; padding: 18px 30px; }}
        .site-header h1 {{ font-size: 22px; display: inline; }}
        .site-header nav {{ float: right; margin-top: 3px; }}
        .site-header nav a {{ color: #fff; text-decoration: none; margin-left: 18px; font-size: 14px; }}
        .site-header nav a:hover {{ text-decoration: underline; }}
        .hero {{ text-align: center; padding: 40px 20px 20px; }}
        .hero h2 {{ font-size: 28px; margin-bottom: 10px; }}
        .hero p {{ color: #666; max-width: 600px; margin: 0 auto; }}
        .services {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 24px; padding: 30px 20px; max-width: 1100px; margin: 0 auto; }}
        .service-card {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 6px; padding: 24px; width: 300px; text-align: center; }}
        .service-card h3 {{ color: #2c8c6c; margin-bottom: 8px; }}
        .service-card p {{ font-size: 14px; color: #555; margin-bottom: 6px; }}
        .btn-book {{ display: inline-block; margin-top: 12px; background: #2c8c6c; color: #fff; padding: 10px 24px; border-radius: 4px; text-decoration: none; }}
        .btn-book:hover {{ background: #247d5f; }}
        .site-footer {{ text-align: center; padding: 20px; font-size: 13px; color: #888; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="site-header">
        <h1>{company_name}</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/schedule">Book Appointment</a>
            <a href="/admin/login">Staff Portal</a>
        </nav>
    </div>
    <div class="hero">
        <h2>Book Your Appointment Online</h2>
        <p>Choose from our available services and schedule at your convenience.</p>
    </div>
    <div class="services">
        {service_cards}
    </div>
    <div class="site-footer">
        &copy; 2024 {company_name}. All rights reserved.
    </div>
</body>
</html>'''


@app.route('/schedule')
def schedule_page():
    company_name = get_setting('company_name')
    service_id = request.args.get('service_id', '1')

    conn = get_db()
    services = conn.execute("SELECT * FROM services WHERE is_active=1").fetchall()
    providers = conn.execute("SELECT * FROM providers WHERE is_active=1").fetchall()
    conn.close()

    svc_options = ''
    for s in services:
        selected = 'selected' if str(s['id']) == str(service_id) else ''
        svc_options += f'<option value="{s["id"]}" {selected}>{s["name"]} ({s["duration"]} min)</option>'

    prov_options = ''
    for p in providers:
        prov_options += f'<option value="{p["id"]}">{p["first_name"]} {p["last_name"]}</option>'

    time_slots = ''
    for h in range(9, 17):
        t = f'{h:02d}:00'
        label = f'{h:02d}:00' if h < 12 else f'{h-12 if h>12 else 12}:00 PM'
        if h < 12:
            label = f'{h}:00 AM'
        time_slots += f'<option value="{t}">{label}</option>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Appointment - {company_name}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; }}
        .site-header {{ background: #2c8c6c; color: #fff; padding: 18px 30px; }}
        .site-header h1 {{ font-size: 22px; display: inline; }}
        .site-header nav {{ float: right; margin-top: 3px; }}
        .site-header nav a {{ color: #fff; text-decoration: none; margin-left: 18px; font-size: 14px; }}
        .booking-form {{ max-width: 700px; margin: 30px auto; background: #fff; padding: 32px; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
        .booking-form h2 {{ margin-bottom: 20px; color: #2c8c6c; }}
        .step-title {{ font-size: 16px; font-weight: 600; margin: 24px 0 12px; color: #444; border-bottom: 1px solid #e0e0e0; padding-bottom: 6px; }}
        .field {{ margin-bottom: 14px; }}
        .field label {{ display: block; font-size: 14px; font-weight: 600; margin-bottom: 4px; }}
        .field label .req {{ color: #d33; }}
        .field input, .field select, .field textarea {{ width: 100%; padding: 9px 12px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }}
        .field textarea {{ resize: vertical; min-height: 80px; }}
        .row {{ display: flex; gap: 16px; }}
        .row .field {{ flex: 1; }}
        .btn-submit {{ background: #2c8c6c; color: #fff; border: none; padding: 12px 32px; border-radius: 4px; font-size: 16px; cursor: pointer; margin-top: 10px; }}
        .btn-submit:hover {{ background: #247d5f; }}
    </style>
</head>
<body>
    <div class="site-header">
        <h1>{company_name}</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/schedule">Book Appointment</a>
        </nav>
    </div>
    <div class="booking-form">
        <h2>Schedule an Appointment</h2>
        <form method="POST" action="/api/bookings/register">

            <div class="step-title">Service &amp; Provider</div>
            <div class="row">
                <div class="field">
                    <label>Service <span class="req">*</span></label>
                    <select name="service_id" required>{svc_options}</select>
                </div>
                <div class="field">
                    <label>Provider <span class="req">*</span></label>
                    <select name="provider_id" required>{prov_options}</select>
                </div>
            </div>

            <div class="step-title">Date &amp; Time</div>
            <div class="row">
                <div class="field">
                    <label>Date <span class="req">*</span></label>
                    <input type="date" name="appointment_date" required>
                </div>
                <div class="field">
                    <label>Time <span class="req">*</span></label>
                    <select name="appointment_time" required>
                        <option value="">Select time</option>
                        {time_slots}
                    </select>
                </div>
            </div>

            <div class="step-title">Your Information</div>
            <div class="row">
                <div class="field">
                    <label>First Name <span class="req">*</span></label>
                    <input type="text" name="first_name" required maxlength="100">
                </div>
                <div class="field">
                    <label>Last Name <span class="req">*</span></label>
                    <input type="text" name="last_name" required maxlength="120">
                </div>
            </div>
            <div class="row">
                <div class="field">
                    <label>Email <span class="req">*</span></label>
                    <input type="email" name="email" required maxlength="120">
                </div>
                <div class="field">
                    <label>Phone Number</label>
                    <input type="tel" name="phone_number" maxlength="60">
                </div>
            </div>
            <div class="row">
                <div class="field">
                    <label>Address</label>
                    <input type="text" name="address" maxlength="200">
                </div>
                <div class="field">
                    <label>City</label>
                    <input type="text" name="city" maxlength="120">
                </div>
            </div>
            <div class="field">
                <label>Notes</label>
                <textarea name="notes" placeholder="Any additional information or special requests..."></textarea>
            </div>

            <button type="submit" class="btn-submit">Confirm Appointment</button>
        </form>
    </div>
</body>
</html>'''


@app.route('/api/bookings/register', methods=['POST'])
def register_booking():
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    phone_number = request.form.get('phone_number', '').strip()
    address = request.form.get('address', '').strip()
    city = request.form.get('city', '').strip()
    notes = request.form.get('notes', '').strip()
    service_id = request.form.get('service_id', '1')
    provider_id = request.form.get('provider_id', '1')
    appointment_date = request.form.get('appointment_date', '')
    appointment_time = request.form.get('appointment_time', '')

    if not first_name or not last_name or not email or not appointment_date or not appointment_time:
        return 'Missing required fields', 400

    conn = get_db()

    # Upsert customer
    existing = conn.execute("SELECT id FROM customers WHERE email=?", (email,)).fetchone()
    if existing:
        customer_id = existing['id']
        conn.execute("UPDATE customers SET first_name=?, last_name=?, phone_number=?, address=?, city=?, notes=? WHERE id=?",
                     (first_name, last_name, phone_number, address, city, notes, customer_id))
    else:
        cur = conn.execute("INSERT INTO customers (first_name, last_name, email, phone_number, address, city, notes) "
                           "VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (first_name, last_name, email, phone_number, address, city, notes))
        customer_id = cur.lastrowid

    appt_hash = hashlib.md5(f"{customer_id}-{time.time()}".encode()).hexdigest()

    start_dt = f"{appointment_date} {appointment_time}:00"
    svc = conn.execute("SELECT duration FROM services WHERE id=?", (service_id,)).fetchone()
    duration = svc['duration'] if svc else 30
    try:
        start_obj = datetime.strptime(start_dt, "%Y-%m-%d %H:%M:%S")
        end_obj = start_obj + timedelta(minutes=duration)
        end_dt = end_obj.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        end_dt = start_dt

    conn.execute('''INSERT INTO appointments (hash, start_datetime, end_datetime, notes,
                    id_services, id_providers, id_customers, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')''',
                 (appt_hash, start_dt, end_dt, notes, service_id, provider_id, customer_id))
    conn.commit()
    conn.close()

    company_name = get_setting('company_name')
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Booking Confirmed - {company_name}</title>
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; }}
    .site-header {{ background: #2c8c6c; color: #fff; padding: 18px 30px; }}
    .site-header h1 {{ font-size: 22px; }}
    .msg {{ max-width: 600px; margin: 40px auto; background: #fff; padding: 32px; border-radius: 6px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
    .msg h2 {{ color: #2c8c6c; margin-bottom: 12px; }}
    .msg p {{ color: #555; margin-bottom: 8px; }}
    .btn {{ display: inline-block; margin-top: 18px; background: #2c8c6c; color: #fff; padding: 10px 24px; border-radius: 4px; text-decoration: none; }}
</style></head>
<body>
    <div class="site-header"><h1>{company_name}</h1></div>
    <div class="msg">
        <h2>Appointment Confirmed</h2>
        <p>Thank you, {first_name}. Your appointment has been registered successfully.</p>
        <p>A confirmation will be sent to <strong>{email}</strong>.</p>
        <p style="font-size:13px;color:#999;">Reference: {appt_hash}</p>
        <a href="/" class="btn">Return Home</a>
    </div>
</body></html>'''


# ──────────────────── Notification emails (rendered as HTML preview) ────────────────────

def build_notification_email(apt, customer, service, provider):
    company_name = get_setting('company_name')
    cust_name = f"{customer['first_name']} {customer['last_name']}" if customer else ''
    cust_email = customer['email'] if customer else ''
    cust_phone = (customer['phone_number'] or '') if customer else ''
    cust_addr = (customer['address'] or '') if customer else ''
    svc_name = service['name'] if service else ''
    prov_name = f"{provider['first_name']} {provider['last_name']}" if provider else ''
    appt_notes = apt['notes'] or ''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head><title>Appointment Confirmation | {company_name}</title></head>
<body style="font: 13px arial, helvetica, tahoma;">
<div style="width:650px; border:1px solid #eee;">
    <div style="background-color:#2c8c6c; height:45px; padding:10px 15px;">
        <strong style="color:white; font-size:20px; margin-top:10px; display:inline-block">
            {company_name}
        </strong>
    </div>
    <div style="padding:10px 15px;">
        <h2>Appointment Confirmation</h2>
        <p>Your appointment has been confirmed.</p>

        <h2>Appointment Details</h2>
        <table>
            <tr><td style="padding:3px;font-weight:bold;">Service</td>
                <td style="padding:3px;">{svc_name}</td></tr>
            <tr><td style="padding:3px;font-weight:bold;">Provider</td>
                <td style="padding:3px;">{prov_name}</td></tr>
            <tr><td style="padding:3px;font-weight:bold;">Start</td>
                <td style="padding:3px;">{apt['start_datetime']}</td></tr>
            <tr><td style="padding:3px;font-weight:bold;">End</td>
                <td style="padding:3px;">{apt['end_datetime']}</td></tr>
            <tr><td style="padding:3px;font-weight:bold;">Notes</td>
                <td style="padding:3px;">{appt_notes}</td></tr>
        </table>

        <h2>Customer Details</h2>
        <table>
            <tr><td style="padding:3px;font-weight:bold;">Name</td>
                <td style="padding:3px;">{cust_name}</td></tr>
            <tr><td style="padding:3px;font-weight:bold;">Email</td>
                <td style="padding:3px;">{cust_email}</td></tr>
            <tr><td style="padding:3px;font-weight:bold;">Phone</td>
                <td style="padding:3px;">{cust_phone}</td></tr>
            <tr><td style="padding:3px;font-weight:bold;">Address</td>
                <td style="padding:3px;">{cust_addr}</td></tr>
        </table>
    </div>
    <div style="padding:10px; text-align:center; margin-top:10px; border-top:1px solid #EEE; background:#FAFAFA;">
        Powered by <a href="#" style="text-decoration:none;">{company_name}</a>
    </div>
</div>
</body></html>'''
    return html


@app.route('/admin/notifications/preview/<int:appointment_id>')
@login_required
def notification_preview(appointment_id):
    conn = get_db()
    apt = conn.execute("SELECT * FROM appointments WHERE id=?", (appointment_id,)).fetchone()
    if not apt:
        conn.close()
        return 'Appointment not found', 404

    customer = conn.execute("SELECT * FROM customers WHERE id=?", (apt['id_customers'],)).fetchone()
    service = conn.execute("SELECT * FROM services WHERE id=?", (apt['id_services'],)).fetchone()
    provider = conn.execute("SELECT * FROM providers WHERE id=?", (apt['id_providers'],)).fetchone()
    conn.close()

    email_html = build_notification_email(apt, customer, service, provider)
    return render_template_string(email_html)


# ──────────────────── Admin authentication ────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    company_name = get_setting('company_name')

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=? AND is_active=1",
                            (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['user_display_name'] = f"{user['first_name']} {user['last_name']}"
            return redirect('/admin/calendar')
        error_msg = '<div class="alert-error">Invalid credentials.</div>'
    else:
        error_msg = ''

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Login - {company_name}</title>
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; }}
    .login-box {{ max-width: 380px; margin: 80px auto; background: #fff; padding: 32px; border-radius: 6px; box-shadow: 0 2px 10px rgba(0,0,0,.08); }}
    .login-box h2 {{ color: #2c8c6c; margin: 0 0 20px; }}
    .field {{ margin-bottom: 14px; }}
    .field label {{ display: block; font-weight: 600; margin-bottom: 4px; font-size: 14px; }}
    .field input {{ width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }}
    .btn {{ width: 100%; background: #2c8c6c; color: #fff; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 15px; }}
    .btn:hover {{ background: #247d5f; }}
    .alert-error {{ background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px; margin-bottom: 14px; font-size: 14px; }}
</style></head>
<body>
    <div class="login-box">
        <h2>{company_name} - Staff Login</h2>
        {error_msg}
        <form method="POST">
            <div class="field"><label>Username</label><input type="text" name="username" required></div>
            <div class="field"><label>Password</label><input type="password" name="password" required></div>
            <button type="submit" class="btn">Sign In</button>
        </form>
    </div>
</body></html>'''


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/')


# ──────────────────── Admin backend ────────────────────

ADMIN_HEADER = '''
<div class="admin-header">
    <h1>{company}</h1>
    <nav>
        <a href="/admin/calendar">Calendar</a>
        <a href="/admin/customers">Customers</a>
        <a href="/admin/services">Services</a>
        <a href="/admin/settings">Settings</a>
    </nav>
    <div class="user-bar">
        <span>Hello, {display_name}</span> |
        <a href="/admin/logout">Logout</a>
    </div>
</div>'''

ADMIN_STYLE = '''
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; }
    .admin-header { background: #2c8c6c; color: #fff; padding: 14px 24px; display: flex; align-items: center; }
    .admin-header h1 { font-size: 20px; margin-right: 30px; }
    .admin-header nav { flex: 1; }
    .admin-header nav a { color: #fff; text-decoration: none; margin-right: 18px; font-size: 14px; }
    .admin-header nav a:hover { text-decoration: underline; }
    .admin-header .user-bar { font-size: 13px; }
    .admin-header .user-bar a { color: #fff; }
    .container { max-width: 1300px; margin: 24px auto; padding: 0 20px; }
    .panel { background: #fff; padding: 24px; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }
    th { background: #f8f9fa; font-weight: 600; }
    tr:hover { background: #f8f9fa; }
    a { color: #2c8c6c; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 3px; font-size: 12px; }
    .badge-pending { background: #fff3cd; color: #856404; }
    .badge-confirmed { background: #d4edda; color: #155724; }
    .badge-cancelled { background: #f8d7da; color: #721c24; }
    .btn { display: inline-block; padding: 8px 18px; background: #2c8c6c; color: #fff; border-radius: 4px; text-decoration: none; font-size: 13px; }
    .btn:hover { background: #247d5f; text-decoration: none; }
'''


@app.route('/admin/calendar')
@login_required
def admin_calendar():
    company = get_setting('company_name')
    display_name = session.get('user_display_name', 'Admin')
    header = ADMIN_HEADER.format(company=company, display_name=display_name)

    conn = get_db()
    appointments = conn.execute('''
        SELECT a.*, c.first_name, c.last_name, c.email as customer_email, s.name as service_name
        FROM appointments a
        LEFT JOIN customers c ON a.id_customers = c.id
        LEFT JOIN services s ON a.id_services = s.id
        ORDER BY a.created_at DESC
    ''').fetchall()
    conn.close()

    rows = ''
    for a in appointments:
        badge_cls = f'badge-{a["status"]}'
        rows += f'''<tr>
            <td>{a['id']}</td>
            <td><a href="/admin/calendar/appointment/{a['id']}">{a['first_name']} {a['last_name']}</a></td>
            <td>{a['customer_email']}</td>
            <td>{a['service_name']}</td>
            <td>{a['start_datetime']}</td>
            <td><span class="badge {badge_cls}">{a['status']}</span></td>
        </tr>'''

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Calendar - {company}</title>
<style>{ADMIN_STYLE}</style></head>
<body>
    {header}
    <div class="container">
        <div class="panel">
            <h2 style="margin-bottom:16px;">Appointments</h2>
            <table>
                <thead><tr><th>#</th><th>Customer</th><th>Email</th><th>Service</th><th>Date/Time</th><th>Status</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
</body></html>'''


DETAIL_STYLE = '''
    .detail-section { margin-bottom: 28px; }
    .detail-section h3 { color: #333; border-bottom: 2px solid #2c8c6c; padding-bottom: 8px; margin-bottom: 12px; }
    .detail-row { display: flex; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
    .detail-label { flex: 0 0 180px; font-weight: 600; color: #666; font-size: 14px; }
    .detail-val { flex: 1; font-size: 14px; }
    .actions { margin-top: 20px; }
    .actions a { margin-right: 10px; }
'''


def build_appointment_view(apt_id, company, display_name, customer, service, provider, apt):
    cust_name = f"{customer['first_name']} {customer['last_name']}" if customer else ''
    cust_email = customer['email'] if customer else ''
    cust_phone = (customer['phone_number'] or '') if customer else ''
    cust_addr = (customer['address'] or '') if customer else ''
    svc_name = service['name'] if service else ''
    prov_name = f"{provider['first_name']} {provider['last_name']}" if provider else ''
    appt_notes = apt['notes'] or ''

    page = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Appointment #{apt_id} - {company}</title>
<style>{ADMIN_STYLE}{DETAIL_STYLE}</style></head>
<body>
    {ADMIN_HEADER.format(company=company, display_name=display_name)}
    <div class="container">
        <div class="panel">
            <h2 style="margin-bottom:20px;">Appointment Details</h2>

            <div class="detail-section">
                <h3>Customer Information</h3>
                <div class="detail-row"><div class="detail-label">Name</div><div class="detail-val">{cust_name}</div></div>
                <div class="detail-row"><div class="detail-label">Email</div><div class="detail-val">{cust_email}</div></div>
                <div class="detail-row"><div class="detail-label">Phone</div><div class="detail-val">{cust_phone}</div></div>
                <div class="detail-row"><div class="detail-label">Address</div><div class="detail-val">{cust_addr}</div></div>
            </div>

            <div class="detail-section">
                <h3>Appointment Information</h3>
                <div class="detail-row"><div class="detail-label">Service</div><div class="detail-val">{svc_name}</div></div>
                <div class="detail-row"><div class="detail-label">Provider</div><div class="detail-val">{prov_name}</div></div>
                <div class="detail-row"><div class="detail-label">Start</div><div class="detail-val">{apt['start_datetime']}</div></div>
                <div class="detail-row"><div class="detail-label">End</div><div class="detail-val">{apt['end_datetime']}</div></div>
                <div class="detail-row"><div class="detail-label">Status</div><div class="detail-val"><span class="badge badge-{apt['status']}">{apt['status']}</span></div></div>
                <div class="detail-row"><div class="detail-label">Created</div><div class="detail-val">{apt['created_at']}</div></div>
            </div>

            <div class="detail-section">
                <h3>Notes</h3>
                <div class="detail-val" style="padding:8px 0;">{appt_notes}</div>
            </div>

            <div class="actions">
                <a href="/admin/calendar" class="btn">Back to Calendar</a>
                <a href="/admin/notifications/preview/{apt_id}" class="btn" style="background:#5a6268;">Preview Notification</a>
            </div>
        </div>
    </div>
</body></html>'''
    return page


@app.route('/admin/calendar/appointment/<int:appointment_id>')
@login_required
def view_appointment_detail(appointment_id):
    conn = get_db()
    apt = conn.execute("SELECT * FROM appointments WHERE id=?", (appointment_id,)).fetchone()
    if not apt:
        conn.close()
        return 'Not found', 404

    customer = conn.execute("SELECT * FROM customers WHERE id=?", (apt['id_customers'],)).fetchone()
    service = conn.execute("SELECT * FROM services WHERE id=?", (apt['id_services'],)).fetchone()
    provider = conn.execute("SELECT * FROM providers WHERE id=?", (apt['id_providers'],)).fetchone()
    conn.close()

    company = get_setting('company_name')
    display_name = session.get('user_display_name', 'Admin')

    page = build_appointment_view(appointment_id, company, display_name, customer, service, provider, apt)
    return render_template_string(page)


@app.route('/admin/customers')
@login_required
def admin_customers():
    company = get_setting('company_name')
    display_name = session.get('user_display_name', 'Admin')
    header = ADMIN_HEADER.format(company=company, display_name=display_name)

    conn = get_db()
    customers = conn.execute("SELECT * FROM customers ORDER BY created_at DESC").fetchall()
    conn.close()

    rows = ''
    for c in customers:
        rows += f'''<tr>
            <td>{c['id']}</td>
            <td>{c['first_name']} {c['last_name']}</td>
            <td>{c['email']}</td>
            <td>{c['phone_number'] or '-'}</td>
            <td>{c['city'] or '-'}</td>
            <td>{c['created_at']}</td>
        </tr>'''

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Customers - {company}</title>
<style>{ADMIN_STYLE}</style></head>
<body>
    {header}
    <div class="container">
        <div class="panel">
            <h2 style="margin-bottom:16px;">Customers</h2>
            <table>
                <thead><tr><th>#</th><th>Name</th><th>Email</th><th>Phone</th><th>City</th><th>Registered</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
</body></html>'''


@app.route('/admin/services')
@login_required
def admin_services():
    company = get_setting('company_name')
    display_name = session.get('user_display_name', 'Admin')
    header = ADMIN_HEADER.format(company=company, display_name=display_name)

    conn = get_db()
    services = conn.execute("SELECT * FROM services").fetchall()
    conn.close()

    rows = ''
    for s in services:
        active = 'Yes' if s['is_active'] else 'No'
        rows += f'''<tr>
            <td>{s['id']}</td>
            <td>{s['name']}</td>
            <td>{s['duration']} min</td>
            <td>{s['description'] or '-'}</td>
            <td>{active}</td>
        </tr>'''

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Services - {company}</title>
<style>{ADMIN_STYLE}</style></head>
<body>
    {header}
    <div class="container">
        <div class="panel">
            <h2 style="margin-bottom:16px;">Services</h2>
            <table>
                <thead><tr><th>#</th><th>Name</th><th>Duration</th><th>Description</th><th>Active</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
</body></html>'''


@app.route('/admin/settings')
@login_required
def admin_settings():
    company = get_setting('company_name')
    display_name = session.get('user_display_name', 'Admin')
    header = ADMIN_HEADER.format(company=company, display_name=display_name)

    conn = get_db()
    settings = conn.execute("SELECT * FROM settings ORDER BY name").fetchall()
    conn.close()

    rows = ''
    for s in settings:
        rows += f'''<tr><td>{s['name']}</td><td>{s['value']}</td></tr>'''

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Settings - {company}</title>
<style>{ADMIN_STYLE}</style></head>
<body>
    {header}
    <div class="container">
        <div class="panel">
            <h2 style="margin-bottom:16px;">System Settings</h2>
            <table>
                <thead><tr><th>Setting</th><th>Value</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
</body></html>'''


# ──────────────────── Health ────────────────────

@app.route('/health')
def health_check():
    return 'OK', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
