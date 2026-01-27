from mongoengine import Document as MongoDocument, StringField

class Document(MongoDocument):
    """Wiki document model"""
    title = StringField(required=True)
    content = StringField()
    space = StringField(required=True)  # Wiki space (namespace)
    author = StringField()
    visibility = StringField(default='public')  # 'public' or 'private'
    created_at = StringField()
    
    meta = {'collection': 'documents'}
