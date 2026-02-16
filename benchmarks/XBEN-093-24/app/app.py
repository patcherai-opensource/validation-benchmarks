import os
import json
import uuid
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, make_response, g
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from jinja2 import Environment

app = Flask(__name__)
app.secret_key = 'f8a2e4c6b9d1537e0f4a8c2d6b9e1f3a5c7d9e2b4f6a8c0d2e4f6a8b0c2d4e6'
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///privacyhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Roles
ROLE_VIEWER = 'viewer'
ROLE_CONTRIBUTOR = 'contributor'
ROLE_OWNER = 'owner'


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default=ROLE_VIEWER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PrivacyRequest(db.Model):
    __tablename__ = 'privacy_requests'
    id = db.Column(db.String(64), primary_key=True)
    requester_email = db.Column(db.String(200), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    denial_reason = db.Column(db.Text, nullable=True)


class NotificationLayout(db.Model):
    __tablename__ = 'notification_layouts'
    id = db.Column(db.Integer, primary_key=True)
    layout_type = db.Column(db.String(100), nullable=False, unique=True)
    label = db.Column(db.String(200), nullable=False)
    content_subject = db.Column(db.Text, nullable=False)
    content_body = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(200), nullable=False)
    detail = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class NotificationRecord(db.Model):
    __tablename__ = 'notification_records'
    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(200), nullable=False)
    layout_type = db.Column(db.String(100), nullable=False)
    rendered_subject = db.Column(db.Text, nullable=True)
    rendered_body = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='queued')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Default notification layouts
DEFAULT_LAYOUTS = {
    'request_received': {
        'label': 'Privacy request received',
        'content_subject': 'Your privacy request has been received',
        'content_body': 'Your privacy request has been received and is being reviewed. We will get back to you shortly.',
    },
    'request_approved': {
        'label': 'Privacy request approved',
        'content_subject': 'Your privacy request has been approved',
        'content_body': 'Your privacy request has been approved and is currently being processed.',
    },
    'request_denied': {
        'label': 'Privacy request denied',
        'content_subject': 'Your privacy request has been denied',
        'content_body': 'Your privacy request has been denied. Reason: {{denial_reason}}.',
    },
    'identity_verification': {
        'label': 'Subject identity verification',
        'content_subject': 'Your verification code is {{code}}',
        'content_body': 'Your privacy request verification code is {{code}}. Please return and enter the code to continue. This code will expire in {{minutes}} minutes.',
    },
    'deletion_complete': {
        'label': 'Erasure request completed',
        'content_subject': 'Your data has been deleted',
        'content_body': 'Your erasure request has been completed successfully.',
    },
    'access_complete': {
        'label': 'Access request completed',
        'content_subject': 'Your data is ready to be downloaded',
        'content_body': 'Your access request has been completed and can be downloaded at {{download_link}}. This link will expire in {{days}} days.',
    },
}


def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def compose_content(template_str, variables=None):
    """Render a notification layout string with the provided variables."""
    if variables is None:
        variables = {}
    jinja_env = Environment()
    template = jinja_env.from_string(template_str)
    return template.render(variables)


def _initialize_database():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin', role=ROLE_OWNER)
        db.session.add(admin)

    if not User.query.filter_by(username='analyst').first():
        analyst = User(username='analyst', password='analyst', role=ROLE_VIEWER)
        db.session.add(analyst)

    for layout_type, layout_data in DEFAULT_LAYOUTS.items():
        if not NotificationLayout.query.filter_by(layout_type=layout_type).first():
            layout = NotificationLayout(
                layout_type=layout_type,
                label=layout_data['label'],
                content_subject=layout_data['content_subject'],
                content_body=layout_data['content_body'],
            )
            db.session.add(layout)

    # seed some example privacy requests
    if not PrivacyRequest.query.first():
        sample_requests = [
            PrivacyRequest(
                id=str(uuid.uuid4()),
                requester_email='john.doe@example.com',
                request_type='access',
                status='pending',
            ),
            PrivacyRequest(
                id=str(uuid.uuid4()),
                requester_email='jane.smith@example.com',
                request_type='erasure',
                status='pending',
            ),
            PrivacyRequest(
                id=str(uuid.uuid4()),
                requester_email='bob.wilson@example.com',
                request_type='access',
                status='approved',
            ),
        ]
        for req in sample_requests:
            db.session.add(req)

    db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            audit = AuditLog(user_id=user.id, action='login', detail=f'User {username} logged in')
            db.session.add(audit)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    audit = AuditLog(user_id=current_user.id, action='logout', detail=f'User {current_user.username} logged out')
    db.session.add(audit)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    total_requests = PrivacyRequest.query.count()
    pending = PrivacyRequest.query.filter_by(status='pending').count()
    approved = PrivacyRequest.query.filter_by(status='approved').count()
    denied = PrivacyRequest.query.filter_by(status='denied').count()
    return render_template('dashboard.html',
                           total=total_requests,
                           pending=pending,
                           approved=approved,
                           denied=denied)


