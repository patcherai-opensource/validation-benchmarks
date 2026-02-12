from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'wp_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, default='')
    display_name = db.Column(db.String(250), nullable=False, default='')
    registered = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def role(self):
        meta = UserMeta.query.filter_by(user_id=self.id, meta_key='wp_capabilities').first()
        if meta and 'administrator' in meta.meta_value:
            return 'administrator'
        return 'subscriber'


class UserMeta(db.Model):
    __tablename__ = 'wp_usermeta'

    umeta_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('wp_users.id'), nullable=False)
    meta_key = db.Column(db.String(255), nullable=False, default='')
    meta_value = db.Column(db.Text)

    user = db.relationship('User', backref=db.backref('meta', lazy=True))


class Project(db.Model):
    __tablename__ = 'pm_projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='active')
    created_by = db.Column(db.Integer, db.ForeignKey('wp_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = db.relationship('User', backref=db.backref('projects', lazy=True))


class ProjectUser(db.Model):
    __tablename__ = 'pm_project_users'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('pm_projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('wp_users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')

    project = db.relationship('Project', backref=db.backref('members', lazy=True))
    user = db.relationship('User', backref=db.backref('project_memberships', lazy=True))


class Task(db.Model):
    __tablename__ = 'pm_tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default='')
    project_id = db.Column(db.Integer, db.ForeignKey('pm_projects.id'), nullable=False)
    status = db.Column(db.String(20), default='incomplete')
    assigned_to = db.Column(db.Integer, db.ForeignKey('wp_users.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('wp_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship('Project', backref=db.backref('tasks', lazy=True))
    assignee = db.relationship('User', foreign_keys=[assigned_to])
    creator = db.relationship('User', foreign_keys=[created_by])


class TaskList(db.Model):
    __tablename__ = 'pm_task_lists'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('pm_projects.id'), nullable=False)
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', backref=db.backref('task_lists', lazy=True))


class Discussion(db.Model):
    __tablename__ = 'pm_discussions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default='')
    project_id = db.Column(db.Integer, db.ForeignKey('pm_projects.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('wp_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', backref=db.backref('discussions', lazy=True))
    creator = db.relationship('User', foreign_keys=[created_by])


class Setting(db.Model):
    __tablename__ = 'pm_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False, unique=True)
    value = db.Column(db.Text, default='')
