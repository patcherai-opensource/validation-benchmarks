import os
import hashlib
from datetime import timedelta, datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from functools import wraps
import jinja2

app = Flask(__name__)
app.secret_key = 'xK9mP2vL8nQ4wR7jT5sY1bF6hD3cA0e'
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///printcore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

login_manager = LoginManager(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)


# ---- Models ----

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='operator')
    api_key = db.Column(db.String(64), nullable=True)

    def is_admin(self):
        return self.role == 'admin'


class PrinterProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    volume_x = db.Column(db.Float, default=200.0)
    volume_y = db.Column(db.Float, default=200.0)
    volume_z = db.Column(db.Float, default=200.0)
    nozzle_diameter = db.Column(db.Float, default=0.4)
    heated_bed = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PrintJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='queued')
    progress = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    printer_id = db.Column(db.Integer, db.ForeignKey('printer_profile.id'), nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EventScript(db.Model):
    """Stores user-defined command scripts (templates) for printer events."""
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False, unique=True)
    script_body = db.Column(db.Text, nullable=False, default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), default='INFO')
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ---- Script Rendering Engine ----
# Renders event scripts as Jinja2 templates, providing context about the
# current printer state. Scripts are authored by admins in Settings.

class ScriptEngine:
    """Handles rendering of event-driven command scripts."""

    def __init__(self):
        self._env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            undefined=jinja2.Undefined,
            keep_trailing_newline=True,
        )

    def render_event_script(self, script_body, context=None):
        if context is None:
            context = {}
        try:
            template = self._env.from_string(script_body)
            return template.render(**context)
        except Exception as e:
            return f"; Script rendering error: {type(e).__name__}"

script_engine = ScriptEngine()


# ---- Initialization ----

def _init_database():
    db.create_all()

    # Create default admin user (first-run setup)
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password='printcore',
            role='admin',
            api_key=hashlib.sha256(b'default-api-key-seed').hexdigest()[:32]
        )
        db.session.add(admin)

    # Create a default operator user
    if not User.query.filter_by(username='operator').first():
        op = User(
            username='operator',
            password='operator123',
            role='operator'
        )
        db.session.add(op)

    # Create default printer profile
    if not PrinterProfile.query.first():
        profile = PrinterProfile(
            name='Default Printer',
            model='Prusa i3 MK3S+',
            volume_x=250.0,
            volume_y=210.0,
            volume_z=210.0,
            nozzle_diameter=0.4,
            heated_bed=True
        )
        db.session.add(profile)

    # Create default event scripts (empty templates)
    default_events = [
        'afterPrinterConnected',
        'beforePrinterDisconnected',
        'beforePrintStarted',
        'afterPrintCancelled',
        'afterPrintDone',
        'beforePrintPaused',
        'afterPrintResumed',
    ]
    for evt in default_events:
        if not EventScript.query.filter_by(event_name=evt).first():
            es = EventScript(event_name=evt, script_body='')
            db.session.add(es)

    db.session.commit()


@app.before_request
def ensure_tables():
    if not hasattr(app, '_db_initialized'):
        _init_database()
        app._db_initialized = True


