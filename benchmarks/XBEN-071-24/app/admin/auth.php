<?php
/**
 * Authentication helper for the CMS admin panel.
 * Validates session state and redirects unauthenticated users.
 */
session_start();

function require_auth() {
    if (!isset($_SESSION['cms_user_id']) || !isset($_SESSION['cms_username'])) {
        header("Location: /admin/login.php");
        exit;
    }
}

function get_current_user_info() {
    return [
        'id' => $_SESSION['cms_user_id'] ?? null,
        'username' => $_SESSION['cms_username'] ?? null,
        'role' => $_SESSION['cms_role'] ?? null,
    ];
}

function is_authenticated() {
    return isset($_SESSION['cms_user_id']);
}
