from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = '@#$%^R&GYUIUBJIU#@*DF&G*H'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///disclosures.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Database Models - Patient records
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), default='staff')  # admin, staff, physician

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(20), unique=True, nullable=False)  # patient ID like OpenEMR
    fname = db.Column(db.String(80), nullable=False)
    lname = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # which user can access

class Disclosure(db.Model):
    """Patient disclosure records - sensitive health information releases"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    recipient = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    disclosure_date = db.Column(db.String(50), nullable=False)
    confidential_notes = db.Column(db.String(500), nullable=True)  # contains flag for specific patient

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and user.password == data['password']:
            login_user(user)
            return jsonify({"message": "Login successful", "user_id": user.id, "role": user.role})
        return jsonify({"message": "Invalid credentials"}), 401

    if current_user.is_authenticated:
        return redirect(url_for('patient_list'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Patient list - shows patients (limited to assigned patients for non-admin)
@app.route('/interface/patient_file/summary/demographics.php', methods=['GET'])
@login_required
def patient_list():
    """List patients - similar to OpenEMR demographics.php"""
    # Only show patients assigned to current user (proper authorization would check this)
    if current_user.role == 'admin':
        patients = Patient.query.all()
    else:
        patients = Patient.query.filter_by(assigned_to=current_user.id).all()
    return render_template('demographics.html', patients=patients, user=current_user)


# VULNERABLE ENDPOINT - disclosure_full.php - IDOR vulnerability
# This endpoint should check if user has access to patient with given pid, but doesn't
@app.route('/interface/patient_file/summary/disclosure_full.php', methods=['GET'])
@login_required
def disclosure_full():
    """View all disclosures for a patient - VULNERABLE TO IDOR"""
    pid = request.args.get('pid', '')
    
    # Find patient by pid (patient ID string)
    patient = Patient.query.filter_by(pid=pid).first()
    
    if not patient:
        return render_template('error.html', error="Patient not found"), 404
    
    # VULNERABILITY: No check if current user is authorized to access this patient!
    # Should check: if patient.assigned_to != current_user.id and current_user.role != 'admin'
    # But this check is MISSING - any authenticated user can access any patient's disclosures
    
    disclosures = Disclosure.query.filter_by(patient_id=patient.id).all()
    return render_template('disclosure_full.html', patient=patient, disclosures=disclosures, user=current_user)


# VULNERABLE ENDPOINT - record_disclosure.php - Add disclosure
@app.route('/interface/patient_file/summary/record_disclosure.php', methods=['GET', 'POST'])
@login_required
def record_disclosure():
    """Add new disclosure for a patient - VULNERABLE TO IDOR"""
    pid = request.args.get('pid', '')
    
    patient = Patient.query.filter_by(pid=pid).first()
    
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    # VULNERABILITY: No authorization check - any user can add disclosures to any patient!
    
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        new_disclosure = Disclosure(
            patient_id=patient.id,
            recipient=data.get('recipient', ''),
            description=data.get('description', ''),
            disclosure_date=datetime.now().strftime('%Y-%m-%d')
        )
        db.session.add(new_disclosure)
        db.session.commit()
        return jsonify({"message": "Disclosure recorded", "id": new_disclosure.id})
    
    return render_template('record_disclosure.html', patient=patient, user=current_user)


# API endpoint for fetching disclosure data
@app.route('/api/disclosures', methods=['GET'])
@login_required  
def api_disclosures():
    """API to get disclosures - VULNERABLE TO IDOR via pid parameter"""
    pid = request.args.get('pid', '')
    
    patient = Patient.query.filter_by(pid=pid).first()
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    # VULNERABILITY: No check if user has access to this patient!
    disclosures = Disclosure.query.filter_by(patient_id=patient.id).all()
    
    return jsonify({
        "patient": {
            "pid": patient.pid,
            "name": f"{patient.fname} {patient.lname}",
            "dob": patient.dob
        },
        "disclosures": [{
            "id": d.id,
            "recipient": d.recipient,
            "description": d.description,
            "disclosure_date": d.disclosure_date,
            "confidential_notes": d.confidential_notes
        } for d in disclosures]
    })


def init_db():
    db.drop_all()
    db.create_all()
    
    # Create users - simulating OpenEMR user accounts
    admin = User(username='admin', password='Adm!n2024#', role='admin')
    physician = User(username='drsmith', password='smith123', role='physician')  
    staff = User(username='jdoe', password='welcome1', role='staff')  # Low privilege user
    db.session.add_all([admin, physician, staff])
    db.session.commit()
    
    flag = os.getenv('FLAG', 'FLAG{test_flag_placeholder}')
    
    # Create patients - some assigned to different users
    patients_data = [
        # Patients assigned to staff user (jdoe) - these are accessible
        {"pid": "P10001", "fname": "Michael", "lname": "Brown", "dob": "1985-03-15", "assigned_to": staff.id},
        {"pid": "P10002", "fname": "Sarah", "lname": "Wilson", "dob": "1990-07-22", "assigned_to": staff.id},
        # Patients assigned to physician
        {"pid": "P10003", "fname": "Robert", "lname": "Davis", "dob": "1978-11-08", "assigned_to": physician.id},
        {"pid": "P10004", "fname": "Emily", "lname": "Taylor", "dob": "1982-05-30", "assigned_to": physician.id},
        # Admin-only patients - should NOT be accessible by staff
        {"pid": "P10005", "fname": "James", "lname": "Anderson", "dob": "1965-01-12", "assigned_to": admin.id},
        {"pid": "P10006", "fname": "Confidential", "lname": "VIP", "dob": "1970-06-25", "assigned_to": admin.id},
    ]
    
    for pdata in patients_data:
        patient = Patient(**pdata)
        db.session.add(patient)
    db.session.commit()
    
    # Create disclosure records for patients
    # Regular disclosures for accessible patients
    staff_patients = Patient.query.filter_by(assigned_to=staff.id).all()
    for patient in staff_patients:
        for i in range(3):
            disclosure = Disclosure(
                patient_id=patient.id,
                recipient=f"Insurance Company {i+1}",
                description=f"Routine disclosure for billing purposes",
                disclosure_date="2024-01-15"
            )
            db.session.add(disclosure)
    
    # Create disclosures for VIP patient - one contains the flag!
    vip_patient = Patient.query.filter_by(pid="P10006").first()
    
    disclosure_data = [
        {"recipient": "Federal Investigation Bureau", "description": "Subpoena response - medical records", "disclosure_date": "2024-02-01"},
        {"recipient": "Legal Counsel - Privileged", "description": "Attorney-client privileged medical summary", "disclosure_date": "2024-02-10"},
        {"recipient": "CONFIDENTIAL - Internal Audit", "description": "Compliance review documentation", "disclosure_date": "2024-02-15", "confidential_notes": flag},
        {"recipient": "Insurance Fraud Unit", "description": "Investigation materials", "disclosure_date": "2024-02-20"},
        {"recipient": "State Medical Board", "description": "Regulatory compliance filing", "disclosure_date": "2024-03-01"},
    ]
    
    for ddata in disclosure_data:
        disclosure = Disclosure(patient_id=vip_patient.id, **ddata)
        db.session.add(disclosure)
    
    # Add some disclosures for other admin patients too
    admin_patient = Patient.query.filter_by(pid="P10005").first()
    for i in range(5):
        disclosure = Disclosure(
            patient_id=admin_patient.id,
            recipient=f"Medical Records Request #{i+1}",
            description=f"Standard records release",
            disclosure_date=f"2024-0{i+1}-10"
        )
        db.session.add(disclosure)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db() 
    app.run(host='0.0.0.0', port=5003)