# ---- Auth helpers ----

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def api_login_required(f):
    """Check for X-Api-Key header or session auth."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-Api-Key')
        if api_key:
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                login_user(user, remember=False)
                return f(*args, **kwargs)
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        abort(401)
    return decorated


# ---- Error Handlers ----

@app.errorhandler(401)
def unauthorized(e):
    if request.path.startswith('/api/'):
        return jsonify(error='Unauthorized'), 401
    return redirect(url_for('login'))

@app.errorhandler(403)
def forbidden(e):
    if request.path.startswith('/api/'):
        return jsonify(error='Forbidden'), 403
    return render_template('error.html', code=403, message='Forbidden'), 403

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify(error='Not found'), 404
    return render_template('error.html', code=404, message='Not Found'), 404


# ---- Web Routes ----

@app.route('/ping')
def ping():
    return 'ok', 200

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid credentials.')
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    printers = PrinterProfile.query.all()
    recent_jobs = PrintJob.query.order_by(PrintJob.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', printers=printers, jobs=recent_jobs)


@app.route('/printers')
@login_required
def printers():
    profiles = PrinterProfile.query.all()
    return render_template('printers.html', profiles=profiles)


@app.route('/jobs')
@login_required
def jobs():
    all_jobs = PrintJob.query.order_by(PrintJob.created_at.desc()).all()
    return render_template('jobs.html', jobs=all_jobs)


@app.route('/settings')
@admin_required
def settings_page():
    scripts = EventScript.query.all()
    printer = PrinterProfile.query.first()
    return render_template('settings.html', scripts=scripts, printer=printer)


# ---- API Routes ----

@app.route('/api/version', methods=['GET'])
def api_version():
    return jsonify({
        'server': '1.8.7',
        'api': '0.1',
        'text': 'PrintCore 1.8.7'
    })


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get('user', '')
    password = data.get('pass', '')
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        login_user(user)
        return jsonify({
            'name': user.username,
            'active': True,
            'admin': user.is_admin(),
            'apikey': user.api_key,
            'session': session.get('_id', ''),
        })
    return jsonify(error='Invalid credentials'), 401


@app.route('/api/currentuser', methods=['GET'])
@api_login_required
def api_current_user():
    return jsonify({
        'name': current_user.username,
        'admin': current_user.is_admin(),
    })


@app.route('/api/printerprofiles', methods=['GET'])
@api_login_required
def api_printer_profiles():
    profiles = PrinterProfile.query.all()
    result = {}
    for p in profiles:
        result[str(p.id)] = {
            'id': p.id,
            'name': p.name,
            'model': p.model,
            'volume': {'x': p.volume_x, 'y': p.volume_y, 'z': p.volume_z},
            'nozzle': p.nozzle_diameter,
            'heatedBed': p.heated_bed,
        }
    return jsonify(profiles=result)


@app.route('/api/job', methods=['GET'])
@api_login_required
def api_job():
    job = PrintJob.query.filter(PrintJob.status.in_(['printing', 'paused'])).first()
    if job:
        return jsonify({
            'job': {
                'file': {'name': job.filename},
                'estimatedPrintTime': None,
            },
            'progress': {
                'completion': job.progress,
                'printTimeLeft': None,
            },
            'state': job.status.capitalize()
        })
    return jsonify({
        'job': None,
        'progress': None,
        'state': 'Operational'
    })


@app.route('/api/connection', methods=['GET'])
@api_login_required
def api_connection():
    return jsonify({
        'current': {
            'state': 'Operational',
            'port': '/dev/ttyUSB0',
            'baudrate': 115200,
            'printerProfile': '_default',
        },
        'options': {
            'ports': ['/dev/ttyUSB0', '/dev/ttyACM0'],
            'baudrates': [115200, 250000],
            'printerProfiles': [{'id': '_default', 'name': 'Default'}],
        }
    })


# ---- Settings API (admin only) ----

@app.route('/api/settings', methods=['GET'])
@api_login_required
def api_get_settings():
    if not current_user.is_admin():
        abort(403)

    scripts = {}
    for es in EventScript.query.all():
        scripts[es.event_name] = es.script_body

    printer = PrinterProfile.query.first()
    return jsonify({
        'printer': {
            'name': printer.name if printer else '',
            'model': printer.model if printer else '',
        },
        'scripts': {
            'command': scripts
        },
        'api': {
            'key': current_user.api_key,
        },
        'server': {
            'onlineCheck': {'enabled': True},
            'allowFraming': False,
        },
        'feature': {
            'temperatureGraph': True,
            'sdSupport': True,
        }
    })


@app.route('/api/settings', methods=['POST'])
@api_login_required
def api_save_settings():
    if not current_user.is_admin():
        abort(403)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400)

    # Handle script updates
    if 'scripts' in data:
        cmd_scripts = data['scripts'].get('command', {})
        if isinstance(cmd_scripts, dict):
            for event_name, body in cmd_scripts.items():
                if event_name == 'snippets':
                    continue
                if not isinstance(body, str):
                    continue
                es = EventScript.query.filter_by(event_name=event_name).first()
                if es:
                    es.script_body = body.replace('\r\n', '\n').replace('\r', '\n')
                    es.updated_at = datetime.utcnow()
                else:
                    es = EventScript(
                        event_name=event_name,
                        script_body=body.replace('\r\n', '\n').replace('\r', '\n')
                    )
                    db.session.add(es)

    # Handle printer profile updates
    if 'printer' in data:
        printer = PrinterProfile.query.first()
        if printer:
            if 'name' in data['printer']:
                printer.name = data['printer']['name']
            if 'model' in data['printer']:
                printer.model = data['printer']['model']

    db.session.commit()

    _log_event('INFO', 'Settings updated by {}'.format(current_user.username))

    return api_get_settings()


# ---- Script Execution / Event Trigger API ----

@app.route('/api/printer/command', methods=['POST'])
@api_login_required
def api_printer_command():
    """Send raw commands or trigger event scripts on the printer."""
    data = request.get_json(silent=True) or {}

    # Direct command passthrough
    if 'commands' in data:
        commands = data['commands']
        if not isinstance(commands, list):
            commands = [commands]
        _log_event('INFO', 'Commands sent: {}'.format(len(commands)))
        return jsonify(ok=True)

    abort(400)


@app.route('/api/job', methods=['POST'])
@api_login_required
def api_job_control():
    """Control print job: start, cancel, pause, resume."""
    data = request.get_json(silent=True) or {}
    command = data.get('command', '')

    event_mapping = {
        'start': 'beforePrintStarted',
        'cancel': 'afterPrintCancelled',
        'pause': 'beforePrintPaused',
        'resume': 'afterPrintResumed',
    }

    if command not in event_mapping:
        abort(400)

    event_name = event_mapping[command]
    es = EventScript.query.filter_by(event_name=event_name).first()

    rendered_output = ''
    if es and es.script_body.strip():
        context = {
            'event': {'type': event_name, 'timestamp': datetime.utcnow().isoformat()},
            'printer': _get_printer_context(),
            'user': current_user.username,
        }
        rendered_output = script_engine.render_event_script(es.script_body, context)

    # Simulate the job state change
    if command == 'start':
        job = PrintJob.query.filter_by(status='queued').first()
        if job:
            job.status = 'printing'
            job.started_at = datetime.utcnow()
    elif command == 'cancel':
        job = PrintJob.query.filter_by(status='printing').first()
        if job:
            job.status = 'cancelled'
            job.completed_at = datetime.utcnow()
    elif command == 'pause':
        job = PrintJob.query.filter_by(status='printing').first()
        if job:
            job.status = 'paused'
    elif command == 'resume':
        job = PrintJob.query.filter_by(status='paused').first()
        if job:
            job.status = 'printing'

    db.session.commit()

    _log_event('INFO', 'Job command: {} — script output: {}'.format(command, rendered_output[:200]))

    return jsonify({
        'ok': True,
        'command': command,
        'event': event_name,
        'script_output': rendered_output,
    })


@app.route('/api/connection', methods=['POST'])
@api_login_required
def api_connect_printer():
    """Connect/disconnect the printer, triggering event scripts."""
    data = request.get_json(silent=True) or {}
    command = data.get('command', '')

    if command == 'connect':
        event_name = 'afterPrinterConnected'
    elif command == 'disconnect':
        event_name = 'beforePrinterDisconnected'
    else:
        abort(400)

    es = EventScript.query.filter_by(event_name=event_name).first()
    rendered_output = ''
    if es and es.script_body.strip():
        context = {
            'event': {'type': event_name, 'timestamp': datetime.utcnow().isoformat()},
            'printer': _get_printer_context(),
            'user': current_user.username,
        }
        rendered_output = script_engine.render_event_script(es.script_body, context)

    _log_event('INFO', 'Connection: {} — script output: {}'.format(command, rendered_output[:200]))

    return jsonify({
        'ok': True,
        'command': command,
        'event': event_name,
        'script_output': rendered_output,
    })


@app.route('/api/files/local', methods=['POST'])
@api_login_required
def api_upload_file():
    """Upload a GCODE file for printing."""
    if 'file' not in request.files:
        abort(400)

    f = request.files['file']
    if not f.filename:
        abort(400)

    filename = f.filename
    # Create a job entry
    job = PrintJob(
        filename=filename,
        status='queued',
        user_id=current_user.id,
        printer_id=PrinterProfile.query.first().id if PrinterProfile.query.first() else None,
    )
    db.session.add(job)
    db.session.commit()

    _log_event('INFO', 'File uploaded: {}'.format(filename))

    return jsonify({
        'files': {
            'local': {
                'name': filename,
                'origin': 'local',
            }
        },
        'done': True,
    })


@app.route('/api/logs', methods=['GET'])
@api_login_required
def api_logs():
    if not current_user.is_admin():
        abort(403)
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(50).all()
    return jsonify({
        'logs': [
            {'level': l.level, 'message': l.message, 'timestamp': l.timestamp.isoformat()}
            for l in logs
        ]
    })


# ---- Helpers ----

def _get_printer_context():
    printer = PrinterProfile.query.first()
    if printer:
        return {
            'name': printer.name,
            'model': printer.model,
            'volume': {'x': printer.volume_x, 'y': printer.volume_y, 'z': printer.volume_z},
        }
    return {}


def _log_event(level, message):
    log = SystemLog(level=level, message=message)
    db.session.add(log)
    db.session.commit()


# ---- Response headers ----

@app.after_request
def set_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers.pop('Server', None)
    return response


if __name__ == '__main__':
    with app.app_context():
        _init_database()
    app.run(host='0.0.0.0', port=5003, debug=False)
