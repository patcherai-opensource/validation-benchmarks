<?php

// Session/auth helper functions

function generateToken($length = 64) {
    return bin2hex(random_bytes($length / 2));
}

function getDbConnection() {
    global $db_host, $db_username, $db_password, $db_database;
    $conn = new mysqli($db_host, $db_username, $db_password, $db_database);
    if ($conn->connect_error) {
        http_response_code(500);
        die("Service temporarily unavailable");
    }
    return $conn;
}

function createSession($conn, $userId) {
    $token = generateToken();
    $stmt = $conn->prepare("INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, DATE_ADD(NOW(), INTERVAL 24 HOUR))");
    $stmt->bind_param("is", $userId, $token);
    $stmt->execute();
    $stmt->close();
    return $token;
}

function getCurrentUser($conn) {
    if (!isset($_COOKIE['token'])) {
        return null;
    }
    $token = $_COOKIE['token'];
    $stmt = $conn->prepare("SELECT u.id, u.username, u.email, u.role, u.profile_image_url FROM users u INNER JOIN sessions s ON u.id = s.user_id WHERE s.token = ? AND s.expires_at > NOW()");
    $stmt->bind_param("s", $token);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($result->num_rows === 1) {
        $user = $result->fetch_assoc();
        $stmt->close();
        return $user;
    }
    $stmt->close();
    return null;
}

function requireAuth($conn) {
    $user = getCurrentUser($conn);
    if (!$user) {
        header("Location: /sign-in.php");
        exit();
    }
    return $user;
}

function requireAdmin($conn) {
    $user = requireAuth($conn);
    if ($user['role'] !== 'admin') {
        http_response_code(403);
        die("Access denied");
    }
    return $user;
}

?>
