from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    loan_term_months = db.Column(db.Integer, nullable=False)
    monthly_payment = db.Column(db.Float, nullable=False)
    image_profile_filename = db.Column(db.String(100), nullable=False)

class NotificationConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    config_name = db.Column(db.String(100), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # email, webhook, etc
    webhook_url = db.Column(db.String(255), nullable=True)
    request_template = db.Column(db.Text, nullable=True)  # Jinja2 template for webhook body
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

class SystemSecret(db.Model):
    __tablename__ = 'system_secrets'
    id = db.Column(db.Integer, primary_key=True)
    secret_key = db.Column(db.String(100), unique=True, nullable=False)
    secret_value = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
