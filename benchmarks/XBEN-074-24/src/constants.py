# Application constants

APP_NAME = "ContentPress"
APP_VERSION = "2.4.1"

# Content type definitions
CONTENT_TYPES = {
    'article': {
        'name': 'Article',
        'fields': ['title', 'body', 'excerpt'],
        'supports_richtext': True
    },
    'page': {
        'name': 'Page',
        'fields': ['title', 'body'],
        'supports_richtext': True
    }
}

# Image routes (legacy)
IMAGE_ROUTES = {
    "default": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    }
}
