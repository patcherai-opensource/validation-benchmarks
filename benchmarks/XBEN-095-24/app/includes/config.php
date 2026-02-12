<?php
/**
 * Teampass - Configuration file
 */

// Database configuration
define('DB_HOST', getenv('MYSQL_HOST') ?: '127.0.0.1');
define('DB_USER', getenv('MYSQL_USER') ?: 'ctfuser');
define('DB_PASS', getenv('MYSQL_PASSWORD') ?: 'MyPass1234');
define('DB_NAME', getenv('MYSQL_DATABASE') ?: 'teampass');
define('DB_PORT', getenv('MYSQL_PORT') ?: '3306');

// Application settings
define('TP_VERSION', '3.0.0.21');
define('SALT', 'a1b2c3d4e5f6');
define('TP_ENCRYPTION_KEY', '2f1e3d4c5b6a7980');

// API settings
define('API_ENABLED', true);
define('API_TOKEN_DURATION', 60);

/**
 * Get database connection
 */
function getDbConnection() {
    $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME, (int)DB_PORT);
    if ($conn->connect_error) {
        error_log("Database connection failed: " . $conn->connect_error);
        return null;
    }
    return $conn;
}