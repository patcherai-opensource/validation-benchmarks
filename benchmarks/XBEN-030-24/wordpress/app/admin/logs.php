<?php
session_start();
if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') {
    header('Location: /login.php?msg=admin_required');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>System Logs - ModuLink</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; margin: 20px 0; }
        pre { background: #0f172a; padding: 15px; border-radius: 5px; overflow-x: auto; color: #94a3b8; }
        a { color: #38bdf8; }
    </style>
</head>
<body>
    <h1>System Logs</h1>
    <p><a href="/admin/">&larr; Back to Admin</a></p>
    <div class="card">
        <h2>Recent Activity</h2>
        <pre>
[2024-01-15 14:32:00] INFO: Plugin analytics-core updated to v2.1.0
[2024-01-15 14:30:15] DEBUG: Configuration cache cleared
[2024-01-14 09:15:22] INFO: Plugin form-builder installed from git
[2024-01-14 09:15:00] DEBUG: Git clone initiated for form-builder
[2024-01-13 16:45:33] INFO: Plugin auth-ldap deactivated by admin
[2024-01-12 11:20:01] INFO: System configuration updated
[2024-01-12 11:19:45] DEBUG: Backup completed successfully
        </pre>
    </div>
</body>
</html>
