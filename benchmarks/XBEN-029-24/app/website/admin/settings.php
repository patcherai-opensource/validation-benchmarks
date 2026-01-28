<?php
include("../include/db_config.php");
session_start();

if (!isset($_SESSION['username'])) {
    header("Location: /index.php?error=failed_login");
    exit();
}
?>
<!doctype html>
<html><head><title>phpDocFAQ - Settings</title></head>
<body>
    <h1>Settings</h1>
    <p>This feature is under development.</p>
    <a href="/admin/dashboard.php">Back to Dashboard</a>
</body>
</html>
