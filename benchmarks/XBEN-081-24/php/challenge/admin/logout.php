<?php
    require_once __DIR__ . '/../config.php';

    session_start();
    session_unset();
    session_destroy();

    setcookie(ADMIN_REMEMBER_ME_COOKIE_NAME, '', time() - 3600, '/admin');

    header("Location: /admin/login.php");
    exit();
?>