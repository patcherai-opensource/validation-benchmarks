<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SubSites - SubSite Manager</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>SubSite Management</h1>
    <p class="subtitle">Manage your multi-tenant environments</p>
    
    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="subsites.php" class="active">SubSites</a>
        <a href="groups.php">Groups</a>
        <a href="members.php">Members</a>
        <a href="settings.php">Settings</a>
        <a href="cms-admin.php">CMS Admin</a>
    </nav>

    <div class="subsite-list">
        <h2>Active SubSites</h2>
        <?php
        $result = $conn->query("SELECT * FROM subsites ORDER BY title");
        if ($result && $result->num_rows > 0) {
            echo "<table class='data-table'>";
            echo "<tr><th>ID</th><th>Title</th><th>Domain</th><th>Theme</th><th>Status</th><th>Created</th></tr>";
            while($row = $result->fetch_assoc()) {
                $status = $row['is_active'] ? '<span class="status-active">Active</span>' : '<span class="status-inactive">Inactive</span>';
                echo "<tr>";
                echo "<td>{$row['id']}</td>";
                echo "<td>" . htmlspecialchars($row['title']) . "</td>";
                echo "<td>" . htmlspecialchars($row['domain']) . "</td>";
                echo "<td>" . htmlspecialchars($row['theme']) . "</td>";
                echo "<td>{$status}</td>";
                echo "<td>{$row['created_at']}</td>";
                echo "</tr>";
            }
            echo "</table>";
        } else {
            echo "<p>No subsites configured.</p>";
        }
        ?>
    </div>

    <div class="subsite-actions">
        <h3>Actions</h3>
        <ul>
            <li><a href="subsites.php?action=new">Create New SubSite</a></li>
            <li><a href="subsites.php?action=import">Import Configuration</a></li>
            <li><a href="subsites.php?action=export">Export All SubSites</a></li>
        </ul>
    </div>
</div>

<footer>
    <p>&copy; 2024 SubSite Manager v3.2.1</p>
</footer>
<?php $conn->close(); ?>
</body>
</html>
