<?php
// TYPO3 Backend entry point - redirect to login handler
// The backend login is handled by the main admin.php controller
// which implements the SaltedPasswordService authentication
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Forward POST requests to the login handler
    require __DIR__ . '/../admin.php';
    exit;
}

session_start();
if (isset($_SESSION['be_user'])) {
    header('Location: /typo3/backend.php');
    exit;
}

// Show login form
require __DIR__ . '/../admin.php';
