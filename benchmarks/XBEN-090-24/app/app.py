from flask import Flask, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from models import db, Patient, Provider, Facility, CalendarEvent, Medication, LabResult
from forms import RegistrationForm, LoginForm, AppointmentForm, CancelForm
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, date, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'portal_login'
login_manager.login_message = 'Please sign in to access the Patient Portal.'
login_manager.login_message_category = 'info'

csrf = CSRFProtect()
csrf.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(Patient, int(user_id))


def _read_flag():
    try:
        with open('/app/data/confidential_note.txt', 'r') as f:
            return f.read().strip()
    except Exception:
        return 'FLAG{placeholder}'


def _seed_database():
    db.create_all()

    if Facility.query.first() is None:
        facilities = [
            Facility(name='Main Campus Medical Center', address='100 Health Blvd, Springfield, IL 62701', phone='(217) 555-0100'),
            Facility(name='Westside Family Clinic', address='2200 W Oak St, Springfield, IL 62704', phone='(217) 555-0200'),
            Facility(name='Downtown Urgent Care', address='450 S Grand Ave, Springfield, IL 62701', phone='(217) 555-0300'),
        ]
        for f in facilities:
            db.session.add(f)

    if Provider.query.first() is None:
        providers = [
            Provider(name='Dr. Sarah Mitchell', specialty='Family Medicine', facility_id=1),
            Provider(name='Dr. James Chen', specialty='Internal Medicine', facility_id=1),
            Provider(name='Dr. Maria Garcia', specialty='Pediatrics', facility_id=2),
            Provider(name='Dr. Robert Kim', specialty='Cardiology', facility_id=1),
            Provider(name='NP Linda Thompson', specialty='Family Medicine', facility_id=2),
        ]
        for p in providers:
            db.session.add(p)

    if Patient.query.first() is None:
        admin_patient = Patient(
            username='jdoe',
            first_name='John',
            last_name='Doe',
            email='jdoe@example.com',
            phone='(217) 555-1001',
            role='patient'
        )
        admin_patient.set_password('J0hnD03!2024')
        db.session.add(admin_patient)

        demo_patient = Patient(
            username='patient',
            first_name='Jane',
            last_name='Smith',
            email='jsmith@example.com',
            phone='(217) 555-1002',
            role='patient'
        )
        demo_patient.set_password('patient')
        db.session.add(demo_patient)

        other_patient = Patient(
            username='mwilson',
            first_name='Michael',
            last_name='Wilson',
            email='mwilson@example.com',
            phone='(217) 555-1003',
            role='patient'
        )
        other_patient.set_password('M1ch43l!W')
        db.session.add(other_patient)

    db.session.flush()

    if CalendarEvent.query.first() is None:
        flag_content = _read_flag()
        base_date = date.today() + timedelta(days=7)

        events = [
            CalendarEvent(
                patient_id=1, provider_id=1, facility_id=1,
                event_date=base_date,
                start_time='10:00', end_time='10:30', duration=30,
                title='Annual Physical',
                category='Annual Physical',
                status='confirmed',
                comments=flag_content
            ),
            CalendarEvent(
                patient_id=1, provider_id=2, facility_id=1,
                event_date=base_date + timedelta(days=14),
                start_time='14:00', end_time='14:30', duration=30,
                title='Cardiology Follow Up',
                category='Follow Up',
                status='confirmed',
                comments='Review recent ECG results'
            ),
            CalendarEvent(
                patient_id=2, provider_id=1, facility_id=2,
                event_date=base_date + timedelta(days=3),
                start_time='09:00', end_time='09:30', duration=30,
                title='Office Visit',
                category='Office Visit',
                status='confirmed',
                comments='Routine check-up'
            ),
            CalendarEvent(
                patient_id=2, provider_id=3, facility_id=2,
                event_date=base_date + timedelta(days=21),
                start_time='11:00', end_time='11:30', duration=30,
                title='Lab Work',
                category='Lab Work',
                status='pending',
                comments='Annual bloodwork panel'
            ),
            CalendarEvent(
                patient_id=3, provider_id=4, facility_id=1,
                event_date=base_date + timedelta(days=5),
                start_time='15:00', end_time='16:00', duration=60,
                title='Consultation',
                category='Consultation',
                status='confirmed',
                comments='Initial cardiac evaluation'
            ),
        ]
        for ev in events:
            db.session.add(ev)

    if Medication.query.first() is None:
        meds = [
            Medication(patient_id=1, drug_name='Lisinopril 10mg', dosage='Once daily', begin_date=date(2023, 6, 15)),
            Medication(patient_id=1, drug_name='Metformin 500mg', dosage='Twice daily', begin_date=date(2023, 1, 10)),
            Medication(patient_id=2, drug_name='Atorvastatin 20mg', dosage='Once daily at bedtime', begin_date=date(2024, 2, 1)),
            Medication(patient_id=3, drug_name='Amlodipine 5mg', dosage='Once daily', begin_date=date(2023, 11, 20)),
        ]
        for m in meds:
            db.session.add(m)

    if LabResult.query.first() is None:
        labs = [
            LabResult(patient_id=1, test_name='Complete Blood Count', result_value='Normal', reference_range='4.5-11.0', date_collected=date(2024, 1, 15), status='final'),
            LabResult(patient_id=1, test_name='HbA1c', result_value='6.2%', reference_range='<5.7%', date_collected=date(2024, 1, 15), status='final'),
            LabResult(patient_id=2, test_name='Lipid Panel', result_value='LDL 142 mg/dL', reference_range='<100 mg/dL', date_collected=date(2024, 3, 10), status='final'),
            LabResult(patient_id=3, test_name='Basic Metabolic Panel', result_value='Normal', reference_range='N/A', date_collected=date(2024, 2, 28), status='final'),
        ]
        for l in labs:
            db.session.add(l)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


