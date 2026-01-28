<?php
/**
 * Dolibar ERP - Open Source Business Software
 * Front page - redirects to login
 */

session_start();

// If logged in, redirect to dashboard
if (isset($_SESSION['logged_in']) && $_SESSION['logged_in'] === true) {
    header("Location: /admin/index.php");
    exit;
}

// Redirect to login page
header("Location: /admin/login.php");
exit;
?>
