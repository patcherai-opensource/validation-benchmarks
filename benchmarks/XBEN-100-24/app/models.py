from mongoengine import Document, StringField, BooleanField, ListField, IntField
from passlib.hash import bcrypt


class User(Document):
    meta = {"collection": "users"}
    email = StringField(required=True, unique=True)
    hashed_password = StringField(required=True)
    full_name = StringField()
    role = StringField(default="basic", choices=["admin", "curator", "basic"])
    is_active = BooleanField(default=True)

    def verify_password(self, password):
        return bcrypt.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password):
        return bcrypt.hash(password)

    def to_dict(self, include_sensitive=False):
        data = {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
        }
        return data


class UserGroup(Document):
    meta = {"collection": "user_groups"}
    name = StringField(required=True)
    description = StringField(default="")
    user_ids = ListField(StringField())
    curator_ids = ListField(StringField())
    cc_pair_ids = ListField(IntField())
    is_active = BooleanField(default=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "user_ids": self.user_ids,
            "curator_ids": self.curator_ids,
            "cc_pair_ids": self.cc_pair_ids,
            "is_active": self.is_active,
        }


class ConnectorCredentialPair(Document):
    meta = {"collection": "cc_pairs"}
    pair_id = IntField(required=True, unique=True)
    connector_name = StringField(required=True)
    credential_name = StringField(default="")
    is_public = BooleanField(default=False)

    def to_dict(self):
        return {
            "id": str(self.id),
            "pair_id": self.pair_id,
            "connector_name": self.connector_name,
            "credential_name": self.credential_name,
            "is_public": self.is_public,
        }


class Document_(Document):
    meta = {"collection": "documents"}
    title = StringField(required=True)
    content = StringField(required=True)
    source_connector = StringField()
    cc_pair_id = IntField()
    access_group_ids = ListField(StringField())
    is_public = BooleanField(default=False)

    def to_dict(self, include_content=True):
        data = {
            "id": str(self.id),
            "title": self.title,
            "source_connector": self.source_connector,
            "cc_pair_id": self.cc_pair_id,
            "access_group_ids": self.access_group_ids,
            "is_public": self.is_public,
        }
        if include_content:
            data["content"] = self.content
        return data
