<?php
/**
 * Pimcore Admin Panel
 * Redirects to the login page if not authenticated.
 */
session_start();

if (!isset($_SESSION['admin_authenticated'])) {
    header('Location: /admin/login.php');
    exit;
}

header('Location: /admin/dashboard.php');
