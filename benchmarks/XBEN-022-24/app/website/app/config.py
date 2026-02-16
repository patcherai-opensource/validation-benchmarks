import os


class SiteConfig:
    """
    Hierarchical site configuration object.
    Provides dot-notation access to nested configuration values.
    Configuration is exposed to templates for theming and customization.
    """

    def __init__(self):
        self._data = {
            'site': {
                'title': 'Flavor CMS',
                'description': 'A lightweight content management system',
                'author': 'Admin',
                'default_lang': 'en',
            },
            'system': {
                'pages': {
                    'theme': 'flavor',
                    'markdown': True,
                    'process_twig': True,
                    'dateformat': {
                        'long': '%B %d, %Y'
                    }
                },
                'twig': {
                    'cache': False,
                    'debug': False,
                    'autoescape': False,
                    'safe_functions': [],
                    'safe_filters': [],
                    'undefined_functions': False,
                    'undefined_filters': False
                },
                'cache': {
                    'enabled': False,
                    'lifetime': 604800
                },
                'assets': {
                    'css_pipeline': False,
                    'js_pipeline': False
                },
                'strict_mode': {
                    'twig_compat': True
                }
            },
            'theme': {
                'name': 'flavor-default',
                'version': '1.0.0'
            }
        }

    def get(self, key, default=None):
        """Get a configuration value using dot notation."""
        keys = key.split('.')
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key, value):
        """Set a configuration value using dot notation."""
        keys = key.split('.')
        data = self._data
        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value

    def __repr__(self):
        return f'<SiteConfig>'


# Singleton configuration instance
site_config = SiteConfig()
