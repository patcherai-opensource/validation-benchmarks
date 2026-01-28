from mongoengine import Document, StringField, BooleanField, DictField, DateTimeField
from datetime import datetime

class Webhook(Document):
    name = StringField(required=True)
    url = StringField(required=True)
    status = StringField(default="active")
    config = DictField()
    flag = StringField()  # Only populated for admin webhook
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'webhooks'}

class SystemConfig(Document):
    key = StringField(required=True, unique=True)
    value = DictField()
    
    meta = {'collection': 'system_config'}
