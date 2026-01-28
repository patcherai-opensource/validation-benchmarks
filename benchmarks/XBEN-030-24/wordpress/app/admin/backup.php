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
    <title>Backup & Restore - ModuLink</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .btn { padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px; }
        a { color: #38bdf8; }
    </style>
</head>
<body>
    <h1>Backup & Restore</h1>
    <p><a href="/admin/">&larr; Back to Admin</a></p>
    <div class="card">
        <h2>Create Backup</h2>
        <p style="color: #94a3b8; margin-bottom: 15px;">Create a full backup of your ModuLink configuration and plugins.</p>
        <button class="btn" disabled>Create Backup (Demo Mode)</button>
    </div>
    <div class="card">
        <h2>Recent Backups</h2>
        <p style="color: #94a3b8;">backup_2024-01-15_143000.zip - 2.3 MB</p>
        <p style="color: #94a3b8;">backup_2024-01-14_091500.zip - 2.1 MB</p>
    </div>
</body>
</html>
