from flask_sqlalchemy import SQLAlchemy
import datetime

from app.db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='operator')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class ManagedNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    group_name = db.Column(db.String(100), nullable=False, default='ungrouped')
    ssh_port = db.Column(db.Integer, default=22)
    status = db.Column(db.String(20), default='unknown')
    last_seen = db.Column(db.DateTime)


class TaskResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_hostname = db.Column(db.String(255), nullable=False)
    task_name = db.Column(db.String(255), nullable=False)
    module_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    stdout = db.Column(db.Text, default='')
    stderr = db.Column(db.Text, default='')
    facts = db.Column(db.Text, default='{}')
    msg = db.Column(db.Text, default='')
    executed_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Playbook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default='')
    content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_run = db.Column(db.DateTime)
