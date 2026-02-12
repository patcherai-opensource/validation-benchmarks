<?php
session_start();

function requireAdmin() {
    if (!isset($_SESSION['pimcore_admin']) || $_SESSION['pimcore_admin'] !== true) {
        http_response_code(403);
        header('Content-Type: application/json');
        echo json_encode(['success' => false, 'message' => 'Access denied. Please login.']);
        exit;
    }
}

function getDbConnection() {
    $conn = new mysqli(
        $_ENV['MYSQL_HOST'] ?? '127.0.0.1',
        $_ENV['MYSQL_USER'] ?? 'user',
        $_ENV['MYSQL_PASSWORD'] ?? 'password',
        $_ENV['MYSQL_DATABASE'] ?? 'pimcore'
    );

    if ($conn->connect_error) {
        http_response_code(500);
        header('Content-Type: application/json');
        echo json_encode(['success' => false, 'message' => 'Database connection error.']);
        exit;
    }

    return $conn;
}
