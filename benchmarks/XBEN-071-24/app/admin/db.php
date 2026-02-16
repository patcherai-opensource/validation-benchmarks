<?php
/**
 * Database connection utility for the CMS admin panel.
 * Provides a shared mysqli connection instance.
 */
function get_db_connection() {
    static $conn = null;
    if ($conn === null || !$conn->ping()) {
        $servername = $_ENV['DB_HOST'] ?? "127.0.0.1";
        $username = $_ENV['DB_USER'] ?? "challenge";
        $password = $_ENV['DB_PASSWORD'] ?? "challenge";
        $dbname = $_ENV['DB_NAME'] ?? "challenge";
        $conn = new mysqli($servername, $username, $password, $dbname);
        if ($conn->connect_error) {
            http_response_code(500);
            die("Service temporarily unavailable.");
        }
        $conn->set_charset("utf8mb4");
    }
    return $conn;
}
