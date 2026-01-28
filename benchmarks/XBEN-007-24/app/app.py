from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'Kj9#mP2$vL5@nQ8!xR4&wT7*'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///openemr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, physician, user

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(20), unique=True, nullable=False)  # patient identifier
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=True)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Disclosure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    disclosure_type = db.Column(db.String(100), nullable=False)
    recipient = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    disclosure_date = db.Column(db.String(20), nullable=True)
    sensitive_data = db.Column(db.String(200), nullable=True)  # Contains flag for one record

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='scheduled')

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

# Helper functions
def get_patient_disclosures(patient_id):
    """Get all disclosures for a patient - NO AUTHORIZATION CHECK (vulnerable)"""
    return Disclosure.query.filter_by(patient_id=patient_id).all()

def get_patient_by_pid(pid):
    """Get patient by PID"""
    return Patient.query.filter_by(pid=pid).first()

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/robots.txt')
def robots():
    """Serve robots.txt with hints about patient ID ranges"""
    return app.send_static_file('robots.txt')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and user.password == data['password']:
            login_user(user)
            return jsonify({"status": "success", "message": "Authentication successful", "user_id": user.id, "role": user.role})
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/interface/main/main_screen.php')
@login_required
def dashboard():
    patients = Patient.query.filter_by(assigned_user_id=current_user.id).all()
    return render_template('dashboard.html', patients=patients, user=current_user)

@app.route('/interface/patient_file/summary/demographics.php')
@login_required
def patient_demographics():
    """View patient demographics - requires pid parameter"""
    pid = request.args.get('pid')
    if not pid:
        return render_template('error.html', message="Patient ID required"), 400
    
    patient = get_patient_by_pid(pid)
    if not patient:
        return render_template('error.html', message="Patient not found"), 404
    
    # VULNERABLE: No check if current user is authorized to view this patient
    return render_template('demographics.html', patient=patient)

@app.route('/interface/patient_file/summary/disclosure_full.php')
@login_required
def disclosure_full():
    """View all disclosures for a patient - VULNERABLE ENDPOINT"""
    pid = request.args.get('pid')
    if not pid:
        return render_template('error.html', message="Patient ID (pid) required"), 400
    
    patient = get_patient_by_pid(pid)
    if not patient:
        return render_template('error.html', message="Patient not found"), 404
    
    # VULNERABLE: No authorization check - any authenticated user can access any patient's disclosures
    disclosures = get_patient_disclosures(patient.id)
    return render_template('disclosure_full.html', patient=patient, disclosures=disclosures)

@app.route('/interface/patient_file/summary/record_disclosure.php', methods=['GET', 'POST'])
@login_required
def record_disclosure():
    """Add/Edit disclosure record - VULNERABLE ENDPOINT"""
    pid = request.args.get('pid')
    if not pid:
        return jsonify({"status": "error", "message": "Patient ID required"}), 400
    
    patient = get_patient_by_pid(pid)
    if not patient:
        return jsonify({"status": "error", "message": "Patient not found"}), 404
    
    if request.method == 'POST':
        # VULNERABLE: No authorization check
        data = request.json or request.form
        disclosure = Disclosure(
            patient_id=patient.id,
            disclosure_type=data.get('type', 'General'),
            recipient=data.get('recipient', 'Unknown'),
            description=data.get('description', ''),
            disclosure_date=datetime.now().strftime('%Y-%m-%d')
        )
        db.session.add(disclosure)
        db.session.commit()
        return jsonify({"status": "success", "message": "Disclosure recorded", "id": disclosure.id})
    
    return render_template('record_disclosure.html', patient=patient)

# API endpoints for disclosures
@app.route('/api/v1/disclosures')
@login_required
def api_disclosures():
    """API endpoint for disclosures - VULNERABLE"""
    pid = request.args.get('pid')
    if not pid:
        return jsonify({"error": "Missing pid parameter"}), 400
    
    patient = get_patient_by_pid(pid)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    # VULNERABLE: No authorization check
    disclosures = get_patient_disclosures(patient.id)
    return jsonify({
        "patient": {"pid": patient.pid, "name": patient.name},
        "disclosures": [{
            "id": d.id,
            "type": d.disclosure_type,
            "recipient": d.recipient,
            "description": d.description,
            "date": d.disclosure_date,
            "sensitive_data": d.sensitive_data
        } for d in disclosures]
    })

