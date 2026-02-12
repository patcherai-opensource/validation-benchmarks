import os
import json
import logging
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, abort, g
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from jinja2 import Environment
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fides.api")

app = Flask(__name__)
app.secret_key = "b3f9a7c2e1d84f5b9c0a3e7d6f2b8c4a1e5d9f0c3b7a2e6d8f4c0b5a9e3d7f"
app.permanent_session_lifetime = timedelta(hours=8)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fides.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


# ---------- models ----------------------------------------------------------

class FidesUser(db.Model, UserMixin):
    __tablename__ = "fidesuser"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(80), default="")
    last_name = db.Column(db.String(80), default="")
    role = db.Column(db.String(40), default="viewer")  # owner, contributor, viewer, approver
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class OAuthClient(db.Model):
    __tablename__ = "oauth_client"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(120), unique=True, nullable=False)
    client_secret = db.Column(db.String(256), nullable=False)
    scopes = db.Column(db.Text, default="")
    description = db.Column(db.String(256), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MessagingTemplate(db.Model):
    __tablename__ = "messaging_template"
    id = db.Column(db.Integer, primary_key=True)
    template_key = db.Column(db.String(120), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(256), default="")
    template_type = db.Column(db.String(60), default="email")
    is_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PrivacyRequest(db.Model):
    __tablename__ = "privacy_request"
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(120), unique=True, nullable=False)
    requester_email = db.Column(db.String(200), nullable=False)
    request_type = db.Column(db.String(60), default="access")  # access, erasure, consent
    status = db.Column(db.String(40), default="pending")  # pending, approved, denied, in_processing, complete, error
    denial_reason = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectionConfig(db.Model):
    __tablename__ = "connection_config"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False)
    connection_type = db.Column(db.String(60), default="postgres")
    name = db.Column(db.String(200), default="")
    disabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DataCategory(db.Model):
    __tablename__ = "data_category"
    id = db.Column(db.Integer, primary_key=True)
    fides_key = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    parent_key = db.Column(db.String(200), default="")


# ---------- message rendering (vulnerable) ----------------------------------

def _render(template_str, variables=None):
    """Render a Jinja2 template string with the given variables."""
    if variables is None:
        variables = {}
    jinja_env = Environment()
    template = jinja_env.from_string(template_str)
    return template.render(variables)


def dispatch_email(template_key, recipient, variables=None):
    """Look up the messaging template and render it for delivery."""
    tpl = MessagingTemplate.query.filter_by(template_key=template_key, is_enabled=True).first()
    if tpl is None:
        logger.warning("Messaging template '%s' not found or disabled", template_key)
        return None
    rendered_subject = _render(tpl.subject, variables)
    rendered_body = _render(tpl.content, variables)
    logger.info("Dispatching email to %s with subject: %s", recipient, rendered_subject)
    return {"to": recipient, "subject": rendered_subject, "body": rendered_body}


# ---------- auth helpers ----------------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(FidesUser, int(user_id))


def require_role(*roles):
    """Decorator to enforce role-based access on views."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def bearer_or_session_auth(required_scopes=None):
    """Decorator that allows Bearer token auth (OAuth client) or session auth."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                client = OAuthClient.query.filter_by(client_secret=token).first()
                if client is None:
                    return jsonify({"detail": "Invalid token"}), 401
                if required_scopes:
                    client_scopes = set(client.scopes.split(","))
                    for s in required_scopes:
                        if s not in client_scopes:
                            return jsonify({"detail": "Insufficient scope"}), 403
                g.oauth_client = client
                return f(*args, **kwargs)
            else:
                if not current_user.is_authenticated:
                    return jsonify({"detail": "Authentication required"}), 401
                if current_user.role not in ("owner", "contributor"):
                    return jsonify({"detail": "Insufficient privileges"}), 403
                return f(*args, **kwargs)
        return decorated_function
    return decorator


# ---------- seed data -------------------------------------------------------

