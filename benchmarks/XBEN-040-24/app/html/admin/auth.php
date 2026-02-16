<?php
session_start();

function requireAuth() {
    if (!isset($_SESSION['cms_user_id']) || !isset($_SESSION['cms_role'])) {
        if (isApiRequest()) {
            header('Content-Type: application/json');
            http_response_code(403);
            echo json_encode(['success' => false, 'message' => 'Authentication required']);
            exit;
        }
        header('Location: /admin.php');
        exit;
    }
}

function requireAdmin() {
    requireAuth();
    if ($_SESSION['cms_role'] !== 'admin') {
        if (isApiRequest()) {
            header('Content-Type: application/json');
            http_response_code(403);
            echo json_encode(['success' => false, 'message' => 'Insufficient permissions']);
            exit;
        }
        http_response_code(403);
        echo 'Access denied.';
        exit;
    }
}

function isApiRequest() {
    return strpos($_SERVER['REQUEST_URI'], '/admin/api/') === 0 ||
           (isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false);
}

function getDbConnection() {
    $mysql_host = getenv('MYSQL_HOST') ?: '127.0.0.1';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'cmsDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        if (isApiRequest()) {
            header('Content-Type: application/json');
            http_response_code(500);
            echo json_encode(['success' => false, 'message' => 'Service unavailable']);
            exit;
        }
        die('Service unavailable.');
    }
    return $conn;
}
