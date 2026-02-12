<?php
/**
 * Authentication helper for admin area
 */

function requireAdminAuth() {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }

    if (!isset($_SESSION['pimcore_admin_sid']) || $_SESSION['pimcore_admin_sid'] !== true) {
        $accept = $_SERVER['HTTP_ACCEPT'] ?? '';
        if (strpos($accept, 'application/json') !== false ||
            strpos($_SERVER['CONTENT_TYPE'] ?? '', 'application/json') !== false ||
            isset($_SERVER['HTTP_X_REQUESTED_WITH'])) {
            header('Content-Type: application/json');
            http_response_code(403);
            echo json_encode(['success' => false, 'message' => 'Access denied - admin session required']);
            exit;
        }
        header('Location: /');
        exit;
    }

    return $_SESSION['pimcore_user'];
}

function getDbConnection() {
    $mysql_host = getenv('MYSQL_HOST') ?: '127.0.0.1';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'pimcore';

    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        http_response_code(500);
        header('Content-Type: application/json');
        echo json_encode(['success' => false, 'message' => 'Internal server error']);
        exit;
    }
    return $conn;
}
