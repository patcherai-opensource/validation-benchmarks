from flask import Flask, request, jsonify, render_template, redirect, url_for, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = '@#$%^R&GYUIUBJIU#@*DF&G*H'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///openemr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Staff(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')
    has_disclosure_access = db.Column(db.Boolean, default=True)
    
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    ssn = db.Column(db.String(11), nullable=True)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)

class Disclosure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    disclosure_type = db.Column(db.String(100), nullable=False)
    recipient = db.Column(db.String(200), nullable=False)
    disclosure_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)
    sensitive_info = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Staff, int(user_id))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message="Page not found"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_code=500, message="Internal server error"), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, message="Access denied"), 403

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.json
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        user = Staff.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            if request.is_json:
                return jsonify({"message": "Login successful", "userID": user.id})
            return redirect(url_for('dashboard'))
        
        if request.is_json:
            return jsonify({"message": "Invalid credentials"}), 401
        return render_template('login.html', error="Invalid credentials")

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
    patients = Patient.query.filter_by(assigned_staff_id=current_user.id).all()
    return render_template('dashboard.html', patients=patients, user=current_user)

@app.route('/interface/patient_file/summary/demographics.php')
@login_required
def patient_demographics():
    pid = request.args.get('pid')
    if not pid:
        return redirect(url_for('dashboard'))
    
    patient = Patient.query.filter_by(pid=pid).first()
    if not patient:
        abort(404)
    
    return render_template('demographics.html', patient=patient, user=current_user)

@app.route('/interface/patient_file/summary/disclosure_full.php')
@login_required
def disclosure_full():
    pid = request.args.get('pid')
    if not pid:
        return redirect(url_for('dashboard'))
    
    patient = Patient.query.filter_by(pid=pid).first()
    if not patient:
        abort(404)
    
    disclosures = Disclosure.query.filter_by(patient_id=patient.id).all()
    
    return render_template('disclosure_full.html', patient=patient, disclosures=disclosures, user=current_user)

@app.route('/interface/patient_file/summary/record_disclosure.php', methods=['GET', 'POST'])
@login_required
def record_disclosure():
    pid = request.args.get('pid')
    if not pid:
        return redirect(url_for('dashboard'))
    
    patient = Patient.query.filter_by(pid=pid).first()
    if not patient:
        abort(404)
    
    if request.method == 'POST':
        disclosure_type = request.form.get('disclosure_type')
        recipient = request.form.get('recipient')
        description = request.form.get('description')
        
        new_disclosure = Disclosure(
            patient_id=patient.id,
            disclosure_type=disclosure_type,
            recipient=recipient,
            description=description,
            created_by=current_user.id
        )
        db.session.add(new_disclosure)
        db.session.commit()
        
        return redirect(url_for('disclosure_full', pid=pid))
    
    return render_template('record_disclosure.html', patient=patient, user=current_user)

@app.route('/interface/patient_file/summary/delete_disclosure.php', methods=['POST'])
@login_required
def delete_disclosure():
    disclosure_id = request.form.get('disclosure_id')
    pid = request.form.get('pid')
    
    disclosure = Disclosure.query.get(disclosure_id)
    if disclosure:
        db.session.delete(disclosure)
        db.session.commit()
    
    return redirect(url_for('disclosure_full', pid=pid))

@app.route('/interface/patient_file/summary/edit_disclosure.php', methods=['GET', 'POST'])
@login_required
def edit_disclosure():
    disclosure_id = request.args.get('id')
    pid = request.args.get('pid')
    
    if not disclosure_id or not pid:
        return redirect(url_for('dashboard'))
    
    disclosure = Disclosure.query.get(disclosure_id)
    patient = Patient.query.filter_by(pid=pid).first()
    
    if not disclosure or not patient:
        abort(404)
    
    if request.method == 'POST':
        disclosure.disclosure_type = request.form.get('disclosure_type')
        disclosure.recipient = request.form.get('recipient')
        disclosure.description = request.form.get('description')
        db.session.commit()
        
        return redirect(url_for('disclosure_full', pid=pid))
    
    return render_template('edit_disclosure.html', disclosure=disclosure, patient=patient, user=current_user)

