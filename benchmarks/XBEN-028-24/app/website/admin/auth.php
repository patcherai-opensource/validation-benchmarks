<?php
session_start();

function getDb() {
    static $db = null;
    if ($db === null) {
        $db = new PDO('sqlite:/var/www/html/data/aimeos.db');
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }
    return $db;
}

function isAuthenticated() {
    return isset($_SESSION['user_id']) && isset($_SESSION['user_code']);
}

function requireAuth() {
    if (!isAuthenticated()) {
        header('Location: /admin/login.php');
        exit();
    }
}

function requireAuthApi() {
    if (!isAuthenticated()) {
        http_response_code(401);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Authentication required']);
        exit();
    }
}

function getCurrentUser() {
    if (!isAuthenticated()) return null;
    $db = getDb();
    $stmt = $db->prepare("SELECT id, code, label, firstname, lastname, email, roleid FROM mshop_customer WHERE id = ? AND status = 1");
    $stmt->execute([$_SESSION['user_id']]);
    return $stmt->fetch(PDO::FETCH_ASSOC);
}
