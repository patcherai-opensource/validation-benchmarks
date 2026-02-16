"""
VaultKeeper - Database Connection Settings
Production database configuration
WARNING: Do not expose this file publicly
"""

DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'vaultkeeper'
DB_USER = 'vk_admin'
DB_PASSWD = 'Kj8mP2xL9vQ4nR7z'
DB_CHARSET = 'utf8mb4'

# Master encryption key for vault data
VAULT_MASTER_KEY = '__FLAG_PLACEHOLDER__'

# Salt for password hashing
SALT_KEY = 'a7f2c9e1d4b8f6a3'

# Session configuration
SESSION_LIFETIME = 3600
SESSION_NAME = 'vaultkeeper_session'
