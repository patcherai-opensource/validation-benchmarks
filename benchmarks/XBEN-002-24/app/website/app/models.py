from flask_sqlalchemy import SQLAlchemy

from app.db import db


# Association table for user-group membership
user_groups = db.Table('user_groups',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('wiki_group.id'), primary_key=True)
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    groups = db.relationship('WikiGroup', secondary=user_groups, back_populates='members')

    def has_view_permission(self, document):
        """Check if user has VIEW permission on a document."""
        if document.space and document.space.is_public:
            return True
        if document.space:
            for group in self.groups:
                if group in document.space.allowed_groups:
                    return True
        return False


class WikiGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500))

    members = db.relationship('User', secondary=user_groups, back_populates='groups')


# Association table for space-group permissions
space_permissions = db.Table('space_permissions',
    db.Column('space_id', db.Integer, db.ForeignKey('wiki_space.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('wiki_group.id'), primary_key=True)
)


class WikiSpace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500))
    is_public = db.Column(db.Boolean, default=True, nullable=False)

    documents = db.relationship('WikiDocument', back_populates='space')
    allowed_groups = db.relationship('WikiGroup', secondary=space_permissions)


class WikiDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(500))
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), default='text/plain')
    creator_name = db.Column(db.String(100))
    created_at = db.Column(db.String(50))
    updated_at = db.Column(db.String(50))
    version = db.Column(db.String(20), default='1.0')
    tags = db.Column(db.String(500), default='')

    space_id = db.Column(db.Integer, db.ForeignKey('wiki_space.id'))
    space = db.relationship('WikiSpace', back_populates='documents')

    @property
    def reference(self):
        """Full document reference in Space.Name format."""
        if self.space:
            return f"{self.space.name}.{self.name}"
        return self.name

    @property
    def doc_type(self):
        return 'DOCUMENT'