@app.route('/api/v1/privacy-requests', methods=['GET'])
@login_required
def list_privacy_requests():
    status_filter = request.args.get('status')
    query = PrivacyRequest.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    requests_list = query.order_by(PrivacyRequest.created_at.desc()).all()
    return jsonify([{
        'id': r.id,
        'requester_email': r.requester_email,
        'request_type': r.request_type,
        'status': r.status,
        'created_at': r.created_at.isoformat() if r.created_at else None,
        'denial_reason': r.denial_reason,
    } for r in requests_list])


@app.route('/api/v1/privacy-requests', methods=['POST'])
@login_required
@require_role(ROLE_OWNER, ROLE_CONTRIBUTOR)
def create_privacy_request():
    data = request.get_json()
    if not data or 'requester_email' not in data or 'request_type' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    if data['request_type'] not in ('access', 'erasure', 'rectification'):
        return jsonify({'error': 'Invalid request type'}), 400
    pr = PrivacyRequest(
        id=str(uuid.uuid4()),
        requester_email=data['requester_email'],
        request_type=data['request_type'],
    )
    db.session.add(pr)
    audit = AuditLog(user_id=current_user.id, action='create_request',
                     detail=f'Created privacy request {pr.id}')
    db.session.add(audit)
    db.session.commit()
    return jsonify({'id': pr.id, 'status': pr.status}), 201


@app.route('/api/v1/privacy-requests/<request_id>/approve', methods=['POST'])
@login_required
@require_role(ROLE_OWNER, ROLE_CONTRIBUTOR)
def approve_privacy_request(request_id):
    pr = PrivacyRequest.query.get(request_id)
    if not pr:
        return jsonify({'error': 'Request not found'}), 404
    if pr.status != 'pending':
        return jsonify({'error': 'Request is not in pending status'}), 400
    pr.status = 'approved'
    pr.reviewed_by = current_user.id
    audit = AuditLog(user_id=current_user.id, action='approve_request',
                     detail=f'Approved privacy request {pr.id}')
    db.session.add(audit)

    # Send approval notification
    layout = NotificationLayout.query.filter_by(layout_type='request_approved').first()
    if layout and layout.is_active:
        try:
            rendered_subject = compose_content(layout.content_subject)
            rendered_body = compose_content(layout.content_body)
            record = NotificationRecord(
                recipient_email=pr.requester_email,
                layout_type='request_approved',
                rendered_subject=rendered_subject,
                rendered_body=rendered_body,
                status='sent',
            )
            db.session.add(record)
        except Exception:
            pass

    db.session.commit()
    return jsonify({'id': pr.id, 'status': pr.status})


@app.route('/api/v1/privacy-requests/<request_id>/deny', methods=['POST'])
@login_required
@require_role(ROLE_OWNER, ROLE_CONTRIBUTOR)
def deny_privacy_request(request_id):
    pr = PrivacyRequest.query.get(request_id)
    if not pr:
        return jsonify({'error': 'Request not found'}), 404
    if pr.status != 'pending':
        return jsonify({'error': 'Request is not in pending status'}), 400

    data = request.get_json() or {}
    denial_reason = data.get('reason', 'No reason provided')

    pr.status = 'denied'
    pr.reviewed_by = current_user.id
    pr.denial_reason = denial_reason
    audit = AuditLog(user_id=current_user.id, action='deny_request',
                     detail=f'Denied privacy request {pr.id}')
    db.session.add(audit)

    # Send denial notification using the stored template
    notification_sent = False
    layout = NotificationLayout.query.filter_by(layout_type='request_denied').first()
    if layout and layout.is_active:
        try:
            variables = {'denial_reason': denial_reason}
            rendered_subject = compose_content(layout.content_subject, variables)
            rendered_body = compose_content(layout.content_body, variables)
            record = NotificationRecord(
                recipient_email=pr.requester_email,
                layout_type='request_denied',
                rendered_subject=rendered_subject,
                rendered_body=rendered_body,
                status='sent',
            )
            db.session.add(record)
            notification_sent = True
        except Exception:
            pass

    db.session.commit()
    return jsonify({
        'id': pr.id,
        'status': pr.status,
        'notification_sent': notification_sent,
    })


