<?php
session_start();
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: login.php");
    exit;
}

$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'blogDB');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ezPortal CMS - Manage Users</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>User Management</h1>
    </div>
    
    <nav class="admin-nav">
        <a href="admin.php">Dashboard</a>
        <a href="manage_articles.php">Manage Articles</a>
        <a href="manage_users.php">Manage Users</a>
        <a href="settings.php">Settings</a>
        <a href="logout.php">Logout</a>
    </nav>

    <div class="admin-content">
        <h2>Registered Users</h2>
        <table class="data-table">
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Auth Type</th>
            </tr>
            <?php
            $result = $conn->query("SELECT id, username, email, role, password_hash_type FROM users ORDER BY id");
            while ($row = $result->fetch_assoc()) {
                $auth_type = $row['password_hash_type'] == 0 ? 'LDAP/External' : 'Standard';
                echo "<tr>
                    <td>{$row['id']}</td>
                    <td>" . htmlspecialchars($row['username']) . "</td>
                    <td>" . htmlspecialchars($row['email']) . "</td>
                    <td>{$row['role']}</td>
                    <td>{$auth_type}</td>
                </tr>";
            }
            ?>
        </table>
    </div>
</div>
</body>
</html>
<?php $conn->close(); ?>
