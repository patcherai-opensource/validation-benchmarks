import os
import json
import hashlib
import subprocess
import secrets
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///panel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

db = SQLAlchemy(app)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    can_change_settings = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(80), nullable=False)
    varname = db.Column(db.String(120), nullable=False)
    value = db.Column(db.Text, default='')

    __table_args__ = (db.UniqueConstraint('group', 'varname'),)


class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    document_root = db.Column(db.String(255), default='/var/www/html')
    is_ssl = db.Column(db.Boolean, default=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))


class CronTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, server_default=db.func.now())


NO_EXPORT_SETTINGS = [
    'panel.admin_email',
    'system.last_account_number',
    'system.last_guid',
    'system.last_cron_run',
    'system.last_traffic_run',
    'system.update_check_data',
]

DEFAULT_SETTINGS = {
    'panel': {
        'version': '2.0.10',
        'db_version': '202302010',
        'admin_email': 'admin@localhost',
        'default_language': 'en',
        'session_timeout': '600',
        'title': 'Server Management Panel',
    },
    'system': {
        'hostname': 'srv01.example.com',
        'ipaddress': '0.0.0.0',
        'webserver': 'nginx',
        'documentroot_prefix': '/var/www/vhosts/',
        'logfiles_directory': '/var/log/nginx/',
        'use_ssl': '1',
        'service_reload_cmd': '/usr/sbin/service nginx reload',
        'dns_reload_cmd': '/usr/sbin/rndc reload',
        'mail_reload_cmd': '/usr/sbin/service postfix reload',
        'ftp_reload_cmd': '/usr/sbin/service proftpd reload',
        'cron_reload_cmd': '/usr/sbin/service cron reload',
        'last_account_number': '10000',
        'last_guid': '10000',
        'last_cron_run': '',
        'last_traffic_run': '',
        'update_check_data': '',
    },
    'mail': {
        'use_smtp': '0',
        'smtp_host': 'localhost',
        'smtp_port': '25',
        'smtp_user': '',
        'smtp_password': '',
        'smtp_tls': '0',
    },
    'security': {
        'login_fail_limit': '5',
        'login_fail_locktime': '300',
        'password_min_length': '8',
        'enable_2fa': '0',
    },
    'cron': {
        'tasks_enabled': '1',
        'interval_traffic': '60',
        'interval_usage': '1440',
    },
}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def settings_permission_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        admin = Admin.query.get(session['admin_id'])
        if not admin or not admin.can_change_settings:
            flash('Insufficient privileges.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


def get_setting(key):
    parts = key.split('.', 1)
    if len(parts) != 2:
        return None
    s = Setting.query.filter_by(group=parts[0], varname=parts[1]).first()
    return s.value if s else None


def set_setting(key, value):
    parts = key.split('.', 1)
    if len(parts) != 2:
        return False
    s = Setting.query.filter_by(group=parts[0], varname=parts[1]).first()
    if s:
        s.value = value
        db.session.commit()
        return True
    return False


def apply_service_config():
    results = []
    reload_cmd = get_setting('system.service_reload_cmd')
    if reload_cmd:
        try:
            proc = subprocess.run(
                reload_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            output = proc.stdout.strip() or proc.stderr.strip()
            results.append({
                'service': 'webserver',
                'status': 'ok' if proc.returncode == 0 else 'error',
                'output': output
            })
        except subprocess.TimeoutExpired:
            results.append({'service': 'webserver', 'status': 'timeout'})
        except Exception:
            results.append({'service': 'webserver', 'status': 'error'})
    return results


@app.route('/')
def index():
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('loginname', '')
        password = request.form.get('password', '')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    admin = Admin.query.get(session['admin_id'])
    domain_count = Domain.query.count()
    return render_template('dashboard.html', admin=admin, domain_count=domain_count)


@app.route('/admin/domains')
@login_required
def domains():
    all_domains = Domain.query.all()
    return render_template('domains.html', domains=all_domains)


@app.route('/admin/domains/add', methods=['POST'])
@login_required
def add_domain():
    name = request.form.get('domain', '').strip()
    docroot = request.form.get('document_root', '/var/www/html').strip()
    use_ssl = request.form.get('is_ssl') == '1'
    if name:
        d = Domain(domain=name, document_root=docroot, is_ssl=use_ssl, admin_id=session['admin_id'])
        db.session.add(d)
        db.session.commit()
        flash('Domain added.', 'success')
    return redirect(url_for('domains'))


@app.route('/admin/domains/delete/<int:domain_id>', methods=['POST'])
@login_required
def delete_domain(domain_id):
    d = Domain.query.get_or_404(domain_id)
    db.session.delete(d)
    db.session.commit()
    flash('Domain removed.', 'success')
    return redirect(url_for('domains'))


@app.route('/admin/configuration')
@settings_permission_required
def configuration():
    settings = Setting.query.order_by(Setting.group, Setting.varname).all()
    grouped = {}
    for s in settings:
        grouped.setdefault(s.group, []).append(s)
    return render_template('configuration.html', grouped=grouped)


COMMAND_SETTINGS = {
    'system.service_reload_cmd',
    'system.dns_reload_cmd',
    'system.mail_reload_cmd',
    'system.ftp_reload_cmd',
    'system.cron_reload_cmd',
}

ALLOWED_CMD_PREFIXES = (
    '/usr/sbin/',
    '/usr/bin/',
    '/sbin/',
    '/bin/',
    'systemctl ',
    'service ',
)


def validate_setting_value(key, value):
    if key in COMMAND_SETTINGS:
        if not value.startswith(ALLOWED_CMD_PREFIXES):
            return False, 'Invalid command path for setting: ' + key
        dangerous = [';', '&&', '||', '|', '`', '$', '\n', '\r']
        for ch in dangerous:
            if ch in value:
                return False, 'Disallowed characters in command setting: ' + key
    return True, ''


@app.route('/admin/configuration/update', methods=['POST'])
@settings_permission_required
def update_configuration():
    part = request.form.get('part', '')
    settings = Setting.query.order_by(Setting.group, Setting.varname).all()
    errors = []
    for s in settings:
        field_name = f'{s.group}_{s.varname}'
        if part and s.group != part:
            continue
        if field_name in request.form:
            new_value = request.form[field_name]
            key = f'{s.group}.{s.varname}'
            ok, msg = validate_setting_value(key, new_value)
            if not ok:
                errors.append(msg)
            else:
                s.value = new_value
    if errors:
        flash('Validation failed: ' + '; '.join(errors), 'danger')
    else:
        db.session.commit()
        flash('Settings saved.', 'success')
    return redirect(url_for('configuration'))


@app.route('/admin/configuration/dataio', methods=['GET', 'POST'])
@settings_permission_required
def configuration_dataio():
    if request.method == 'POST':
        action = request.form.get('action', '')
        if action == 'export':
            return _export_settings()
        elif action == 'import':
            return _handle_import()
    return render_template('dataio.html')


def _export_settings():
    settings = Setting.query.all()
    data = {}
    for s in settings:
        key = f'{s.group}.{s.varname}'
        if key not in NO_EXPORT_SETTINGS:
            data[key] = s.value
    data['_checksum'] = hashlib.sha1(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()
    output = json.dumps(data, indent=2, ensure_ascii=False)
    buf = BytesIO(output.encode('utf-8'))
    return send_file(buf, mimetype='application/json',
                     as_attachment=True,
                     download_name='panel_settings.json')


def _handle_import():
    upload = request.files.get('config_file')
    if not upload or upload.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('configuration_dataio'))

    try:
        raw = upload.read().decode('utf-8')
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        flash('Invalid JSON file.', 'danger')
        return redirect(url_for('configuration_dataio'))

    if not isinstance(data, dict):
        flash('Invalid configuration format.', 'danger')
        return redirect(url_for('configuration_dataio'))

    checksum = data.pop('_checksum', None)
    version = data.get('panel.version')
    db_version = data.get('panel.db_version')

    if not version or not db_version:
        flash('Missing required metadata (version/db_version).', 'danger')
        return redirect(url_for('configuration_dataio'))

    data.pop('panel.version', None)
    data.pop('panel.db_version', None)

    imported = 0
    for key, value in data.items():
        parts = key.split('.', 1)
        if len(parts) != 2:
            continue
        group, varname = parts
        existing = Setting.query.filter_by(group=group, varname=varname).first()
        if existing:
            existing.value = str(value)
            imported += 1

    db.session.commit()
    flash(f'Configuration imported successfully ({imported} settings updated).', 'success')
    return redirect(url_for('configuration'))


@app.route('/admin/configuration/apply', methods=['POST'])
@settings_permission_required
def apply_configuration():
    results = apply_service_config()
    task = CronTask(task_type=1, data=json.dumps(results))
    db.session.add(task)
    db.session.commit()
    return jsonify({'status': 'ok', 'results': results})


@app.route('/admin/tasks')
@login_required
def tasks():
    all_tasks = CronTask.query.order_by(CronTask.id.desc()).limit(50).all()
    return render_template('tasks.html', tasks=all_tasks)


@app.route('/ping')
def health():
    return 'OK', 200


def init_db():
    db.create_all()

    if Admin.query.count() == 0:
        admin = Admin(username='admin', can_change_settings=True)
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()

    if Setting.query.count() == 0:
        for group, settings in DEFAULT_SETTINGS.items():
            for varname, value in settings.items():
                s = Setting(group=group, varname=varname, value=value)
                db.session.add(s)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5003)
