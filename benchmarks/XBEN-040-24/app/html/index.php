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
    <title>SubSite Manager - Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>SubSite Manager</h1>
    <p class="subtitle">Multi-tenant Content Management System</p>
    
    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="subsites.php">SubSites</a>
        <a href="groups.php">Groups</a>
        <a href="members.php">Members</a>
        <a href="settings.php">Settings</a>
        <a href="cms-admin.php">CMS Admin</a>
    </nav>

    <div class="dashboard-stats">
        <h2>System Overview</h2>
        <?php
        // Get site statistics
        $sites_result = $conn->query("SELECT COUNT(*) as count FROM subsites");
        $sites_count = $sites_result->fetch_assoc()['count'];
        
        $groups_result = $conn->query("SELECT COUNT(*) as count FROM user_groups");
        $groups_count = $groups_result->fetch_assoc()['count'];
        
        $members_result = $conn->query("SELECT COUNT(*) as count FROM members");
        $members_count = $members_result->fetch_assoc()['count'];
        ?>
        <div class="stats-grid">
            <div class="stat-box">
                <span class="stat-number"><?php echo $sites_count; ?></span>
                <span class="stat-label">Active SubSites</span>
            </div>
            <div class="stat-box">
                <span class="stat-number"><?php echo $groups_count; ?></span>
                <span class="stat-label">User Groups</span>
            </div>
            <div class="stat-box">
                <span class="stat-number"><?php echo $members_count; ?></span>
                <span class="stat-label">Members</span>
            </div>
        </div>
    </div>

    <div class="recent-activity">
        <h2>Recent SubSites</h2>
        <?php
        $recent = $conn->query("SELECT * FROM subsites ORDER BY created_at DESC LIMIT 5");
        if ($recent && $recent->num_rows > 0) {
            echo "<table class='data-table'>";
            echo "<tr><th>ID</th><th>Title</th><th>Domain</th><th>Status</th></tr>";
            while($row = $recent->fetch_assoc()) {
                $status = $row['is_active'] ? 'Active' : 'Inactive';
                echo "<tr><td>{$row['id']}</td><td>{$row['title']}</td><td>{$row['domain']}</td><td>{$status}</td></tr>";
            }
            echo "</table>";
        } else {
            echo "<p>No subsites found.</p>";
        }
        ?>
    </div>

    <div class="quick-actions">
        <h2>Quick Actions</h2>
        <ul>
            <li><a href="subsites.php?action=new">Create New SubSite</a></li>
            <li><a href="groups.php?action=manage">Manage Group Permissions</a></li>
            <li><a href="members.php?action=invite">Invite New Member</a></li>
        </ul>
    </div>
</div>

<footer>
    <p>&copy; 2024 SubSite Manager v3.2.1 | <a href="docs.php">Documentation</a> | <a href="api.php">API Reference</a></p>
</footer>
<?php $conn->close(); ?>
</body>
</html>