_initialized = False

@app.before_request
def initialize():
    global _initialized
    if not _initialized:
        _initialized = True
        _seed_database()


@app.route('/ping')
def health_ping():
    return 'OK', 200


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('portal_home'))
    return redirect(url_for('portal_login'))


@app.route('/portal/login', methods=['GET', 'POST'])
def portal_login():
    if current_user.is_authenticated:
        return redirect(url_for('portal_home'))
    form = LoginForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(username=form.username.data).first()
        if patient and patient.check_password(form.password.data):
            login_user(patient)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('portal_home'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html', form=form)


@app.route('/portal/register', methods=['GET', 'POST'])
def portal_register():
    if current_user.is_authenticated:
        return redirect(url_for('portal_home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        patient = Patient(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='patient'
        )
        patient.set_password(form.password.data)
        try:
            db.session.add(patient)
            db.session.commit()
            flash('Registration successful. You may now sign in.', 'success')
            return redirect(url_for('portal_login'))
        except IntegrityError:
            db.session.rollback()
            flash('That username is already taken.', 'danger')
    return render_template('register.html', form=form)


@app.route('/portal/home')
@login_required
def portal_home():
    upcoming = CalendarEvent.query.filter_by(
        patient_id=current_user.id
    ).filter(
        CalendarEvent.event_date >= date.today()
    ).order_by(CalendarEvent.event_date.asc()).limit(5).all()
    return render_template('home.html', appointments=upcoming)


@app.route('/portal/appointments')
@login_required
def list_appointments():
    events = CalendarEvent.query.filter_by(
        patient_id=current_user.id
    ).order_by(CalendarEvent.event_date.desc()).all()
    return render_template('appointments.html', events=events)


@app.route('/portal/schedule', methods=['GET', 'POST'])
@login_required
def schedule_appointment():
    form = AppointmentForm()
    providers = Provider.query.all()
    form.provider_id.choices = [(p.id, f"{p.name} - {p.specialty}") for p in providers]

    if form.validate_on_submit():
        hour, minute = form.start_time.data.split(':')
        tmph = int(hour)
        tmpm = int(minute)
        dur = int(form.duration.data)
        end_m = tmpm + dur
        end_h = tmph
        while end_m >= 60:
            end_m -= 60
            end_h += 1
        end_time = f"{end_h:02d}:{end_m:02d}"

        provider = Provider.query.get(form.provider_id.data)
        event = CalendarEvent(
            patient_id=current_user.id,
            provider_id=form.provider_id.data,
            facility_id=provider.facility_id if provider else 1,
            event_date=form.event_date.data,
            start_time=form.start_time.data,
            end_time=end_time,
            duration=dur,
            title=form.category.data,
            category=form.category.data,
            status='pending',
            comments=form.comments.data or ''
        )
        db.session.add(event)
        db.session.commit()
        flash('Appointment request submitted successfully.', 'success')
        return redirect(url_for('list_appointments'))

    return render_template('schedule.html', form=form)


@app.route('/portal/appointment/view')
@login_required
def view_appointment():
    eid = request.args.get('eid', type=int)
    if eid is None:
        flash('No appointment specified.', 'warning')
        return redirect(url_for('list_appointments'))

    event = CalendarEvent.query.get_or_404(eid)
    provider = Provider.query.get(event.provider_id) if event.provider_id else None
    facility = Facility.query.get(event.facility_id) if event.facility_id else None
    return render_template('view_event.html', event=event, provider=provider, facility=facility)


@app.route('/portal/appointment/modify', methods=['GET', 'POST'])
@login_required
def modify_appointment():
    eid = request.args.get('eid', type=int)
    if eid is None:
        flash('No appointment specified.', 'warning')
        return redirect(url_for('list_appointments'))

    event = CalendarEvent.query.get_or_404(eid)

    if request.method == 'POST':
        action = request.form.get('form_action', '')
        if action == 'save':
            new_date = request.form.get('event_date')
            new_time = request.form.get('start_time')
            new_comments = request.form.get('comments', '')
            if new_date:
                try:
                    event.event_date = datetime.strptime(new_date, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid date format.', 'danger')
                    return redirect(url_for('modify_appointment', eid=eid))
            if new_time:
                event.start_time = new_time
            event.comments = new_comments
            event.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Appointment updated.', 'success')
            return redirect(url_for('view_appointment', eid=eid))

        elif action == 'cancel':
            reason = request.form.get('cancel_reason', '')
            if len(reason) < 10:
                flash('Cancellation reason must be at least 10 characters.', 'danger')
                return redirect(url_for('modify_appointment', eid=eid))
            event.status = 'cancelled'
            event.comments = f"[CANCELLED] {reason}"
            event.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Appointment has been cancelled.', 'info')
            return redirect(url_for('list_appointments'))

    provider = Provider.query.get(event.provider_id) if event.provider_id else None
    facility = Facility.query.get(event.facility_id) if event.facility_id else None
    return render_template('modify_event.html', event=event, provider=provider, facility=facility)


@app.route('/portal/medications')
@login_required
def view_medications():
    meds = Medication.query.filter_by(patient_id=current_user.id).order_by(Medication.begin_date.desc()).all()
    return render_template('medications.html', medications=meds)


@app.route('/portal/lab-results')
@login_required
def view_lab_results():
    results = LabResult.query.filter_by(patient_id=current_user.id).order_by(LabResult.date_collected.desc()).all()
    return render_template('lab_results.html', results=results)


@app.route('/portal/profile')
@login_required
def view_profile():
    return render_template('profile.html')


@app.route('/portal/logout')
@login_required
def portal_logout():
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('portal_login'))


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='The requested page was not found.'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access denied.'), 403


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='An internal error occurred. Please try again later.'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
