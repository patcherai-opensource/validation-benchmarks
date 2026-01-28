<?php
    $conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'subsiteDB');
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SilverSubsite CMS - Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="cms-header">
        <h1>SilverSubsite CMS</h1>
        <p class="tagline">Enterprise Multi-Site Content Management</p>
    </header>

    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="groups.php">Group Management</a>
        <a href="subsites.php">Subsites</a>
        <a href="settings.php">Settings</a>
        <a href="admin.php">Admin Panel</a>
    </nav>

    <section class="dashboard-stats">
        <h2>System Overview</h2>
        <div class="stats-grid">
            <?php
            $stats_query = "SELECT COUNT(*) as total FROM sites WHERE status = 1";
            $stats_result = $conn->query($stats_query);
            $active_sites = $stats_result->fetch_assoc()['total'] ?? 0;
            ?>
            <div class="stat-box">
                <span class="stat-number"><?php echo $active_sites; ?></span>
                <span class="stat-label">Active Subsites</span>
            </div>
            <div class="stat-box">
                <span class="stat-number">3</span>
                <span class="stat-label">User Groups</span>
            </div>
            <div class="stat-box">
                <span class="stat-number">12</span>
                <span class="stat-label">Total Users</span>
            </div>
        </div>
    </section>

    <section class="recent-activity">
        <h2>Recent Activity</h2>
        <?php
        $activity_query = "SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 5";
        $activity_result = $conn->query($activity_query);
        
        if ($activity_result && $activity_result->num_rows > 0) {
            echo "<ul class='activity-list'>";
            while($row = $activity_result->fetch_assoc()) {
                echo "<li><span class='activity-action'>{$row['action']}</span> - <span class='activity-time'>{$row['created_at']}</span></li>";
            }
            echo "</ul>";
        } else {
            echo "<p>No recent activity.</p>";
        }
        ?>
    </section>

    <section class="quick-links">
        <h2>Quick Actions</h2>
        <ul>
            <li><a href="groups.php">Manage Group Permissions</a></li>
            <li><a href="subsites.php">Configure Subsites</a></li>
            <li><a href="settings.php">System Settings</a></li>
        </ul>
    </section>
</div>
<?php $conn->close(); ?>
</body>
</html>
