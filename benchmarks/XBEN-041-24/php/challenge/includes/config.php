<?php
/**
 * CatalogHub PIM - Configuration
 */

define('APP_NAME', 'CatalogHub PIM');
define('APP_VERSION', '5.0.118');
define('APP_ENV', 'prod');

// Paths
define('BASE_DIR', dirname(__DIR__));
define('PUBLIC_DIR', BASE_DIR . '/public');
define('TEMPLATE_DIR', BASE_DIR . '/templates');
define('MEDIA_DIR', PUBLIC_DIR . '/media');
define('UPLOAD_SUBDIR', 'media');

// Database
define('DB_FILE', BASE_DIR . '/data/cataloghub.db');

// Upload settings
define('MAX_UPLOAD_SIZE', 10 * 1024 * 1024); // 10MB
define('ALLOWED_MIME_TYPES', serialize([
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/svg+xml',
    'application/pdf',
]));
