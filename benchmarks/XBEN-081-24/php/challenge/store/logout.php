<?php
    require_once __DIR__ . '/../config.php';

    session_start();
    session_unset();
    session_destroy();

    setcookie(CUSTOMER_REMEMBER_ME_COOKIE_NAME, '', time() - 3600, '/');

    header("Location: /store/");
    exit();
?>