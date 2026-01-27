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
    <title>SilverStripe Subsites - Management Console</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Subsites Management Console</h1>
        <p class="subtitle">Manage your multi-site network from a single CMS instance</p>
    </div>

    <div class="dashboard-nav">
        <a href="index.php" class="nav-active">Dashboard</a>
        <a href="groups.php">Groups & Permissions</a>
        <a href="cms_login.php">CMS Admin</a>
    </div>

    <h2>Active Subsites</h2>
    
    <?php
    // Fetch all active subsites
    $subsites_result = $conn->query("SELECT * FROM subsites ORDER BY is_default DESC, created_at DESC");
    
    if ($subsites_result && $subsites_result->num_rows > 0) {
        echo "<div class='subsites-grid'>";
        while($row = $subsites_result->fetch_assoc()) {
            $default_badge = $row['is_default'] ? "<span class='badge'>Default</span>" : "";
            echo "<div class='subsite-card'>
                    <h3>{$row['title']} {$default_badge}</h3>
                    <p><strong>Domain:</strong> {$row['domain']}</p>
                    <p><strong>Theme:</strong> {$row['theme']}</p>
                    <p class='meta'>Created: {$row['created_at']}</p>
                </div>";
        }
        echo "</div>";
    } else {
        echo "<p>No subsites configured.</p>";
    }
    ?>
    
    <h2>Quick Stats</h2>
    <div class="stats-row">
        <?php
        $stats_groups = $conn->query("SELECT COUNT(*) as cnt FROM site_groups");
        $stats_subsites = $conn->query("SELECT COUNT(*) as cnt FROM subsites");
        $groups_count = $stats_groups->fetch_assoc()['cnt'];
        $subsites_count = $stats_subsites->fetch_assoc()['cnt'];
        ?>
        <div class="stat-box">
            <span class="stat-number"><?php echo $subsites_count; ?></span>
            <span class="stat-label">Subsites</span>
        </div>
        <div class="stat-box">
            <span class="stat-number"><?php echo $groups_count; ?></span>
            <span class="stat-label">Groups</span>
        </div>
    </div>

    <?php
    $conn->close();
    ?>
</div>

<footer class="footer">
    <p>SilverStripe Subsites Module v2.1.0 | <a href="cms_login.php">Admin Access</a></p>
</footer>
</body>
</html>
