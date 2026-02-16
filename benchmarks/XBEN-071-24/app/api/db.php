<?php

function getDbConnection() {
    $servername = $_ENV['DB_HOST'] ?? "127.0.0.1";
    $username = $_ENV['DB_USER'] ?? "challenge";
    $password = $_ENV['DB_PASSWORD'] ?? "challenge";
    $dbname = $_ENV['DB_NAME'] ?? "challenge";

    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        return null;
    }

    return $conn;
}
