<?php
session_start();
$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'subsiteDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Fetch settings
$settings_query = "SELECT * FROM system_settings";
$settings_result = $conn->query($settings_query);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SilverSubsite CMS - Settings</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="cms-header">
        <h1>SilverSubsite CMS</h1>
        <p class="tagline">System Settings</p>
    </header>

    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="groups.php">Group Management</a>
        <a href="subsites.php">Subsites</a>
        <a href="settings.php" class="active">Settings</a>
        <a href="admin.php">Admin Panel</a>
    </nav>

    <section class="settings-page">
        <h2>System Configuration</h2>
        
        <?php if ($settings_result && $settings_result->num_rows > 0): ?>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Setting</th>
                        <th>Value</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while ($setting = $settings_result->fetch_assoc()): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($setting['setting_key']); ?></td>
                            <td><?php echo htmlspecialchars($setting['setting_value']); ?></td>
                            <td><?php echo htmlspecialchars($setting['description']); ?></td>
                        </tr>
                    <?php endwhile; ?>
                </tbody>
            </table>
        <?php else: ?>
            <p>No settings configured.</p>
        <?php endif; ?>
        
        <div class="info-box">
            <h3>Version Information</h3>
            <p>SilverSubsite CMS v2.1.0</p>
            <p>Schema Extension: GroupSubsites v2.1.0</p>
        </div>
    </section>
</div>
<?php $conn->close(); ?>
</body>
</html>
