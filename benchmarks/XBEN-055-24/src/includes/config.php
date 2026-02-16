<?php
/**
 * Application configuration
 */

define('APP_NAME', 'Corporate Portal');
define('APP_VERSION', '3.1.13');
define('DB_PATH', '/var/www/data/application.db');
define('SESSION_TIMEOUT', 3600);
define('LOCKOUT_THRESHOLD', 10);
define('PASSWORD_RESET_EXPIRY', '+2 days');

// Suppress PHP errors in production
error_reporting(0);
ini_set('display_errors', 0);

// Configure session
ini_set('session.cookie_httponly', 1);
ini_set('session.use_strict_mode', 1);

// Remove X-Powered-By header
header_remove('X-Powered-By');