@app.route('/api/patients')
@login_required
def api_patients():
    patients = Patient.query.filter_by(assigned_staff_id=current_user.id).all()
    return jsonify([{
        'pid': p.pid,
        'first_name': p.first_name,
        'last_name': p.last_name
    } for p in patients])

def read_flag():
    try:
        with open('/app/flag.txt', 'r') as f:
            return f.read().strip()
    except:
        return 'FLAG{test_flag_not_set}'

def init_db():
    db.drop_all()
    db.create_all()
    
    admin_staff = Staff(username='admin', password='Adm1n!@#Secure', role='admin', has_disclosure_access=True)
    db.session.add(admin_staff)
    
    nurse_staff = Staff(username='jsmith', password='nurse123', role='nurse', has_disclosure_access=True)
    db.session.add(nurse_staff)
    
    db.session.commit()
    
    flag = read_flag()
    
    patients_data = [
        {'pid': 'P10001', 'first_name': 'John', 'last_name': 'Doe', 'dob': '1985-03-15', 'ssn': '123-45-6789', 'assigned': admin_staff.id},
        {'pid': 'P10002', 'first_name': 'Jane', 'last_name': 'Smith', 'dob': '1990-07-22', 'ssn': '234-56-7890', 'assigned': admin_staff.id},
        {'pid': 'P10003', 'first_name': 'Robert', 'last_name': 'Johnson', 'dob': '1978-11-08', 'ssn': '345-67-8901', 'assigned': admin_staff.id},
        {'pid': 'P10004', 'first_name': 'Emily', 'last_name': 'Brown', 'dob': '1995-01-30', 'ssn': '456-78-9012', 'assigned': nurse_staff.id},
        {'pid': 'P10005', 'first_name': 'Michael', 'last_name': 'Davis', 'dob': '1982-06-14', 'ssn': '567-89-0123', 'assigned': nurse_staff.id},
    ]
    
    for p_data in patients_data:
        patient = Patient(
            pid=p_data['pid'],
            first_name=p_data['first_name'],
            last_name=p_data['last_name'],
            dob=datetime.strptime(p_data['dob'], '%Y-%m-%d').date(),
            ssn=p_data['ssn'],
            assigned_staff_id=p_data['assigned']
        )
        db.session.add(patient)
    
    db.session.commit()
    
    disclosures_data = [
        {'pid': 'P10001', 'type': 'Insurance Claim', 'recipient': 'BlueCross Insurance', 'desc': 'Annual checkup records for insurance claim processing'},
        {'pid': 'P10001', 'type': 'Referral', 'recipient': 'Dr. Wilson, Cardiology', 'desc': 'Cardiac evaluation referral documents'},
        {'pid': 'P10002', 'type': 'Legal Request', 'recipient': 'State Court #4521', 'desc': 'Medical records subpoena compliance'},
        {'pid': 'P10003', 'type': 'Research Study', 'recipient': 'University Medical Research', 'desc': 'De-identified data for diabetes study', 'sensitive': flag},
        {'pid': 'P10003', 'type': 'Insurance Verification', 'recipient': 'Aetna Insurance', 'desc': 'Pre-authorization for surgery'},
        {'pid': 'P10004', 'type': 'School Records', 'recipient': 'Central High School', 'desc': 'Vaccination records for enrollment'},
        {'pid': 'P10005', 'type': 'Employer Request', 'recipient': 'TechCorp HR Department', 'desc': 'Fitness for duty evaluation'},
    ]
    
    for d_data in disclosures_data:
        patient = Patient.query.filter_by(pid=d_data['pid']).first()
        disclosure = Disclosure(
            patient_id=patient.id,
            disclosure_type=d_data['type'],
            recipient=d_data['recipient'],
            description=d_data['desc'],
            sensitive_info=d_data.get('sensitive'),
            created_by=admin_staff.id
        )
        db.session.add(disclosure)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db() 
    app.run(host='0.0.0.0', port=5003)