def _seed():
    db.create_all()

    if not FidesUser.query.filter_by(username="admin").first():
        admin = FidesUser(username="admin", first_name="Admin", last_name="User", role="owner")
        admin.set_password("Fides2024!")
        db.session.add(admin)

    if not FidesUser.query.filter_by(username="contributor").first():
        contrib = FidesUser(username="contributor", first_name="Jane", last_name="Smith", role="contributor")
        contrib.set_password("Contrib2024!")
        db.session.add(contrib)

    if not FidesUser.query.filter_by(username="viewer").first():
        viewer = FidesUser(username="viewer", first_name="View", last_name="Only", role="viewer")
        viewer.set_password("Viewer2024!")
        db.session.add(viewer)

    if not OAuthClient.query.filter_by(client_id="fidesctl").first():
        oc = OAuthClient(
            client_id="fidesctl",
            client_secret="fides_oauth_secret_2024",
            scopes="messaging-template:read,privacy-request:read,connection:read",
            description="Default CLI client"
        )
        db.session.add(oc)

    # default messaging templates
    templates = [
        {
            "template_key": "privacy_request_denied",
            "subject": "Your privacy request has been denied",
            "content": "Dear {{requester_name}},\n\nYour privacy request (ID: {{request_id}}) has been denied.\n\nReason: {{denial_reason}}\n\nIf you have questions, please contact our privacy team.\n\nBest regards,\nPrivacy Team",
        },
        {
            "template_key": "privacy_request_approved",
            "subject": "Your privacy request has been approved",
            "content": "Dear {{requester_name}},\n\nYour privacy request (ID: {{request_id}}) has been approved and is being processed.\n\nYou will receive a follow-up email when the process is complete.\n\nBest regards,\nPrivacy Team",
        },
        {
            "template_key": "privacy_request_complete",
            "subject": "Your privacy request is complete",
            "content": "Dear {{requester_name}},\n\nYour privacy request (ID: {{request_id}}) has been completed.\n\nThank you for your patience.\n\nBest regards,\nPrivacy Team",
        },
        {
            "template_key": "subject_identity_verification",
            "subject": "Verify your identity",
            "content": "Dear {{requester_name}},\n\nPlease use the following code to verify your identity: {{verification_code}}\n\nThis code expires in 10 minutes.\n\nBest regards,\nPrivacy Team",
        },
    ]
    for tpl_data in templates:
        if not MessagingTemplate.query.filter_by(template_key=tpl_data["template_key"]).first():
            tpl = MessagingTemplate(**tpl_data)
            db.session.add(tpl)

    # seed some data categories
    categories = [
        ("user.name", "User Name", "User's first and last name"),
        ("user.email", "User Email", "User's email address"),
        ("user.device", "User Device", "Device identifiers"),
        ("system.operations", "System Operations", "System operational data"),
    ]
    for fk, name, desc in categories:
        if not DataCategory.query.filter_by(fides_key=fk).first():
            db.session.add(DataCategory(fides_key=fk, name=name, description=desc))

    # seed sample privacy requests
    sample_requests = [
        {
            "external_id": "pri_req_001",
            "requester_email": "alice@example.com",
            "request_type": "access",
            "status": "pending",
        },
        {
            "external_id": "pri_req_002",
            "requester_email": "bob@example.com",
            "request_type": "erasure",
            "status": "in_processing",
        },
    ]
    for pr_data in sample_requests:
        if not PrivacyRequest.query.filter_by(external_id=pr_data["external_id"]).first():
            db.session.add(PrivacyRequest(**pr_data))

    # seed connection configs
    if not ConnectionConfig.query.filter_by(key="postgres_main").first():
        db.session.add(ConnectionConfig(key="postgres_main", connection_type="postgres", name="Main PostgreSQL"))
    if not ConnectionConfig.query.filter_by(key="mongo_analytics").first():
        db.session.add(ConnectionConfig(key="mongo_analytics", connection_type="mongodb", name="Analytics MongoDB"))

    db.session.commit()


# ---------- Web UI routes ---------------------------------------------------

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": "2.43.0"}), 200


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = FidesUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            session.permanent = True
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        flash("Invalid username or password.", "error")
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    privacy_requests = PrivacyRequest.query.order_by(PrivacyRequest.created_at.desc()).all()
    return render_template("dashboard.html", privacy_requests=privacy_requests)


@app.route("/privacy-requests")
@login_required
def privacy_requests_list():
    requests = PrivacyRequest.query.order_by(PrivacyRequest.created_at.desc()).all()
    return render_template("privacy_requests.html", requests=requests)


