<?php
    session_start();
    session_unset();
    session_destroy();
    setcookie("session", "", time() - 3600, '/');
    header("Location: sign-in.php");
    exit();
?>
