<?php
    session_start();
    session_unset();
    session_destroy();
    setcookie("user_session", "", time() - 3600);
    setcookie("cms_maintenance", "", time() - 3600);
    header("Location: login.php");
    exit();
?>
