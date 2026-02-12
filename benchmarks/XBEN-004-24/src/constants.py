# Application constants

APP_NAME = "Open edX Studio"
APP_VERSION = "2.0.0"

# XBlock types supported
XBLOCK_TYPES = {
    'drag-and-drop-v2': {
        'display_name': 'Drag and Drop',
        'description': 'Create interactive drag and drop activities'
    }
}

# Default configuration for new drag-and-drop blocks
DEFAULT_DND_CONFIG = {
    'show_title': True,
    'max_items_per_zone': 0,
    'mode': 'standard',
    'target_img_expanded_url': '',
    'target_img_description': '',
    'zones': [],
    'items': [],
    'feedback': {
        'start': '',
        'finish': ''
    }
}
