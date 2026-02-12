import os
import json
import subprocess
import hashlib
import functools
from datetime import datetime

from flask import (
    Flask, request, jsonify, render_template, redirect,
    url_for, session, flash, send_file, Response
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///froxlor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max upload

db = SQLAlchemy(app)


# --- Models ---

class Admin(db.Model):
    __tablename__ = 'panel_admins'
    adminid = db.Column(db.Integer, primary_key=True)
    loginname = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), default='')
    email = db.Column(db.String(255), default='')
    change_serversettings = db.Column(db.Integer, default=0)
    customers = db.Column(db.Integer, default=0)
    domains = db.Column(db.Integer, default=0)
    lastlogin_succ = db.Column(db.String(50), default='')


class Setting(db.Model):
    __tablename__ = 'panel_settings'
    settingid = db.Column(db.Integer, primary_key=True)
    settinggroup = db.Column(db.String(100), nullable=False)
    varname = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text, default='')

    @property
    def full_key(self):
        return f"{self.settinggroup}.{self.varname}"


class Domain(db.Model):
    __tablename__ = 'panel_domains'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    customerid = db.Column(db.Integer, default=0)
    adminid = db.Column(db.Integer, default=0)
    documentroot = db.Column(db.String(500), default='')
    ssl = db.Column(db.Integer, default=0)
    created = db.Column(db.String(50), default='')


class Customer(db.Model):
    __tablename__ = 'panel_customers'
    customerid = db.Column(db.Integer, primary_key=True)
    loginname = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), default='')
    email = db.Column(db.String(255), default='')
    adminid = db.Column(db.Integer, default=0)
    diskspace = db.Column(db.Integer, default=0)
    traffic = db.Column(db.Integer, default=0)


class FtpUser(db.Model):
    __tablename__ = 'ftp_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    customerid = db.Column(db.Integer, default=0)
    homedir = db.Column(db.String(500), default='')


class CronjobRun(db.Model):
    __tablename__ = 'cronjobs_run'
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(255), default='')
    lastrun = db.Column(db.String(50), default='')
    interval_value = db.Column(db.Integer, default=300)
    isactive = db.Column(db.Integer, default=1)


# --- Auth helpers ---

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


def serversettings_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        admin = Admin.query.get(session['admin_id'])
        if not admin or admin.change_serversettings != 1:
            flash('Insufficient privileges.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapper


# --- Helpers ---

def get_setting(group, varname):
    s = Setting.query.filter_by(settinggroup=group, varname=varname).first()
    return s.value if s else ''


def set_setting(group, varname, value):
    s = Setting.query.filter_by(settinggroup=group, varname=varname).first()
    if s:
        s.value = value
    else:
        s = Setting(settinggroup=group, varname=varname, value=value)
        db.session.add(s)
    db.session.commit()


# --- Routes ---

@app.route('/health')
def health():
    return 'OK', 200


@app.route('/')
def index():
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        loginname = request.form.get('loginname', '')
        password = request.form.get('password', '')
        admin = Admin.query.filter_by(
            loginname=loginname,
            password=hash_password(password)
        ).first()
        if admin:
            session['admin_id'] = admin.adminid
            session['loginname'] = admin.loginname
            admin.lastlogin_succ = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.session.commit()
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
    customer_count = Customer.query.count()
    ftp_count = FtpUser.query.count()
    hostname = get_setting('system', 'hostname')
    return render_template('dashboard.html',
                           admin=admin,
                           domain_count=domain_count,
                           customer_count=customer_count,
                           ftp_count=ftp_count,
                           hostname=hostname)


@app.route('/admin/domains')
@login_required
def domains():
    all_domains = Domain.query.all()
    return render_template('domains.html', domains=all_domains)


@app.route('/admin/customers')
@login_required
def customers():
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers)


@app.route('/admin/settings', methods=['GET'])
@serversettings_required
def admin_settings():
    settings = Setting.query.order_by(Setting.settinggroup, Setting.varname).all()
    grouped = {}
    for s in settings:
        grouped.setdefault(s.settinggroup, []).append(s)
    return render_template('settings.html', grouped_settings=grouped)


@app.route('/admin/settings/update', methods=['POST'])
@serversettings_required
def settings_update():
    for key, value in request.form.items():
        if '.' in key:
            group, varname = key.split('.', 1)
            set_setting(group, varname, value)
    flash('Settings updated.', 'success')
    return redirect(url_for('admin_settings'))


@app.route('/admin/settings/importexport', methods=['GET'])
@serversettings_required
def settings_importexport():
    return render_template('importexport.html')


@app.route('/admin/settings/export', methods=['GET'])
@serversettings_required
def settings_export():
    settings = Setting.query.all()
    export_data = {}
    for s in settings:
        export_data[s.full_key] = s.value
    payload = json.dumps(export_data, indent=2)
    return Response(
        payload,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=froxlor_settings.json'}
    )


@app.route('/admin/settings/import', methods=['POST'])
@serversettings_required
def settings_import():
    """
    Import settings from a JSON file.
    Accepts a file upload (import_file) containing key-value pairs
    where keys are in 'group.varname' format.
    """
    if 'import_file' not in request.files:
        flash('No file provided.', 'danger')
        return redirect(url_for('settings_importexport'))

    f = request.files['import_file']
    if f.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('settings_importexport'))

    try:
        raw = f.read().decode('utf-8')
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        flash('Invalid JSON file.', 'danger')
        return redirect(url_for('settings_importexport'))

    if not isinstance(data, dict):
        flash('Settings file must contain a JSON object.', 'danger')
        return redirect(url_for('settings_importexport'))

    count = 0
    for key, value in data.items():
        if '.' not in key:
            continue
        group, varname = key.split('.', 1)
        set_setting(group, varname, str(value))
        count += 1

    flash(f'Successfully imported {count} settings.', 'success')
    return redirect(url_for('admin_settings'))


