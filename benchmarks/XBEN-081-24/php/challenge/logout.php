<?php
    include 'config.php';
    include 'user-profile.php';

    if (isset($_COOKIE['token'])) {
        $conn = getDbConnection();
        $token = $_COOKIE['token'];
        $stmt = $conn->prepare("DELETE FROM sessions WHERE token = ?");
        $stmt->bind_param("s", $token);
        $stmt->execute();
        $stmt->close();
        $conn->close();
    }

    setcookie('token', '', time() - 3600, '/');
    header("Location: /sign-in.php");
    exit();
?>
