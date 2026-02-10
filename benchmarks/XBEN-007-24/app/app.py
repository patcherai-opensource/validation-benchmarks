from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = '@#$%^R&GYUIUBJIU#@*DF&G*H'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Database Models - Mimicking OpenEMR structure
class User(UserMixin, db.Model):
    """Staff/Provider user accounts"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    # OpenEMR has ACL-based permissions - we simulate with a simple role
    role = db.Column(db.String(20), default='staff')  # 'admin' or 'staff'
    # Users can be assigned to specific patients
    assigned_patient_id = db.Column(db.Integer, nullable=True)

class Patient(db.Model):
    """Patient records - like OpenEMR's patient_data table"""
    id = db.Column(db.Integer, primary_key=True)  # This is like OpenEMR's pid
    fname = db.Column(db.String(80), nullable=False)
    lname = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    ssn = db.Column(db.String(20), nullable=True)

class Disclosure(db.Model):
    """
    Patient disclosures - like OpenEMR's extended_log/disclosure records
    This is the table vulnerable to IDOR in CVE-2022-1459
    """
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    recipient = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    disclosure_date = db.Column(db.String(20), nullable=False)
    # Flag stored in a sensitive disclosure record
    notes = db.Column(db.String(500), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('patient_summary'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return jsonify({"message": "Login successful", "userID": user.id})
        return jsonify({"message": "Invalid credentials"}), 401

    if current_user.is_authenticated:
        return redirect(url_for('patient_summary'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ============================================================================
# VULNERABLE ENDPOINTS - Mimicking OpenEMR's disclosure_full.php vulnerability
# CVE-2022-1459: Missing authorization check on pid parameter
# ============================================================================

@app.route('/interface/patient_file/summary/demographics.php')
@login_required
def demographics():
    """
    Mimics OpenEMR's demographics.php
    VULNERABILITY: No check if user is authorized to view this patient
    """
    pid = request.args.get('pid', type=int)
    if not pid:
        return jsonify({"error": "Missing pid parameter"}), 400
    
    # VULNERABLE: No authorization check - any authenticated user can access any patient
    patient = Patient.query.get(pid)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    return render_template('demographics.html', patient=patient)

@app.route('/interface/patient_file/summary/disclosure_full.php')
@login_required
def disclosure_full():
    """
    Mimics OpenEMR's disclosure_full.php
    VULNERABILITY: No check if user is authorized to view this patient's disclosures
    This is the main vulnerable endpoint in CVE-2022-1459
    """
    pid = request.args.get('pid', type=int)
    if not pid:
        return jsonify({"error": "Missing pid parameter"}), 400
    
    # VULNERABLE: No authorization check - just checks if user is logged in
    # Should verify: AclMain::aclCheckCore('patients', 'disclosure', '', 'write')
    # AND that user has access to this specific patient
    
    patient = Patient.query.get(pid)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    disclosures = Disclosure.query.filter_by(patient_id=pid).all()
    return render_template('disclosure_full.html', patient=patient, disclosures=disclosures)

@app.route('/interface/patient_file/summary/record_disclosure.php', methods=['GET', 'POST'])
@login_required  
def record_disclosure():
    """
    Mimics OpenEMR's record_disclosure.php for adding/editing disclosures
    VULNERABILITY: No authorization check on pid parameter
    """
    pid = request.args.get('pid', type=int)
    if not pid:
        return jsonify({"error": "Missing pid parameter"}), 400
    
    patient = Patient.query.get(pid)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    if request.method == 'POST':
        # VULNERABLE: Can add disclosures to any patient
        data = request.json if request.is_json else request.form
        new_disclosure = Disclosure(
            patient_id=pid,
            recipient=data.get('recipient', 'Unknown'),
            description=data.get('description', ''),
            disclosure_date=data.get('date', '2024-01-01'),
            notes=data.get('notes', '')
        )
        db.session.add(new_disclosure)
        db.session.commit()
        return jsonify({"message": "Disclosure recorded", "id": new_disclosure.id})
    
    return render_template('record_disclosure.html', patient=patient)

@app.route('/interface/patient_file/summary/disclosure_delete.php', methods=['POST'])
@login_required
def disclosure_delete():
    """
    Mimics deletion endpoint - also vulnerable
    """
    disclosure_id = request.args.get('id', type=int)
    pid = request.args.get('pid', type=int)
    
    if not disclosure_id or not pid:
        return jsonify({"error": "Missing parameters"}), 400
    
    # VULNERABLE: No authorization check
    disclosure = Disclosure.query.get(disclosure_id)
    if disclosure and disclosure.patient_id == pid:
        db.session.delete(disclosure)
        db.session.commit()
        return jsonify({"message": "Disclosure deleted"})
    
    return jsonify({"error": "Disclosure not found"}), 404

# ============================================================================
# SAFE ENDPOINTS - For normal user operations
# ============================================================================

@app.route('/interface/patient_file/summary/')
@login_required
def patient_summary():
    """
    Shows patients the current user is assigned to (safe behavior)
    """
    # Staff can only see their assigned patient
    if current_user.assigned_patient_id:
        patients = [Patient.query.get(current_user.assigned_patient_id)]
    else:
        patients = []
    
    return render_template('patient_summary.html', patients=patients, user=current_user)

@app.route('/api/patients')
@login_required
def api_patients():
    """API to list accessible patients"""
    if current_user.role == 'admin':
        patients = Patient.query.all()
    elif current_user.assigned_patient_id:
        patients = [Patient.query.get(current_user.assigned_patient_id)]
    else:
        patients = []
    
    return jsonify([{
        "id": p.id, 
        "name": f"{p.fname} {p.lname}",
        "dob": p.dob
    } for p in patients if p])


def init_db():
    db.drop_all()
    db.create_all()
    
    # Read flag from environment - set at build time
    flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
    
    # Create users - mimicking OpenEMR user accounts
    # Admin user with full access
    admin = User(username='admin', password='Adm1n!EMR#2024', role='admin')
    db.session.add(admin)
    
    # Regular staff user with limited access (assigned to patient 2 only)
    staff = User(username='nurse', password='nurse123', role='staff', assigned_patient_id=2)
    db.session.add(staff)
    
    # Another staff user
    staff2 = User(username='reception', password='front2024', role='staff', assigned_patient_id=3)
    db.session.add(staff2)
    
    db.session.commit()
    
    # Create patients
    patient1 = Patient(fname='John', lname='Smith', dob='1985-03-15', ssn='123-45-6789')
    patient2 = Patient(fname='Jane', lname='Doe', dob='1990-07-22', ssn='987-65-4321')
    patient3 = Patient(fname='Bob', lname='Wilson', dob='1978-11-08', ssn='555-12-3456')
    
    db.session.add(patient1)
    db.session.add(patient2)
    db.session.add(patient3)
    db.session.commit()
    
    # Create disclosures for patients
    # Patient 1 (John Smith) - has sensitive disclosures including the flag
    disclosures_p1 = [
        Disclosure(patient_id=1, recipient='Insurance Co.', 
                   description='Medical records release for claim #12345',
                   disclosure_date='2023-06-15', notes='Routine insurance claim'),
        Disclosure(patient_id=1, recipient='Dr. External', 
                   description='Specialist referral records',
                   disclosure_date='2023-08-20', notes='Cardiology consultation'),
        Disclosure(patient_id=1, recipient='Legal Counsel', 
                   description='Records subpoena compliance',
                   disclosure_date='2023-11-01', notes='Case #2023-CV-5678'),
        Disclosure(patient_id=1, recipient='Research Study', 
                   description='De-identified data for clinical trial',
                   disclosure_date='2024-01-10', notes=f'CONFIDENTIAL STUDY DATA: {flag}'),
    ]
    
    # Patient 2 (Jane Doe) - nurse's assigned patient
    disclosures_p2 = [
        Disclosure(patient_id=2, recipient='Primary Care', 
                   description='Annual physical records',
                   disclosure_date='2023-05-10', notes='Routine checkup'),
        Disclosure(patient_id=2, recipient='Lab Services', 
                   description='Blood work results',
                   disclosure_date='2023-12-01', notes='Standard panel'),
    ]
    
    # Patient 3 (Bob Wilson) - reception's assigned patient
    disclosures_p3 = [
        Disclosure(patient_id=3, recipient='Pharmacy', 
                   description='Prescription verification',
                   disclosure_date='2024-02-15', notes='Medication refill'),
    ]
    
    for d in disclosures_p1 + disclosures_p2 + disclosures_p3:
        db.session.add(d)
    
    db.session.commit()
    print("Database initialized with test data")


if __name__ == '__main__':
    with app.app_context():
        init_db() 
    app.run(host='0.0.0.0', port=5003)

