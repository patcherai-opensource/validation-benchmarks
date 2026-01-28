from mongoengine import Document, StringField, ListField

class WikiDocument(Document):
    title = StringField(required=True)
    space = StringField(required=True)
    content = StringField(required=True)
    author = StringField(required=True)
    visibility = StringField(default='public')  # 'public' or 'private'
    reference = StringField()  # Document reference like "Main.WebHome"
    doc_type = StringField(default='DOCUMENT')
    related_links = ListField(StringField())
