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
    <title>System Settings - ModuLink</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; margin: 20px 0; }
        h1 { margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #94a3b8; }
        input, select { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 5px; color: #e2e8f0; }
        .btn { padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; }
        a { color: #38bdf8; }
    </style>
</head>
<body>
    <h1>System Settings</h1>
    <p><a href="/admin/">&larr; Back to Admin</a></p>
    <div class="card">
        <h2>General Configuration</h2>
        <form>
            <div class="form-group">
                <label>Site Name</label>
                <input type="text" value="ModuLink Enterprise" disabled>
            </div>
            <div class="form-group">
                <label>Plugin Directory</label>
                <input type="text" value="/var/www/html/plugins" disabled>
            </div>
            <div class="form-group">
                <label>Log Level</label>
                <select disabled>
                    <option>INFO</option>
                    <option selected>DEBUG</option>
                    <option>WARN</option>
                </select>
            </div>
            <button type="button" class="btn" disabled>Save (Demo Mode)</button>
        </form>
    </div>
</body>
</html>
