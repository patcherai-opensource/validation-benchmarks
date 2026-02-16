<?php

function get_db_connection() {
    $host = getenv('DB_HOST') ?: '127.0.0.1';
    $user = getenv('DB_USER') ?: 'wikiapp';
    $pass = getenv('DB_PASSWORD') ?: 'Kj7#mP9xR2vL';
    $dbname = getenv('DB_NAME') ?: 'wikiengine';
    $port = getenv('DB_PORT') ?: '3306';

    $conn = new mysqli($host, $user, $pass, $dbname, (int)$port);

    if ($conn->connect_error) {
        error_log("Database connection failed: " . $conn->connect_error);
        return null;
    }

    $conn->set_charset("utf8mb4");
    return $conn;
}