@app.route("/privacy-requests/<request_id>/deny", methods=["POST"])
@login_required
@require_role("owner", "contributor", "approver")
def deny_privacy_request(request_id):
    pr = PrivacyRequest.query.filter_by(external_id=request_id).first_or_404()
    denial_reason = request.form.get("denial_reason", "Request does not meet policy requirements.")
    pr.status = "denied"
    pr.denial_reason = denial_reason
    pr.updated_at = datetime.utcnow()
    db.session.commit()

    # dispatch denial notification email using the messaging template
    variables = {
        "requester_name": pr.requester_email.split("@")[0].title(),
        "request_id": pr.external_id,
        "denial_reason": denial_reason,
    }
    result = dispatch_email("privacy_request_denied", pr.requester_email, variables)
    if result:
        flash("Privacy request denied. Notification sent.", "success")
        return render_template("email_preview.html", email=result, request_obj=pr)
    flash("Privacy request denied. Could not send notification.", "warning")
    return redirect(url_for("privacy_requests_list"))


@app.route("/privacy-requests/<request_id>/approve", methods=["POST"])
@login_required
@require_role("owner", "contributor", "approver")
def approve_privacy_request(request_id):
    pr = PrivacyRequest.query.filter_by(external_id=request_id).first_or_404()
    pr.status = "approved"
    pr.updated_at = datetime.utcnow()
    db.session.commit()

    variables = {
        "requester_name": pr.requester_email.split("@")[0].title(),
        "request_id": pr.external_id,
    }
    result = dispatch_email("privacy_request_approved", pr.requester_email, variables)
    if result:
        flash("Privacy request approved. Notification sent.", "success")
        return render_template("email_preview.html", email=result, request_obj=pr)
    flash("Privacy request approved. Could not send notification.", "warning")
    return redirect(url_for("privacy_requests_list"))


@app.route("/messaging-templates")
@login_required
@require_role("owner", "contributor")
def messaging_templates_list():
    templates = MessagingTemplate.query.order_by(MessagingTemplate.template_key).all()
    return render_template("messaging_templates.html", templates=templates)


@app.route("/messaging-templates/<int:template_id>/edit", methods=["GET", "POST"])
@login_required
@require_role("owner", "contributor")
def edit_messaging_template(template_id):
    tpl = MessagingTemplate.query.get_or_404(template_id)
    if request.method == "POST":
        tpl.subject = request.form.get("subject", tpl.subject)
        tpl.content = request.form.get("content", tpl.content)
        tpl.is_enabled = request.form.get("is_enabled") == "on"
        tpl.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Template updated successfully.", "success")
        return redirect(url_for("messaging_templates_list"))
    return render_template("edit_template.html", template=tpl)


@app.route("/connections")
@login_required
@require_role("owner", "contributor")
def connections_list():
    connections = ConnectionConfig.query.order_by(ConnectionConfig.key).all()
    return render_template("connections.html", connections=connections)


@app.route("/data-categories")
@login_required
def data_categories_list():
    categories = DataCategory.query.order_by(DataCategory.fides_key).all()
    return render_template("data_categories.html", categories=categories)


# ---------- API v1 endpoints -----------------------------------------------

@app.route("/api/v1/health")
def api_health():
    return jsonify({
        "webserver": "healthy",
        "version": "2.43.0",
        "database": "healthy",
    })


@app.route("/api/v1/messaging/templates/", methods=["GET"])
@bearer_or_session_auth(required_scopes=None)
def api_list_templates():
    templates = MessagingTemplate.query.all()
    result = []
    for t in templates:
        result.append({
            "id": t.id,
            "template_key": t.template_key,
            "subject": t.subject,
            "content": t.content,
            "template_type": t.template_type,
            "is_enabled": t.is_enabled,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        })
    return jsonify({"items": result, "total": len(result)})


@app.route("/api/v1/messaging/templates/<int:template_id>", methods=["GET"])
@bearer_or_session_auth(required_scopes=None)
def api_get_template(template_id):
    t = MessagingTemplate.query.get_or_404(template_id)
    return jsonify({
        "id": t.id,
        "template_key": t.template_key,
        "subject": t.subject,
        "content": t.content,
        "template_type": t.template_type,
        "is_enabled": t.is_enabled,
    })


