<?php
require_once __DIR__ . '/auth.php';
requireAdmin();

$conn = getDbConnection();
$result = $conn->query("SELECT id, username, role, email, firstname, lastname, active FROM cms_users ORDER BY username");
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
    <title>Users - Administration</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>CMS Admin</h2>
                <span class="user-badge"><?php echo htmlspecialchars($_SESSION['cms_username']); ?></span>
            </div>
            <ul class="nav-menu">
                <li><a href="/admin/dashboard.php">Dashboard</a></li>
                <li><a href="/admin/elements.php">Elements</a></li>
                <li><a href="/admin/segments.php">Segments</a></li>
                <li><a href="/admin/segment-manager.php">Segment Manager</a></li>
                <li><a href="/admin/users.php" class="active">Users</a></li>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <h1>User Management</h1>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($users as $user): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($user['id']); ?></td>
                        <td><?php echo htmlspecialchars($user['username']); ?></td>
                        <td><?php echo htmlspecialchars($user['firstname'] . ' ' . $user['lastname']); ?></td>
                        <td><?php echo htmlspecialchars($user['email']); ?></td>
                        <td><?php echo htmlspecialchars($user['role']); ?></td>
                        <td><?php echo $user['active'] ? 'Active' : 'Inactive'; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