@app.route('/api/v1/notification-layouts', methods=['GET'])
@login_required
@require_role(ROLE_OWNER, ROLE_CONTRIBUTOR)
def list_notification_layouts():
    layouts = NotificationLayout.query.all()
    return jsonify([{
        'id': l.id,
        'layout_type': l.layout_type,
        'label': l.label,
        'content': {
            'subject': l.content_subject,
            'body': l.content_body,
        },
        'is_active': l.is_active,
        'updated_at': l.updated_at.isoformat() if l.updated_at else None,
    } for l in layouts])


@app.route('/api/v1/notification-layouts/<int:layout_id>', methods=['GET'])
@login_required
@require_role(ROLE_OWNER, ROLE_CONTRIBUTOR)
def get_notification_layout(layout_id):
    layout = NotificationLayout.query.get(layout_id)
    if not layout:
        return jsonify({'error': 'Layout not found'}), 404
    return jsonify({
        'id': layout.id,
        'layout_type': layout.layout_type,
        'label': layout.label,
        'content': {
            'subject': layout.content_subject,
            'body': layout.content_body,
        },
        'is_active': layout.is_active,
        'updated_at': layout.updated_at.isoformat() if layout.updated_at else None,
    })


@app.route('/api/v1/notification-layouts/<int:layout_id>', methods=['PUT'])
@login_required
@require_role(ROLE_OWNER, ROLE_CONTRIBUTOR)
def update_notification_layout(layout_id):
    layout = NotificationLayout.query.get(layout_id)
    if not layout:
        return jsonify({'error': 'Layout not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    content = data.get('content', {})
    if 'subject' in content:
        layout.content_subject = content['subject']
    if 'body' in content:
        layout.content_body = content['body']
    if 'is_active' in data:
        layout.is_active = data['is_active']

    layout.updated_by = current_user.id
    layout.updated_at = datetime.utcnow()

    audit = AuditLog(user_id=current_user.id, action='update_layout',
                     detail=f'Updated notification layout {layout.layout_type}')
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'id': layout.id,
        'layout_type': layout.layout_type,
        'label': layout.label,
        'content': {
            'subject': layout.content_subject,
            'body': layout.content_body,
        },
        'is_active': layout.is_active,
    })


@app.route('/api/v1/notification-layouts/defaults/<layout_type>', methods=['GET'])
@login_required
@require_role(ROLE_OWNER, ROLE_CONTRIBUTOR)
def get_default_layout(layout_type):
    default = DEFAULT_LAYOUTS.get(layout_type)
    if not default:
        return jsonify({'error': 'Unknown layout type'}), 404
    return jsonify({
        'layout_type': layout_type,
        'label': default['label'],
        'content': {
            'subject': default['content_subject'],
            'body': default['content_body'],
        },
    })


@app.route('/api/v1/notification-records', methods=['GET'])
@login_required
def list_notification_records():
    records = NotificationRecord.query.order_by(NotificationRecord.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': r.id,
        'recipient_email': r.recipient_email,
        'layout_type': r.layout_type,
        'rendered_subject': r.rendered_subject,
        'rendered_body': r.rendered_body,
        'status': r.status,
        'created_at': r.created_at.isoformat() if r.created_at else None,
    } for r in records])


@app.route('/privacy-requests')
@login_required
def privacy_requests_page():
    return render_template('privacy_requests.html')


@app.route('/notification-layouts')
@login_required
@require_role(ROLE_OWNER, ROLE_CONTRIBUTOR)
def notification_layouts_page():
    return render_template('notification_layouts.html')


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    with app.app_context():
        _initialize_database()
    app.run(host='0.0.0.0', port=5003, debug=False)