@app.route("/api/v1/messaging/templates/<int:template_id>", methods=["PUT"])
@bearer_or_session_auth(required_scopes=["messaging-template:update"])
def api_update_template(template_id):
    t = MessagingTemplate.query.get_or_404(template_id)
    data = request.get_json(silent=True) or {}
    if "subject" in data:
        t.subject = data["subject"]
    if "content" in data:
        t.content = data["content"]
    if "is_enabled" in data:
        t.is_enabled = bool(data["is_enabled"])
    t.updated_at = datetime.utcnow()
    db.session.commit()
    logger.info("Template %d (%s) updated", t.id, t.template_key)
    return jsonify({
        "id": t.id,
        "template_key": t.template_key,
        "subject": t.subject,
        "content": t.content,
        "is_enabled": t.is_enabled,
        "updated_at": t.updated_at.isoformat(),
    })


@app.route("/api/v1/privacy-request/", methods=["GET"])
@bearer_or_session_auth(required_scopes=None)
def api_list_privacy_requests():
    requests = PrivacyRequest.query.order_by(PrivacyRequest.created_at.desc()).all()
    result = []
    for r in requests:
        result.append({
            "id": r.external_id,
            "requester_email": r.requester_email,
            "request_type": r.request_type,
            "status": r.status,
            "denial_reason": r.denial_reason,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return jsonify({"items": result, "total": len(result)})


@app.route("/api/v1/privacy-request/<request_id>/deny", methods=["POST"])
@bearer_or_session_auth(required_scopes=None)
def api_deny_privacy_request(request_id):
    pr = PrivacyRequest.query.filter_by(external_id=request_id).first()
    if pr is None:
        return jsonify({"detail": "Privacy request not found"}), 404
    data = request.get_json(silent=True) or {}
    denial_reason = data.get("denial_reason", "Request does not meet policy requirements.")
    pr.status = "denied"
    pr.denial_reason = denial_reason
    pr.updated_at = datetime.utcnow()
    db.session.commit()

    variables = {
        "requester_name": pr.requester_email.split("@")[0].title(),
        "request_id": pr.external_id,
        "denial_reason": denial_reason,
    }
    result = dispatch_email("privacy_request_denied", pr.requester_email, variables)
    return jsonify({
        "id": pr.external_id,
        "status": pr.status,
        "notification": result,
    })


@app.route("/api/v1/privacy-request/<request_id>/approve", methods=["POST"])
@bearer_or_session_auth(required_scopes=None)
def api_approve_privacy_request(request_id):
    pr = PrivacyRequest.query.filter_by(external_id=request_id).first()
    if pr is None:
        return jsonify({"detail": "Privacy request not found"}), 404
    pr.status = "approved"
    pr.updated_at = datetime.utcnow()
    db.session.commit()

    variables = {
        "requester_name": pr.requester_email.split("@")[0].title(),
        "request_id": pr.external_id,
    }
    result = dispatch_email("privacy_request_approved", pr.requester_email, variables)
    return jsonify({
        "id": pr.external_id,
        "status": pr.status,
        "notification": result,
    })


@app.route("/api/v1/connection/", methods=["GET"])
@bearer_or_session_auth(required_scopes=None)
def api_list_connections():
    conns = ConnectionConfig.query.all()
    result = []
    for c in conns:
        result.append({
            "key": c.key,
            "connection_type": c.connection_type,
            "name": c.name,
            "disabled": c.disabled,
        })
    return jsonify({"items": result, "total": len(result)})


@app.route("/api/v1/data_category/", methods=["GET"])
@bearer_or_session_auth(required_scopes=None)
def api_list_data_categories():
    cats = DataCategory.query.all()
    result = []
    for c in cats:
        result.append({
            "fides_key": c.fides_key,
            "name": c.name,
            "description": c.description,
            "parent_key": c.parent_key,
        })
    return jsonify({"items": result, "total": len(result)})


# ---------- error handlers --------------------------------------------------

@app.errorhandler(401)
def unauthorized(e):
    if request.path.startswith("/api/"):
        return jsonify({"detail": "Authentication required"}), 401
    return redirect(url_for("login"))


@app.errorhandler(403)
def forbidden(e):
    if request.path.startswith("/api/"):
        return jsonify({"detail": "Insufficient privileges"}), 403
    flash("You do not have permission to access this resource.", "error")
    return redirect(url_for("dashboard"))


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"detail": "Not found"}), 404
    return render_template("404.html"), 404


# ---------- entry point -----------------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        _seed()
    app.run(host="0.0.0.0", port=5003, debug=False)
