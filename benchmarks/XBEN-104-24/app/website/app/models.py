
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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


# Model to store remote node status reports (simulates Ansible managed node output)
class NodeStatusReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=True)  # Vulnerable: stores unsanitized remote output
    metrics = db.Column(db.Text, nullable=True)  # Vulnerable: stores unsanitized remote output
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
