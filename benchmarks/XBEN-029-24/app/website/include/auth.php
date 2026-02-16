<?php

function requireAuth() {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }
    if (!isset($_SESSION['user_id']) || !isset($_SESSION['username'])) {
        if (strpos($_SERVER['REQUEST_URI'], '/api/') !== false) {
            http_response_code(401);
            header('Content-Type: application/json');
            echo json_encode(array("error" => "Authentication required"));
            exit();
        }
        header("Location: /index.php");
        exit();
    }
}

function requireAdmin() {
    requireAuth();
    if (!isset($_SESSION['role']) || $_SESSION['role'] !== 'admin') {
        if (strpos($_SERVER['REQUEST_URI'], '/api/') !== false) {
            http_response_code(403);
            header('Content-Type: application/json');
            echo json_encode(array("error" => "Insufficient privileges"));
            exit();
        }
        header("Location: /admin/dashboard.php");
        exit();
    }
}

function getCsrfToken() {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

function verifyCsrfToken($token) {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }
    if (empty($_SESSION['csrf_token']) || empty($token)) {
        return false;
    }
    return hash_equals($_SESSION['csrf_token'], $token);
}

?>
