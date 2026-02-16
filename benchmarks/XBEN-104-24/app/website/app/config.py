class SiteConfig:
    """
    Hierarchical site configuration object.
    Supports dot-notation access (e.g., 'template.allowed_functions').
    Configuration values can be read and modified at runtime.
    """

    def __init__(self, initial=None):
        self._data = initial or {}

    def get(self, key, default=None):
        parts = key.split('.')
        current = self._data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def set(self, key, value):
        parts = key.split('.')
        current = self._data
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
        return ''

    def all(self):
        return self._data

    def __repr__(self):
        return '<SiteConfig>'


# Default site configuration
site_config = SiteConfig({
    'site': {
        'title': 'GravPages CMS',
        'description': 'A lightweight flat-file content management system',
        'author': 'Admin',
    },
    'pages': {
        'theme': 'default',
        'process': {
            'markdown': True,
            'twig': False,
        },
        'dateformat': {
            'short': '%Y-%m-%d',
            'long': '%B %d, %Y at %I:%M %p',
        },
    },
    'template': {
        'cache': False,
        'debug': False,
        'autoescape': True,
        'undefined_functions': False,
        'undefined_filters': False,
        'allowed_functions': [],
        'allowed_filters': [],
    },
    'system': {
        'cache': {
            'enabled': False,
            'driver': 'file',
        },
        'debug': False,
        'timezone': 'UTC',
    },
})
