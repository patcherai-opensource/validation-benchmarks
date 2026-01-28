<?php
session_start();
$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'subsiteDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Fetch all subsites
$sites_query = "SELECT * FROM sites ORDER BY name";
$sites_result = $conn->query($sites_query);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SilverSubsite CMS - Subsites</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="cms-header">
        <h1>SilverSubsite CMS</h1>
        <p class="tagline">Subsite Configuration</p>
    </header>

    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="groups.php">Group Management</a>
        <a href="subsites.php" class="active">Subsites</a>
        <a href="settings.php">Settings</a>
        <a href="admin.php">Admin Panel</a>
    </nav>

    <section class="subsites-list">
        <h2>Configured Subsites</h2>
        <p>Manage multi-site configurations and access permissions.</p>
        
        <?php if ($sites_result && $sites_result->num_rows > 0): ?>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Site Name</th>
                        <th>Domain</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while ($site = $sites_result->fetch_assoc()): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($site['id']); ?></td>
                            <td><?php echo htmlspecialchars($site['name']); ?></td>
                            <td><?php echo htmlspecialchars($site['domain']); ?></td>
                            <td><?php echo $site['status'] ? '<span class="status-active">Active</span>' : '<span class="status-inactive">Inactive</span>'; ?></td>
                        </tr>
                    <?php endwhile; ?>
                </tbody>
            </table>
        <?php else: ?>
            <p>No subsites configured.</p>
        <?php endif; ?>
    </section>
</div>
<?php $conn->close(); ?>
</body>
</html>
