from flask_sqlalchemy import SQLAlchemy

from app.db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='viewer')


class Device(db.Model):
    device_id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(255), nullable=False)
    sys_name = db.Column(db.String(255), nullable=True)
    os = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Integer, nullable=False, default=1)
    uptime = db.Column(db.BigInteger, nullable=True)
    location = db.Column(db.String(255), nullable=True)

    ports = db.relationship('Port', backref='device')


class Port(db.Model):
    port_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.device_id'), nullable=False)
    if_descr = db.Column(db.String(255), nullable=True)
    if_alias = db.Column(db.String(255), nullable=True)
    if_type = db.Column(db.String(100), nullable=True)
    if_speed = db.Column(db.BigInteger, nullable=True)
    hw_address = db.Column(db.String(64), nullable=True)
    if_oper_status = db.Column(db.String(20), nullable=True, default='up')
    if_admin_status = db.Column(db.String(20), nullable=True, default='up')
    in_octets = db.Column(db.BigInteger, nullable=True, default=0)
    out_octets = db.Column(db.BigInteger, nullable=True, default=0)
    in_errors = db.Column(db.Integer, nullable=True, default=0)
    out_errors = db.Column(db.Integer, nullable=True, default=0)


class Ipv4Address(db.Model):
    ipv4_address_id = db.Column(db.Integer, primary_key=True)
    port_id = db.Column(db.Integer, db.ForeignKey('port.port_id'), nullable=False)
    ipv4_address = db.Column(db.String(64), nullable=False)
    ipv4_prefixlen = db.Column(db.Integer, nullable=True)

    port = db.relationship('Port', backref='ipv4_addresses')


class AlertRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(50), nullable=False, default='warning')
    device_id = db.Column(db.Integer, db.ForeignKey('device.device_id'), nullable=True)
    expression = db.Column(db.Text, nullable=True)
    enabled = db.Column(db.Integer, nullable=False, default=1)


class EventLog(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.device_id'), nullable=True)
    message = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), nullable=True)
    timestamp = db.Column(db.String(50), nullable=True)


class SystemConfig(db.Model):
    config_id = db.Column(db.Integer, primary_key=True)
    config_group = db.Column(db.String(100), nullable=False)
    config_name = db.Column(db.String(255), nullable=False)
    config_value = db.Column(db.Text, nullable=False)
