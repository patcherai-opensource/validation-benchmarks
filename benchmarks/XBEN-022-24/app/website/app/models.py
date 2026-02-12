from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app.db import db


class User(db.Model):
    __tablename__ = 't_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    nick_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    user_type = db.Column(db.Integer, default=2)  # 1=admin, 2=user
    status = db.Column(db.Integer, default=1)  # 1=active, 0=locked
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_time = db.Column(db.DateTime, nullable=True)
    avatar = db.Column(db.String(256), nullable=True, default='default.png')
    description = db.Column(db.String(256), nullable=True)


class Team(db.Model):
    __tablename__ = 't_team'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class FlinkApp(db.Model):
    __tablename__ = 't_flink_app'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('t_team.id'), nullable=False)
    app_name = db.Column(db.String(128), nullable=False)
    app_type = db.Column(db.Integer, default=1)  # 1=StreamPark Flink, 2=Apache Flink
    execution_mode = db.Column(db.Integer, default=1)  # 1=remote, 2=yarn, 4=k8s session
    state = db.Column(db.Integer, default=0)  # 0=added, 1=starting, 5=running, 9=failed
    launch = db.Column(db.Integer, default=1)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    alert_id = db.Column(db.Integer, db.ForeignKey('t_alert_config.id'), nullable=True)
    description = db.Column(db.String(256), nullable=True)


class AlertConfig(db.Model):
    __tablename__ = 't_alert_config'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), nullable=False)
    alert_name = db.Column(db.String(128), nullable=False)
    alert_type = db.Column(db.Integer, default=4)  # 1=email, 2=dingtalk, 3=wechat, 4=http_callback
    email_params = db.Column(db.Text, nullable=True)
    dingtalk_params = db.Column(db.Text, nullable=True)
    wechat_params = db.Column(db.Text, nullable=True)
    http_callback_params = db.Column(db.Text, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Variable(db.Model):
    __tablename__ = 't_variable'
    id = db.Column(db.Integer, primary_key=True)
    variable_code = db.Column(db.String(100), unique=True, nullable=False)
    variable_value = db.Column(db.String(512), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    desensitization = db.Column(db.Boolean, default=False)
