from mongoengine import Document, StringField, BooleanField, ListField

class WikiDocument(Document):
    """
    Represents a wiki document similar to XWiki's document structure.
    """
    meta = {'collection': 'wiki_documents'}
    
    # Core document fields
    reference = StringField(required=True, unique=True)  # Document reference (used for access checks)
    title = StringField(required=True)
    content = StringField()  # Document content (may contain sensitive data)
    
    # Access control fields - these are used for authorization checks
    wiki = StringField(default="xwiki")  # Wiki identifier (used in access check)
    space = StringField()  # Document space (used in access check) 
    name = StringField()  # Document name
    
    # Visibility
    is_public = BooleanField(default=True)
    allowed_users = ListField(StringField())  # Users allowed to view this document
    
    # Additional metadata
    author = StringField()
    links = ListField(StringField())  # Links to other documents
