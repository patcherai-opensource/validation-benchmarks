<?php
    include 'config.php';
    session_start();

    // Clear customer session data
    unset($_SESSION['customer_id']);
    unset($_SESSION['customer_email']);
    unset($_SESSION['customer_name']);

    // Clear persistence cookie
    if (isset($_COOKIE[$customer_persist_cookie])) {
        setcookie($customer_persist_cookie, '', time() - 3600, '/');
    }

    session_destroy();
    header("Location: index.php");
    exit();
?>