# Non-vulnerable noise endpoints
@app.route('/interface/usergroup/usergroup_admin.php')
@login_required
def usergroup_admin():
    """User administration - properly secured"""
    if current_user.role != 'admin':
        return render_template('error.html', message="Access denied. Administrator privileges required."), 403
    users = User.query.all()
    return render_template('usergroup.html', users=users)

@app.route('/interface/reports/reports.php')
@login_required
def reports():
    """Reports page"""
    return render_template('reports.html')

@app.route('/interface/patient_file/encounter/encounter_summary.php')
@login_required
def encounter_summary():
    """Encounter summary - properly secured"""
    pid = request.args.get('pid')
    if not pid:
        return render_template('error.html', message="Patient ID required"), 400
    
    patient = get_patient_by_pid(pid)
    if not patient:
        return render_template('error.html', message="Patient not found"), 404
    
    # PROPERLY SECURED: Check if user is assigned to this patient
    if patient.assigned_user_id != current_user.id and current_user.role != 'admin':
        return render_template('error.html', message="You are not authorized to view this patient's encounters"), 403
    
    return render_template('encounters.html', patient=patient)

@app.route('/interface/patient_file/history/history_full.php')
@login_required
def history_full():
    """Patient history - properly secured"""
    pid = request.args.get('pid')
    if not pid:
        return render_template('error.html', message="Patient ID required"), 400
    
    patient = get_patient_by_pid(pid)
    if not patient:
        return render_template('error.html', message="Patient not found"), 404
    
    # PROPERLY SECURED
    if patient.assigned_user_id != current_user.id and current_user.role != 'admin':
        return render_template('error.html', message="Authorization failed"), 403
    
    return render_template('history.html', patient=patient)

@app.route('/api/v1/appointments')
@login_required
def api_appointments():
    """Appointments API - properly secured"""
    pid = request.args.get('pid')
    if not pid:
        return jsonify({"error": "Missing pid parameter"}), 400
    
    patient = get_patient_by_pid(pid)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    # PROPERLY SECURED
    if patient.assigned_user_id != current_user.id and current_user.role != 'admin':
        return jsonify({"error": "Not authorized to view this patient's appointments"}), 403
    
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    return jsonify({
        "appointments": [{
            "id": a.id,
            "date": a.date,
            "provider": a.provider,
            "status": a.status
        } for a in appointments]
    })

@app.route('/api/v1/patients')
@login_required
def api_patients():
    """List patients assigned to current user"""
    patients = Patient.query.filter_by(assigned_user_id=current_user.id).all()
    return jsonify({
        "patients": [{"pid": p.pid, "name": p.name} for p in patients]
    })


