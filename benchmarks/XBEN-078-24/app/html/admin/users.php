<?php
require_once __DIR__ . '/auth.php';
requireAdmin();

$conn = getDbConnection();
$result = $conn->query("SELECT id, username, firstname, lastname, email, admin, active, language, lastLogin FROM users ORDER BY id ASC");
$users = [];
while ($row = $result->fetch_assoc()) {
    $users[] = $row;
}
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Administration - Users</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header"><h2>CMS Admin</h2></div>
            <ul class="nav-menu">
                <li><a href="/admin/portal.php">Dashboard</a></li>
                <li><a href="/admin/documents.php">Documents</a></li>
                <li><a href="/admin/assets-manager.php">Assets</a></li>
                <li><a href="/admin/locale/data.php">Translations</a></li>
                <li class="active"><a href="/admin/users.php">Users</a></li>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header"><h1>User Management</h1></div>
            <table class="data-table">
                <thead>
                    <tr><th>ID</th><th>Username</th><th>Name</th><th>Email</th><th>Admin</th><th>Active</th><th>Last Login</th></tr>
                </thead>
                <tbody>
                    <?php foreach ($users as $user): ?>
                    <tr>
                        <td><?php echo $user['id']; ?></td>
                        <td><?php echo htmlspecialchars($user['username']); ?></td>
                        <td><?php echo htmlspecialchars(($user['firstname'] ?? '') . ' ' . ($user['lastname'] ?? '')); ?></td>
                        <td><?php echo htmlspecialchars($user['email'] ?? '-'); ?></td>
                        <td><?php echo $user['admin'] ? 'Yes' : 'No'; ?></td>
                        <td><?php echo $user['active'] ? 'Yes' : 'No'; ?></td>
                        <td><?php echo $user['lastLogin'] ? date('Y-m-d H:i', $user['lastLogin']) : 'Never'; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
