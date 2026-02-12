from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app.db import db


class User(db.Model):
    __tablename__ = 't_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    nick_name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(128), nullable=True)
    user_type = db.Column(db.Integer, default=2)  # 1=admin, 2=user
    status = db.Column(db.Integer, default=1)  # 1=active, 0=locked
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_time = db.Column(db.DateTime, nullable=True)


class Application(db.Model):
    __tablename__ = 't_flink_app'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.String(128), nullable=False)
    app_type = db.Column(db.Integer, default=1)  # 1=StreamPark Flink, 2=Apache Flink, 3=StreamPark Spark
    execution_mode = db.Column(db.Integer, default=4)  # 4=yarn-application
    state = db.Column(db.Integer, default=0)  # 0=added, 1=starting, 7=running, 9=failed, 14=finished
    job_id = db.Column(db.String(64), nullable=True)
    cluster_id = db.Column(db.String(45), nullable=True)
    version_id = db.Column(db.Integer, nullable=True)
    resource_from = db.Column(db.Integer, nullable=True)
    jar = db.Column(db.String(256), nullable=True)
    main_class = db.Column(db.String(256), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), nullable=False)
    alert_id = db.Column(db.Integer, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)


class AlertConfig(db.Model):
    __tablename__ = 't_alert_config'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), nullable=False)
    alert_name = db.Column(db.String(128), nullable=False)
    alert_type = db.Column(db.Integer, default=4)  # 1=email, 2=dingtalk, 3=wechat, 4=http_callback
    http_callback_url = db.Column(db.String(512), nullable=True)
    http_callback_method = db.Column(db.String(10), default='POST')
    http_callback_header = db.Column(db.Text, nullable=True)
    http_callback_content_type = db.Column(db.String(64), default='application/json')
    http_callback_request_template = db.Column(db.Text, nullable=True)
    is_enabled = db.Column(db.Boolean, default=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AlertHistory(db.Model):
    __tablename__ = 't_alert_history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alert_config_id = db.Column(db.Integer, db.ForeignKey('t_alert_config.id'), nullable=False)
    title = db.Column(db.String(256), nullable=True)
    content = db.Column(db.Text, nullable=True)
    alert_status = db.Column(db.Integer, default=0)  # 0=pending, 1=success, 2=failed
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
