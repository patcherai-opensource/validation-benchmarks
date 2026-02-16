<?php
    include '../config.php';
    session_start();

    unset($_SESSION['admin_id']);
    unset($_SESSION['admin_login']);
    unset($_SESSION['admin_name']);

    if (isset($_COOKIE[$admin_persist_cookie])) {
        setcookie($admin_persist_cookie, '', time() - 3600, '/');
    }

    session_destroy();
    header("Location: login.php");
    exit();
?>
