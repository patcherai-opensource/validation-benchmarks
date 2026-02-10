<?php
session_start();
require_once 'includes/db.php';

if (isset($_COOKIE['session_token'])) {
    destroySession($_COOKIE['session_token']);
    setcookie('session_token', '', time() - 3600, '/', '', false, true);
}

header('Location: index.php');
exit;
?>
