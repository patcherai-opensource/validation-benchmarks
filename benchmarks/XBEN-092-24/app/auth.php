<?php

session_start();

function getSession() {
    if (isset($_SESSION['user_id']) && isset($_SESSION['username'])) {
        return [
            'user_id' => $_SESSION['user_id'],
            'username' => $_SESSION['username'],
            'role' => $_SESSION['role'] ?? 'user',
        ];
    }
    return null;
}

function requireAuth() {
    $session = getSession();
    if (!$session) {
        header('Location: /login.php');
        exit();
    }
    return $session;
}

function authenticateUser($username, $password) {
    $db = include __DIR__ . '/database.php';
    $stmt = $db->prepare('SELECT id, username, password_hash, role FROM users WHERE username = ?');
    $stmt->execute([$username]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($user && password_verify($password, $user['password_hash'])) {
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];
        return true;
    }
    return false;
}
