from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app.db import db


class Operator(db.Model):
    __tablename__ = 'operators'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ManagedNode(db.Model):
    __tablename__ = 'managed_nodes'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    node_group = db.Column(db.String(100), nullable=False, default='default')
    os_info = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending')
    last_checkin = db.Column(db.DateTime, nullable=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)


class TaskResult(db.Model):
    __tablename__ = 'task_results'
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('managed_nodes.id'), nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    module_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    output_data = db.Column(db.Text, nullable=True)
    error_msg = db.Column(db.Text, nullable=True)
    changed = db.Column(db.Boolean, default=False)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)

    node = db.relationship('ManagedNode', backref=db.backref('task_results', lazy=True))


class NodeFact(db.Model):
    __tablename__ = 'node_facts'
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('managed_nodes.id'), nullable=False)
    fact_key = db.Column(db.String(200), nullable=False)
    fact_value = db.Column(db.Text, nullable=False)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)

    node = db.relationship('ManagedNode', backref=db.backref('facts', lazy=True))
