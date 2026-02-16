<?php

function check_session() {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }
    return isset($_SESSION['user_id']) && isset($_SESSION['username']);
}

function get_session_user() {
    if (!check_session()) {
        return null;
    }
    return [
        'user_id' => $_SESSION['user_id'],
        'username' => $_SESSION['username'],
        'role' => $_SESSION['role'] ?? 'viewer',
        'display_name' => $_SESSION['display_name'] ?? $_SESSION['username']
    ];
}

function require_role($minimum_role) {
    $user = get_session_user();
    if (!$user) {
        return false;
    }
    
    $role_hierarchy = ['viewer' => 1, 'editor' => 2, 'admin' => 3];
    $user_level = $role_hierarchy[$user['role']] ?? 0;
    $required_level = $role_hierarchy[$minimum_role] ?? 0;
    
    return $user_level >= $required_level;
}
