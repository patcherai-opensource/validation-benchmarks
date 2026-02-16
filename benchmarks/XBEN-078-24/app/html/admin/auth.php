<?php
session_start();

function requireAuth() {
    if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
        if (isApiRequest()) {
            header('Content-Type: application/json');
            http_response_code(403);
            echo json_encode(['success' => false, 'message' => 'Authentication required']);
            exit;
        }
        header('Location: /');
        exit;
    }
}

function isApiRequest() {
    return strpos($_SERVER['REQUEST_URI'], '/admin/api/') !== false;
}

function getDbConnection() {
    $conn = new mysqli(
        $_ENV['MYSQL_HOST'] ?? '127.0.0.1',
        $_ENV['MYSQL_USER'] ?? 'user',
        $_ENV['MYSQL_PASSWORD'] ?? 'password',
        $_ENV['MYSQL_DATABASE'] ?? 'cmfDB'
    );
    if ($conn->connect_error) {
        if (isApiRequest()) {
            header('Content-Type: application/json');
            http_response_code(500);
            echo json_encode(['success' => false, 'message' => 'Internal server error']);
            exit;
        }
        die('Service temporarily unavailable.');
    }
    return $conn;
}

function jsonResponse($data, $code = 200) {
    header('Content-Type: application/json');
    http_response_code($code);
    echo json_encode($data);
    exit;
}