<?php
session_start();
if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'admin') {
    header('Location: /login.php?msg=admin_required');
    exit;
}
$users = [
    ['id' => 1, 'username' => 'admin', 'email' => 'admin@modulink.local', 'role' => 'admin'],
    ['id' => 2, 'username' => 'viewer', 'email' => 'viewer@modulink.local', 'role' => 'viewer'],
    ['id' => 3, 'username' => 'developer', 'email' => 'developer@modulink.local', 'role' => 'developer'],
];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>User Management - ModuLink</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
        th { background: #0f172a; }
        a { color: #38bdf8; }
    </style>
</head>
<body>
    <h1>User Management</h1>
    <p><a href="/admin/">&larr; Back to Admin</a></p>
    <div class="card">
        <table>
            <thead>
                <tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th></tr>
            </thead>
            <tbody>
                <?php foreach ($users as $u): ?>
                <tr>
                    <td><?= $u['id'] ?></td>
                    <td><?= htmlspecialchars($u['username']) ?></td>
                    <td><?= htmlspecialchars($u['email']) ?></td>
                    <td><?= ucfirst($u['role']) ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</body>
</html>
