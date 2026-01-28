<?php
session_start();
if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header("Location: /admin/");
    exit;
}
?>
<!DOCTYPE html>
<html>
<head><title>Settings - Aimeos CMS</title></head>
<body style="font-family: sans-serif; padding: 50px; max-width: 600px; margin: auto;">
<h1>⚙️ System Settings</h1>
<h3>API Configuration</h3>
<p><strong>Default API Key:</strong> <code>aimeos_dev_key</code></p>
<p style="color: #666; font-size: 0.9em;">Note: In production, generate unique API keys from the API management interface.</p>
<hr style="margin: 20px 0;">
<a href="/admin/">← Back to Dashboard</a>
</body>
</html>
