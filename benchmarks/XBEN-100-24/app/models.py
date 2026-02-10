from mongoengine import Document, StringField, BooleanField, IntField


class WikiDocument(Document):
    meta = {'collection': 'documents'}
    
    doc_id = StringField(required=True, unique=True)
    title = StringField(required=True)
    content = StringField()
    space = StringField(required=True)
    creator = StringField()
    is_private = BooleanField(default=False)
    view_count = IntField(default=0)
