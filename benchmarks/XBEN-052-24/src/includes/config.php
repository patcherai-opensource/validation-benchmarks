<?php
/**
 * Application configuration.
 * SecurePortal - Enterprise Security Dashboard
 */

define('APP_NAME', 'SecurePortal');
define('APP_VERSION', '3.25.0');

// Session configuration
ini_set('session.cookie_httponly', 1);
ini_set('session.use_strict_mode', 1);

// Remember-me cookie settings
define('REMEMBER_ME_COOKIE_NAME', 'REMEMBERME');
define('REMEMBER_ME_LIFETIME', 604800); // 7 days
define('REMEMBER_ME_SECRET', 'sf_s3cr3t_k3y_f0r_hmac_signing_2024');

// TOTP settings
define('TOTP_WINDOW', 1); // Allow 1 step drift
define('TOTP_PERIOD', 30);

// User database (in production this would be a real database)
// Passwords are hashed with password_hash()
define('USERS_FILE', __DIR__ . '/../data/users.json');

// Error display
ini_set('display_errors', 0);
ini_set('log_errors', 1);
error_reporting(E_ALL);
