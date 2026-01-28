<?php
session_start();
if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header("Location: /admin/");
    exit;
}
?>
<!DOCTYPE html>
<html>
<head><title>Orders - Coming Soon</title></head>
<body style="font-family: sans-serif; text-align: center; padding: 50px;">
<h1>🛒 Orders Module</h1>
<p>This module is currently under development.</p>
<a href="/admin/">← Back to Dashboard</a>
</body>
</html>
