import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Role(db.Model):
    __tablename__ = "ab_role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return self.name


assoc_user_role = db.Table(
    "ab_user_role",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("ab_user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("ab_role.id")),
)


class User(UserMixin, db.Model):
    __tablename__ = "ab_user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256))
    email = db.Column(db.String(120), unique=True)
    active = db.Column(db.Boolean, default=True)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    changed_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    login_count = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)
    fail_login_count = db.Column(db.Integer, default=0)

    roles = db.relationship("Role", secondary=assoc_user_role, backref="user")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if self.password:
            return check_password_hash(self.password, password)
        return False

    @property
    def is_active(self):
        return self.active

    def __repr__(self):
        return self.username


class ViewMenu(db.Model):
    __tablename__ = "ab_view_menu"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)


class Permission(db.Model):
    __tablename__ = "ab_permission"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class PermissionView(db.Model):
    __tablename__ = "ab_permission_view"
    id = db.Column(db.Integer, primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey("ab_permission.id"))
    view_menu_id = db.Column(db.Integer, db.ForeignKey("ab_view_menu.id"))
    permission = db.relationship("Permission")
    view_menu = db.relationship("ViewMenu")


class PermissionViewRole(db.Model):
    __tablename__ = "ab_permission_view_role"
    id = db.Column(db.Integer, primary_key=True)
    permission_view_id = db.Column(
        db.Integer, db.ForeignKey("ab_permission_view.id")
    )
    role_id = db.Column(db.Integer, db.ForeignKey("ab_role.id"))
    permission_view = db.relationship("PermissionView")
    role = db.relationship("Role")


class RegisterUser(db.Model):
    __tablename__ = "ab_register_user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256))
    email = db.Column(db.String(120))
    registration_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    registration_hash = db.Column(db.String(256))
