<?php
session_start();

function requireAuth() {
    if (!isset($_SESSION['user_id'])) {
        header('HTTP/1.1 403 Forbidden');
        header('Content-Type: application/json');
        echo json_encode(['success' => false, 'message' => 'Authentication required']);
        exit;
    }
}

function requireAdmin() {
    requireAuth();
    if (empty($_SESSION['is_admin'])) {
        header('HTTP/1.1 403 Forbidden');
        header('Content-Type: application/json');
        echo json_encode(['success' => false, 'message' => 'Insufficient permissions']);
        exit;
    }
}

function getDbConnection() {
    $dbHost = $_ENV['MYSQL_HOST'] ?? '127.0.0.1';
    $dbUser = $_ENV['MYSQL_USER'] ?? 'user';
    $dbPass = $_ENV['MYSQL_PASSWORD'] ?? 'password';
    $dbName = $_ENV['MYSQL_DATABASE'] ?? 'cmsDB';

    $conn = new mysqli($dbHost, $dbUser, $dbPass, $dbName);
    if ($conn->connect_error) {
        header('HTTP/1.1 503 Service Unavailable');
        echo json_encode(['success' => false, 'message' => 'Database connection error']);
        exit;
    }
    return $conn;
}
