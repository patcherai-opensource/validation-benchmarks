<?php
/**
 * Database connection helper for XWiki Platform.
 * Uses environment-based configuration for container deployments.
 */
function get_db_connection() {
    $host = getenv('MYSQL_HOST') ?: '127.0.0.1';
    $user = getenv('MYSQL_USER') ?: 'xwikiuser';
    $pass = getenv('MYSQL_PASSWORD') ?: 'xwiki2024Secure';
    $db   = getenv('MYSQL_DATABASE') ?: 'xwiki';
    $port = getenv('MYSQL_PORT') ?: 3306;

    $conn = new mysqli($host, $user, $pass, $db, $port);

    if ($conn->connect_error) {
        http_response_code(503);
        die('Service temporarily unavailable.');
    }

    $conn->set_charset('utf8mb4');
    return $conn;
}
