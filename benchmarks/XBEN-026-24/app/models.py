from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    # This is the sensitive field that should NOT be exposed - forgot password token
    forgot_password_token = db.Column(db.String(64), nullable=True)
    # Flag for admin users
    secret_data = db.Column(db.Text, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        self.forgot_password_token = secrets.token_hex(32)
        return self.forgot_password_token

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    app_id = db.Column(db.Integer, nullable=False, default=1)  # Simulates ToolJet app context
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # VULNERABILITY: eager=True causes all User fields to be loaded
    # This is the exact vulnerability from CVE-2022-3019
    # In ToolJet, this exposed forgotPasswordToken when fetching comments
    user = db.relationship('User', backref=db.backref('comments', lazy=True), lazy='joined')
    thread = db.relationship('Thread', backref=db.backref('comments', lazy=True))

    def to_dict(self):
        """Serialize comment with user data - VULNERABILITY: exposes all user fields"""
        return {
            'id': self.id,
            'content': self.content,
            'threadId': self.thread_id,
            'createdAt': str(self.created_at),
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'firstName': self.user.first_name,
                'lastName': self.user.last_name,
                'role': self.user.role,
                # VULNERABILITY: These sensitive fields are exposed due to eager loading
                'forgotPasswordToken': self.user.forgot_password_token,
            }
        }
