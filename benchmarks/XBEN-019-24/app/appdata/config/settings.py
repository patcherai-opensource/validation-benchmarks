"""
VaultKeeper - Application Settings
Core configuration constants and version info
"""

VK_VERSION = '3.0.9'
UPGRADE_MIN_DATE = "1688411345"
VK_TOOL_NAME = 'VaultKeeper'
VK_ONE_DAY_SECONDS = 86400
VK_ONE_WEEK_SECONDS = 604800
VK_ONE_MONTH_SECONDS = 2592000
VK_IMAGE_FILE_EXT = ['jpg', 'gif', 'png', 'jpeg', 'tiff', 'bmp']
VK_OFFICE_FILE_EXT = ['xls', 'xlsx', 'docx', 'doc', 'csv', 'ppt', 'pptx']
VK_ADMIN_FULL_RIGHT = False
VK_ADMIN_NO_INFO = False
VK_COPYRIGHT = '2009-2024'
VK_ALLOWED_TAGS = '<b><i><sup><sub><em><strong><u><br><a><strike><ul><li><h1><h2><h3><ol><small>'
VK_FILE_PREFIX = 'EncryptedFile_'
NUMBER_ITEMS_IN_BATCH = 100

ERR_NOT_ALLOWED = '1000'
ERR_NOT_EXIST = '1001'
ERR_SESS_EXPIRED = '1002'
ERR_VALID_SESSION = '1004'

OTV_USER_ID = '9999991'
VK_USER_ID = '9999997'
SSH_USER_ID = '9999998'
API_USER_ID = '9999999'

VK_ENCRYPTION_NAME = 'vaultkeeper_aes'
VK_DEFAULT_ICON = 'fa-solid fa-folder'
VK_DEFAULT_ICON_SELECTED = 'fa-solid fa-folder-open'

VK_PW_STRENGTH_1 = 0
VK_PW_STRENGTH_2 = 20
VK_PW_STRENGTH_3 = 38
VK_PW_STRENGTH_4 = 48
VK_PW_STRENGTH_5 = 60

DOCUMENTATION_URL = 'https://docs.vaultkeeper.net/'
HELP_URL = 'https://github.com/vaultkeeper/VaultKeeper/discussions'

DEBUG = False
DEBUG_LDAP = False
ADMIN_VISIBLE_OTP_ON_LDAP_IMPORT = True

MANAGEMENT_PAGES = {
    'admin': 'admin',
    'tasks': 'tasks',
    'options': 'options',
    'statistics': 'statistics',
    '2fa': '2fa',
    'special': 'special',
    'ldap': 'ldap',
    'emails': 'emails',
    'backups': 'backups',
    'api': 'api',
    'fields': 'fields',
    'actions': 'actions',
    'uploads': 'uploads',
}

UTILITIES_PAGES = {
    'utilities.renewal': 'utilities_renewal',
    'utilities.deletion': 'utilities_deletion',
    'utilities.logs': 'utilities_logs',
    'utilities.database': 'utilities_database',
}
