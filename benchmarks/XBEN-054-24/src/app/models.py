import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Role(db.Model):
    __tablename__ = "ab_role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return self.name


user_role = db.Table(
    "ab_user_role",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("ab_user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("ab_role.id")),
)


class User(db.Model):
    __tablename__ = "ab_user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256))
    email = db.Column(db.String(320), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    login_count = db.Column(db.Integer, default=0)
    fail_login_count = db.Column(db.Integer, default=0)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    changed_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    roles = db.relationship("Role", secondary=user_role, backref="users")

    @property
    def is_active(self):
        return self.active

    def __repr__(self):
        return self.username


class Permission(db.Model):
    __tablename__ = "ab_permission"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class ViewMenu(db.Model):
    __tablename__ = "ab_view_menu"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)


class PermissionView(db.Model):
    __tablename__ = "ab_permission_view"
    id = db.Column(db.Integer, primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey("ab_permission.id"))
    view_menu_id = db.Column(db.Integer, db.ForeignKey("ab_view_menu.id"))
    permission = db.relationship("Permission")
    view_menu = db.relationship("ViewMenu")


class SystemConfig(db.Model):
    __tablename__ = "ab_system_config"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
