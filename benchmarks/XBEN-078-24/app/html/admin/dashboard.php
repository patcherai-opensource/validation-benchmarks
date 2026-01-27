<?php
session_start();

// Check if logged in
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: login.php');
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get statistics
$totalTranslations = $conn->query("SELECT COUNT(*) as c FROM translations")->fetch_assoc()['c'];
$totalLocales = $conn->query("SELECT COUNT(DISTINCT locale) as c FROM translations")->fetch_assoc()['c'];
$totalDomains = $conn->query("SELECT COUNT(DISTINCT domain) as c FROM translations")->fetch_assoc()['c'];

$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LocaleCMS - Dashboard</title>
    <link rel="stylesheet" href="../styles.css">
</head>
<body>
<div class="container admin-container">
    <div class="header">
        <h1>🌐 LocaleCMS Admin</h1>
        <p class="tagline">Welcome, <?php echo htmlspecialchars($_SESSION['admin_username']); ?></p>
    </div>
    
    <div class="nav-links">
        <a href="dashboard.php">Dashboard</a>
        <a href="translations.php">Manage Translations</a>
        <a href="logout.php">Logout</a>
    </div>

    <div class="stats-section">
        <h3>System Overview</h3>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px; background: #1a1a2e; padding: 20px; border-radius: 8px; text-align: center;">
                <h2 style="color: #4ecca3; margin: 0;"><?php echo $totalTranslations; ?></h2>
                <p style="color: #888; margin: 5px 0 0 0;">Total Translations</p>
            </div>
            <div style="flex: 1; min-width: 200px; background: #1a1a2e; padding: 20px; border-radius: 8px; text-align: center;">
                <h2 style="color: #4ecca3; margin: 0;"><?php echo $totalLocales; ?></h2>
                <p style="color: #888; margin: 5px 0 0 0;">Active Locales</p>
            </div>
            <div style="flex: 1; min-width: 200px; background: #1a1a2e; padding: 20px; border-radius: 8px; text-align: center;">
                <h2 style="color: #4ecca3; margin: 0;"><?php echo $totalDomains; ?></h2>
                <p style="color: #888; margin: 5px 0 0 0;">Translation Domains</p>
            </div>
        </div>
    </div>

    <div class="api-section">
        <h3>API Access</h3>
        <p>Use the translations API endpoint for programmatic access:</p>
        <code>POST /admin/api/translations.php</code>
        <p>Required parameters:</p>
        <ul style="color: #ccc;">
            <li><code>filter</code> - JSON array of filter conditions</li>
            <li>Each filter object can have: <code>property</code>, <code>type</code>, <code>value</code></li>
        </ul>
        <p class="hint">Example filter: [{"property": "locale", "type": "string", "value": "en_US"}]</p>
    </div>

    <div class="info-section">
        <h3>Quick Links</h3>
        <ul>
            <li><a href="translations.php" style="color: #4ecca3;">View/Edit Translations</a></li>
            <li><a href="api/translations.php" style="color: #4ecca3;">API Endpoint</a></li>
        </ul>
    </div>
</div>
</body>
</html>
