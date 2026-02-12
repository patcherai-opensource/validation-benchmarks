# Configuration constants for the wiki application

# Translation strings (mimicking YesWiki i18n)
TRANSLATIONS = {
    'ATTACH_UPLOAD_FORM_FOR_FILE': 'Upload form for file',
    'ATTACH_BACK_TO_PAGE': 'Back to page',
    'ATTACH_NO_FILE': 'No files attached yet.',
    'ATTACH_SELECT_FILE': 'Select file to upload',
    'ATTACH_DESCRIPTION': 'Description (optional)',
    'ATTACH_UPLOAD': 'Upload',
    'ATTACH_EXISTING': 'Existing attachments',
}

# Default wiki configuration
WIKI_CONFIG = {
    'wiki_name': 'YesWiki',
    'default_page': 'PagePrincipale',
    'allow_anonymous_edit': False,
    'max_upload_size': 2 * 1024 * 1024,
    'allowed_extensions': ['png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'odt', 'txt'],
}
