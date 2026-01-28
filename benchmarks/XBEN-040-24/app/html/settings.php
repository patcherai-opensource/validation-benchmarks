<?php
    session_start();
    
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
    <title>Settings - SubSite Manager</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>System Settings</h1>
    <p class="subtitle">Configure your SubSite Manager installation</p>
    
    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="subsites.php">SubSites</a>
        <a href="groups.php">Groups</a>
        <a href="members.php">Members</a>
        <a href="settings.php" class="active">Settings</a>
        <a href="cms-admin.php">CMS Admin</a>
    </nav>

    <div class="settings-sections">
        <div class="settings-section">
            <h2>General Settings</h2>
            <form method="POST" action="settings.php">
                <div class="form-group">
                    <label for="site_name">Site Name:</label>
                    <input type="text" id="site_name" name="site_name" value="SubSite Manager">
                </div>
                <div class="form-group">
                    <label for="admin_email">Admin Email:</label>
                    <input type="email" id="admin_email" name="admin_email" value="admin@example.com">
                </div>
                <div class="form-group">
                    <label for="default_theme">Default Theme:</label>
                    <select name="default_theme" id="default_theme">
                        <option value="default">Default</option>
                        <option value="dark">Dark Mode</option>
                        <option value="light">Light Mode</option>
                    </select>
                </div>
                <button type="submit" class="btn-primary" disabled>Save Changes (Requires Admin)</button>
            </form>
        </div>

        <div class="settings-section">
            <h2>Security Settings</h2>
            <form method="POST" action="settings.php">
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="two_factor" checked disabled> Enable Two-Factor Authentication
                    </label>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="audit_log" checked disabled> Enable Audit Logging
                    </label>
                </div>
                <div class="form-group">
                    <label for="session_timeout">Session Timeout (minutes):</label>
                    <input type="number" id="session_timeout" name="session_timeout" value="30" disabled>
                </div>
                <button type="submit" class="btn-primary" disabled>Save Changes (Requires Admin)</button>
            </form>
        </div>

        <div class="settings-section">
            <h2>Database Information</h2>
            <table class="data-table">
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>Database</td><td><?php echo htmlspecialchars($mysql_database); ?></td></tr>
                <tr><td>Host</td><td><?php echo htmlspecialchars($mysql_host); ?></td></tr>
                <tr><td>Version</td><td><?php 
                    $version = $conn->query("SELECT VERSION() as v");
                    echo $version->fetch_assoc()['v'];
                ?></td></tr>
            </table>
        </div>
    </div>
</div>

<footer>
    <p>&copy; 2024 SubSite Manager v3.2.1</p>
</footer>
<?php $conn->close(); ?>
</body>
</html>
