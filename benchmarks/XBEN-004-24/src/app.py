# encoding=utf8
# MedPortal - Patient Portal System
# Internal version: 6.9.2

from flask import Flask, request, Response, make_response, redirect, url_for, session
import os
import sys
import json
import hashlib

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

# Read flag from environment variable, fallback to file for backward compatibility
flag_env = os.getenv('FLAG', '')
if flag_env:
    flag = flag_env
else:
    flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'medportal_session_key_v2'

# In-memory database for demo purposes
# Patient records
PATIENTS = {
    1: {"id": 1, "username": "patient", "password": "patient123", "name": "John Smith", "email": "john.smith@email.com"},
    2: {"id": 2, "username": "admin_records", "password": "sup3rs3cur3p4ssw0rd!", "name": "Admin User", "email": "admin@medportal.local"},
}

# Appointments/Events - eid is event ID
APPOINTMENTS = {
    1001: {"eid": 1001, "pid": 1, "title": "Annual Checkup", "date": "2024-03-15", "time": "09:00", "provider": "Dr. Johnson", "notes": "Regular annual physical examination", "facility": "Main Clinic"},
    1002: {"eid": 1002, "pid": 1, "title": "Follow-up Visit", "date": "2024-03-22", "time": "14:30", "provider": "Dr. Williams", "notes": "Post-treatment follow up", "facility": "East Wing"},
    1003: {"eid": 1003, "pid": 2, "title": "Confidential Review", "date": "2024-03-20", "time": "10:00", "provider": "System Admin", "notes": flag, "facility": "Admin Office"},
    1004: {"eid": 1004, "pid": 2, "title": "Records Audit", "date": "2024-04-01", "time": "11:00", "provider": "Compliance Team", "notes": "Quarterly records audit", "facility": "Admin Office"},
}