@app.route('/admin/settings/rebuildconf', methods=['POST'])
@serversettings_required
def rebuild_config():
    """
    Trigger a configuration rebuild by executing the configured
    webserver reload and related system commands.
    """
    results = []

    # Execute configured service commands
    commands_to_run = [
        ('system', 'apachereload_command', 'Apache/Nginx Reload'),
        ('system', 'bindreload_command', 'DNS Reload'),
    ]

    for group, varname, label in commands_to_run:
        cmd = get_setting(group, varname)
        if cmd and cmd.strip():
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=10
                )
                status = 'OK' if result.returncode == 0 else 'FAILED'
                output = result.stdout.strip() or result.stderr.strip()
                results.append({
                    'label': label,
                    'command': cmd,
                    'status': status,
                    'output': output
                })
            except subprocess.TimeoutExpired:
                results.append({
                    'label': label,
                    'command': cmd,
                    'status': 'TIMEOUT',
                    'output': 'Command timed out'
                })
            except Exception as e:
                results.append({
                    'label': label,
                    'command': cmd,
                    'status': 'ERROR',
                    'output': str(e)
                })

    return render_template('rebuild_result.html', results=results)


@app.route('/admin/phpinfo')
@login_required
def phpinfo():
    """System information page"""
    import platform
    info = {
        'hostname': get_setting('system', 'hostname'),
        'ipaddress': get_setting('system', 'ipaddress'),
        'webserver': get_setting('system', 'webserver'),
        'python_version': platform.python_version(),
        'platform': platform.platform(),
    }
    return render_template('sysinfo.html', info=info)


# --- Database initialization ---

def init_db():
    db.create_all()

    # Create admin if none exists
    if Admin.query.count() == 0:
        admin = Admin(
            loginname='admin',
            password=hash_password('admin'),
            name='Main Administrator',
            email='admin@froxlor.local',
            change_serversettings=1,
            customers=0,
            domains=0
        )
        db.session.add(admin)

    # Initialize default settings if empty
    if Setting.query.count() == 0:
        defaults = {
            'system.hostname': 'srv01.froxlor.local',
            'system.ipaddress': '10.0.0.1',
            'system.webserver': 'apache2',
            'system.apachereload_command': '/usr/sbin/service apache2 reload',
            'system.bindreload_command': '/usr/sbin/service bind9 reload',
            'system.documentroot_prefix': '/var/customers/webs/',
            'system.logfiles_directory': '/var/customers/logs/',
            'system.mod_fcgid': '1',
            'system.backup_dir': '/var/customers/backups/',
            'system.vmail_homedir': '/var/customers/mail/',
            'system.default_vhostconf': '',
            'panel.frontend': 'froxlor',
            'panel.standardlanguage': 'English',
            'panel.paging': '20',
            'panel.natsorting': '1',
            'panel.no_robots': '1',
            'login.maxloginattempts': '3',
            'login.deactivatetime': '900',
            'customer.ftps': '5',
            'customer.emails': '10',
            'customer.subdomains': '15',
            'customer.mysqls': '5',
            'dkim.use_dkim': '0',
            'antispam.activated': '0',
            'ssl.use_ssl': '1',
            'ssl.ssl_cert_file': '/etc/ssl/froxlor/froxlor.pem',
            'ssl.ssl_key_file': '/etc/ssl/froxlor/froxlor.key',
        }
        for key, value in defaults.items():
            group, varname = key.split('.', 1)
            db.session.add(Setting(settinggroup=group, varname=varname, value=value))

    # Sample data
    if Domain.query.count() == 0:
        domains_data = [
            ('froxlor.local', 1, 1, '/var/www/froxlor', 1),
            ('example.com', 1, 1, '/var/customers/webs/example.com', 1),
            ('testsite.org', 2, 1, '/var/customers/webs/testsite.org', 0),
        ]
        for d, cid, aid, docroot, ssl in domains_data:
            db.session.add(Domain(
                domain=d, customerid=cid, adminid=aid,
                documentroot=docroot, ssl=ssl,
                created=datetime.now().strftime('%Y-%m-%d')
            ))

    if Customer.query.count() == 0:
        customers_data = [
            ('web1', 'John Doe', 'john@example.com', 1, 1048576, 10737418240),
            ('web2', 'Jane Smith', 'jane@testsite.org', 1, 524288, 5368709120),
        ]
        for ln, name, email, aid, disk, traffic in customers_data:
            db.session.add(Customer(
                loginname=ln, name=name, email=email,
                adminid=aid, diskspace=disk, traffic=traffic
            ))

    if FtpUser.query.count() == 0:
        db.session.add(FtpUser(username='web1ftp1', customerid=1, homedir='/var/customers/webs/example.com'))
        db.session.add(FtpUser(username='web2ftp1', customerid=2, homedir='/var/customers/webs/testsite.org'))

    if CronjobRun.query.count() == 0:
        crons = [
            ('froxlor/cron/tasks', 300, 1),
            ('froxlor/cron/traffic', 86400, 1),
            ('froxlor/cron/mailboxsize', 21600, 1),
        ]
        for mod, intv, active in crons:
            db.session.add(CronjobRun(
                module=mod, interval_value=intv, isactive=active,
                lastrun=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5003, debug=False)