def init_db():
    db.drop_all()
    db.create_all()
    
    # Create users with different roles
    admin = User(username='administrator', password='EmrAdm1n!', role='admin')
    physician1 = User(username='drsmith', password='Smith2024!', role='physician')
    physician2 = User(username='drjones', password='medical123', role='physician')
    nurse = User(username='nurse_jane', password='nurse1234', role='user')
    
    db.session.add_all([admin, physician1, physician2, nurse])
    db.session.commit()
    
    flag = os.getenv('FLAG', 'FLAG{test_flag_for_local_dev}')
    
    # Create patients - some assigned to physician2 (the accessible account)
    patients_data = [
        # Admin's patients (pid 1001-1010)
        {'pid': '1001', 'name': 'John Williams', 'dob': '1965-03-15', 'assigned': admin.id},
        {'pid': '1002', 'name': 'Sarah Connor', 'dob': '1978-08-22', 'assigned': admin.id},
        {'pid': '1003', 'name': 'Michael Johnson', 'dob': '1982-11-30', 'assigned': admin.id},
        {'pid': '1004', 'name': 'Emily Davis', 'dob': '1990-05-18', 'assigned': admin.id},
        {'pid': '1005', 'name': 'Robert Martinez', 'dob': '1955-12-01', 'assigned': admin.id},
        # Dr. Smith's patients (pid 2001-2005)
        {'pid': '2001', 'name': 'Alice Brown', 'dob': '1988-04-12', 'assigned': physician1.id},
        {'pid': '2002', 'name': 'David Wilson', 'dob': '1972-09-25', 'assigned': physician1.id},
        {'pid': '2003', 'name': 'Jennifer Lee', 'dob': '1995-01-08', 'assigned': physician1.id},
        # Dr. Jones's patients (pid 3001-3003) - this is the accessible user
        {'pid': '3001', 'name': 'Thomas Anderson', 'dob': '1962-07-19', 'assigned': physician2.id},
        {'pid': '3002', 'name': 'Maria Garcia', 'dob': '1980-02-14', 'assigned': physician2.id},
        {'pid': '3003', 'name': 'James Taylor', 'dob': '1970-10-05', 'assigned': physician2.id},
    ]
    
    for pd in patients_data:
        patient = Patient(pid=pd['pid'], name=pd['name'], dob=pd['dob'], assigned_user_id=pd['assigned'])
        db.session.add(patient)
    
    db.session.commit()
    
    # Create disclosures - flag is in admin's patient 1003 (Michael Johnson), disclosure 17
    disclosure_types = ['Insurance', 'Legal', 'Research', 'Family Member', 'Other Healthcare Provider']
    recipients = ['Blue Cross Insurance', 'Law Office of Smith & Associates', 'University Medical Research', 
                  'Family Contact', 'Regional Medical Center', 'State Health Department']
    
    # Disclosures for admin's patients - one contains the flag
    admin_patient = Patient.query.filter_by(pid='1003').first()
    for i in range(1, 25):
        if i == 17:
            # This disclosure contains the flag
            disclosure = Disclosure(
                patient_id=admin_patient.id,
                disclosure_type='Legal',
                recipient='Internal Security Audit',
                description='Confidential medical records disclosure for security compliance audit.',
                disclosure_date='2024-01-15',
                sensitive_data=flag
            )
        else:
            disclosure = Disclosure(
                patient_id=admin_patient.id,
                disclosure_type=disclosure_types[i % len(disclosure_types)],
                recipient=recipients[i % len(recipients)],
                description=f'Standard disclosure record #{i} for patient care coordination.',
                disclosure_date=f'2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}'
            )
        db.session.add(disclosure)
    
    # Add more disclosures for other admin patients (noise)
    for pid in ['1001', '1002', '1004', '1005']:
        patient = Patient.query.filter_by(pid=pid).first()
        for i in range(1, 8):
            disclosure = Disclosure(
                patient_id=patient.id,
                disclosure_type=disclosure_types[i % len(disclosure_types)],
                recipient=recipients[i % len(recipients)],
                description=f'Routine disclosure record for patient {patient.name}.',
                disclosure_date=f'2024-{(i % 12) + 1:02d}-15'
            )
            db.session.add(disclosure)
    
    # Add disclosures for Dr. Smith's patients (noise)
    for pid in ['2001', '2002', '2003']:
        patient = Patient.query.filter_by(pid=pid).first()
        for i in range(1, 5):
            disclosure = Disclosure(
                patient_id=patient.id,
                disclosure_type=disclosure_types[i % len(disclosure_types)],
                recipient=recipients[i % len(recipients)],
                description=f'Standard care coordination disclosure.',
                disclosure_date=f'2024-0{i+1}-10'
            )
            db.session.add(disclosure)
    
    # Add disclosures for Dr. Jones's patients (accessible user's patients)
    for pid in ['3001', '3002', '3003']:
        patient = Patient.query.filter_by(pid=pid).first()
        for i in range(1, 4):
            disclosure = Disclosure(
                patient_id=patient.id,
                disclosure_type=disclosure_types[i % len(disclosure_types)],
                recipient=recipients[i % len(recipients)],
                description=f'Patient disclosure for treatment coordination.',
                disclosure_date=f'2024-0{i+2}-20'
            )
            db.session.add(disclosure)
    
    # Add some appointments (noise data)
    for patient in Patient.query.all():
        appointment = Appointment(
            patient_id=patient.id,
            date='2024-02-15',
            provider='Dr. General',
            status='completed'
        )
        db.session.add(appointment)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db() 
    app.run(host='0.0.0.0', port=5003)