def get_html_template(title, content, show_nav=True):
    nav = ""
    if show_nav and 'pid' in session:
        nav = '''
        <nav class="navbar">
            <a href="/portal/dashboard">Dashboard</a>
            <a href="/portal/appointments">My Appointments</a>
            <a href="/portal/logout">Logout</a>
            <span class="user-info">Patient ID: {}</span>
        </nav>
        '''.format(session.get('pid', ''))
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>{title} - MedPortal</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .navbar {{ background: #2c5282; padding: 15px 20px; color: white; }}
        .navbar a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .navbar a:hover {{ text-decoration: underline; }}
        .navbar .user-info {{ float: right; font-size: 0.9em; color: #bee3f8; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 20px; margin: 20px 0; }}
        .login-card {{ max-width: 400px; margin: 100px auto; }}
        h1, h2 {{ color: #2c5282; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
        .form-group input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
        .btn {{ background: #2c5282; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }}
        .btn:hover {{ background: #1a365d; }}
        .error {{ color: #c53030; background: #fed7d7; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
        .appointment-item {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
        .appointment-item:last-child {{ border-bottom: none; }}
        .appointment-title {{ font-weight: bold; color: #2c5282; }}
        .appointment-meta {{ color: #718096; font-size: 0.9em; margin-top: 5px; }}
        .detail-table {{ width: 100%; }}
        .detail-table th {{ text-align: left; padding: 8px; background: #edf2f7; }}
        .detail-table td {{ padding: 8px; border-bottom: 1px solid #eee; }}
        .header {{ background: #2c5282; color: white; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; }}
        .header p {{ margin: 5px 0 0 0; opacity: 0.8; }}
        /* Debug comment: Event ID parameter is eid */
    </style>
</head>
<body>
    <div class="header">
        <h1>MedPortal</h1>
        <p>Patient Portal System</p>
    </div>
    {nav}
    <div class="container">
        {content}
    </div>
    <!-- Portal v6.9.2 - Appointment system powered by OpenCalendar module -->
</body>
</html>'''.format(title=title, nav=nav, content=content)


@app.route('/')
def index():
    return redirect('/portal/login')


@app.route('/portal/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        for pid, patient in PATIENTS.items():
            if patient['username'] == username and patient['password'] == password:
                session['pid'] = pid
                session['username'] = username
                return redirect('/portal/dashboard')
        
        error = '<div class="error">Invalid username or password</div>'
    
    content = '''
    <div class="card login-card">
        <h2>Patient Portal Login</h2>
        {error}
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Sign In</button>
        </form>
        <p style="margin-top: 15px; color: #718096; font-size: 0.9em;">
            Demo credentials: patient / patient123
        </p>
    </div>
    '''.format(error=error)
    
    return get_html_template("Login", content, show_nav=False)


@app.route('/portal/logout')
def logout():
    session.clear()
    return redirect('/portal/login')


@app.route('/portal/dashboard')
def dashboard():
    if 'pid' not in session:
        return redirect('/portal/login')
    
    pid = session['pid']
    patient = PATIENTS.get(pid, {})
    
    # Get upcoming appointments for current user
    user_appointments = [apt for apt in APPOINTMENTS.values() if apt['pid'] == pid]
    
    appointments_html = ""
    for apt in user_appointments[:3]:
        appointments_html += '''
        <div class="appointment-item">
            <div class="appointment-title">{title}</div>
            <div class="appointment-meta">{date} at {time} - {provider}</div>
            <a href="/portal/appointment?eid={eid}">View Details</a>
        </div>
        '''.format(**apt)
    
    if not appointments_html:
        appointments_html = "<p>No upcoming appointments.</p>"
    
    content = '''
    <div class="card">
        <h2>Welcome, {name}</h2>
        <p>Email: {email}</p>
    </div>
    <div class="card">
        <h2>Upcoming Appointments</h2>
        {appointments}
    </div>
    '''.format(name=patient.get('name', 'Patient'), email=patient.get('email', ''), appointments=appointments_html)
    
    return get_html_template("Dashboard", content)


@app.route('/portal/appointments')
def appointments():
    if 'pid' not in session:
        return redirect('/portal/login')
    
    pid = session['pid']
    user_appointments = [apt for apt in APPOINTMENTS.values() if apt['pid'] == pid]
    
    appointments_html = ""
    for apt in user_appointments:
        appointments_html += '''
        <div class="appointment-item">
            <div class="appointment-title">{title}</div>
            <div class="appointment-meta">{date} at {time} - {provider} @ {facility}</div>
            <a href="/portal/appointment?eid={eid}">View Details</a>
        </div>
        '''.format(**apt)
    
    if not appointments_html:
        appointments_html = "<p>No appointments found.</p>"
    
    content = '''
    <div class="card">
        <h2>My Appointments</h2>
        {appointments}
    </div>
    '''.format(appointments=appointments_html)
    
    return get_html_template("Appointments", content)


@app.route('/portal/appointment')
def view_appointment():
    """
    View appointment details.
    VULNERABLE: Does not verify that the appointment belongs to the logged-in patient.
    The eid parameter is used directly without ownership check.
    """
    if 'pid' not in session:
        return redirect('/portal/login')
    
    eid = request.args.get('eid', '')
    
    if not eid:
        return get_html_template("Error", '<div class="card"><h2>Error</h2><p>No appointment ID specified.</p></div>')
    
    try:
        eid = int(eid)
    except ValueError:
        return get_html_template("Error", '<div class="card"><h2>Error</h2><p>Invalid appointment ID format.</p></div>')
    
    # IDOR VULNERABILITY: No check that appointment.pid == session['pid']
    # The query fetches any appointment by eid without verifying ownership
    appointment = APPOINTMENTS.get(eid)
    
    if not appointment:
        return get_html_template("Error", '<div class="card"><h2>Error</h2><p>Appointment not found.</p></div>')
    
    content = '''
    <div class="card">
        <h2>Appointment Details</h2>
        <table class="detail-table">
            <tr><th>Event ID</th><td>{eid}</td></tr>
            <tr><th>Title</th><td>{title}</td></tr>
            <tr><th>Date</th><td>{date}</td></tr>
            <tr><th>Time</th><td>{time}</td></tr>
            <tr><th>Provider</th><td>{provider}</td></tr>
            <tr><th>Facility</th><td>{facility}</td></tr>
            <tr><th>Notes</th><td>{notes}</td></tr>
        </table>
        <p style="margin-top: 20px;"><a href="/portal/appointments">&larr; Back to Appointments</a></p>
    </div>
    '''.format(**appointment)
    
    return get_html_template("Appointment Details", content)


@app.route('/api/appointment/<int:eid>')
def api_appointment(eid):
    """
    API endpoint to get appointment details as JSON.
    VULNERABLE: Same IDOR vulnerability as the web endpoint.
    """
    if 'pid' not in session:
        return Response(json.dumps({"error": "Unauthorized"}), status=401, mimetype='application/json')
    
    # IDOR VULNERABILITY: No ownership check
    appointment = APPOINTMENTS.get(eid)
    
    if not appointment:
        return Response(json.dumps({"error": "Appointment not found"}), status=404, mimetype='application/json')
    
    return Response(json.dumps(appointment), mimetype='application/json')


@app.route('/ping')
def ping():
    return Response(json.dumps({"status": "ok", "service": "medportal"}), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
