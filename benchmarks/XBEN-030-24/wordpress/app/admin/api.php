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
    <title>API Management - ModuLink</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; margin: 20px 0; }
        code { background: #334155; padding: 2px 6px; border-radius: 3px; }
        a { color: #38bdf8; }
    </style>
</head>
<body>
    <h1>API Management</h1>
    <p><a href="/admin/">&larr; Back to Admin</a></p>
    <div class="card">
        <h2>API Keys</h2>
        <p style="color: #94a3b8; margin-bottom: 15px;">No API keys configured. API key management coming soon.</p>
    </div>
    <div class="card">
        <h2>Rate Limiting</h2>
        <p style="color: #94a3b8;">Current limit: <code>100 requests/minute</code></p>
    </div>
</body>
</html>
