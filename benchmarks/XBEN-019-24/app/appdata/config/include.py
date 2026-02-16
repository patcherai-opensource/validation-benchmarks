"""
VaultKeeper - Include Configuration
Defines core paths and required modules
"""
import os

VAULTKEEPER_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULTKEEPER_CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))

REQUIRED_MODULES = [
    'svc.Handler.auth_handler',
    'svc.Handler.vault_handler',
    'svc.Handler.folder_handler',
    'svc.Handler.user_handler',
    'svc.Schema.database',
    'svc.Schema.auth_model',
    'svc.Schema.vault_model',
    'svc.Schema.folder_model',
    'svc.Schema.user_model',
]

TEMPLATE_DIRS = [
    os.path.join(VAULTKEEPER_ROOT_PATH, 'modules'),
    os.path.join(VAULTKEEPER_ROOT_PATH, 'app', 'templates'),
]

STATIC_DIRS = [
    os.path.join(VAULTKEEPER_ROOT_PATH, 'app', 'static'),
]
