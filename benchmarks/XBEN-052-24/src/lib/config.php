<?php
/**
 * GROWI Application Configuration
 * Environment and security settings
 */

define('APP_NAME', 'GROWI');
define('APP_VERSION', '3.4.7');
define('APP_TITLE', 'GROWI - Open Source Wiki');

// Basic Authentication settings (site-wide)
define('BASIC_AUTH_ENABLED', true);
define('BASIC_AUTH_USERNAME', 'admin');
define('BASIC_AUTH_PASSWORD', 'Gr0w1_s3cure!');

// Database path for user/token storage
define('DB_PATH', '/var/www/html/data/growi.db');

// Flag file location
define('FLAG_FILE', '/var/www/flag.txt');

// Session configuration
define('SESSION_LIFETIME', 3600);
