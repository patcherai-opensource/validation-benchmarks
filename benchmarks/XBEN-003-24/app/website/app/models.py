from flask_sqlalchemy import SQLAlchemy

from app.db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='viewer')


class PipelineConnection(db.Model):
    __tablename__ = 'pipeline_connection'

    id = db.Column(db.Integer, primary_key=True)
    conn_id = db.Column(db.String(250), unique=True, nullable=False)
    conn_type = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    host = db.Column(db.String(500), nullable=True)
    schema_name = db.Column(db.String(500), nullable=True)
    login = db.Column(db.String(500), nullable=True)
    password = db.Column(db.String(500), nullable=True)
    port = db.Column(db.Integer, nullable=True)
    extra = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<PipelineConnection {self.conn_id}>'


class Pipeline(db.Model):
    __tablename__ = 'pipeline'

    id = db.Column(db.Integer, primary_key=True)
    pipeline_id = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    schedule = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    owner = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Pipeline {self.pipeline_id}>'
