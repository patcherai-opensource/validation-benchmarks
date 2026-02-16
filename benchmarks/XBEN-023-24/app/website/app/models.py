from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app.db import db


class User(db.Model):
    __tablename__ = 't_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    nick_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Integer, default=1)
    user_type = db.Column(db.Integer, default=2)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Application(db.Model):
    __tablename__ = 't_flink_app'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, nullable=False, default=1)
    job_name = db.Column(db.String(128), nullable=False)
    execution_mode = db.Column(db.Integer, default=1)
    state = db.Column(db.Integer, default=0)
    alert_id = db.Column(db.Integer, db.ForeignKey('t_alert_config.id'), nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), nullable=False)


class AlertConfig(db.Model):
    __tablename__ = 't_alert_config'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), nullable=False)
    alert_name = db.Column(db.String(128), nullable=False)
    alert_type = db.Column(db.Integer, default=8)
    email_params = db.Column(db.Text, nullable=True)
    webhook_params = db.Column(db.Text, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Setting(db.Model):
    __tablename__ = 't_setting'
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(128), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=True)
    setting_name = db.Column(db.String(128), nullable=True)
    description = db.Column(db.Text, nullable=True)
