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

// Get translations
$sql = "SELECT * FROM translations ORDER BY locale, domain, trans_key LIMIT 100";
$result = $conn->query($sql);
$translations = [];
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $translations[] = $row;
    }
}

$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LocaleCMS - Translations</title>
    <link rel="stylesheet" href="../styles.css">
</head>
<body>
<div class="container admin-container">
    <div class="header">
        <h1>🌐 Translation Manager</h1>
        <p class="tagline">Manage your localization strings</p>
    </div>
    
    <div class="nav-links">
        <a href="dashboard.php">Dashboard</a>
        <a href="translations.php">Manage Translations</a>
        <a href="logout.php">Logout</a>
    </div>

    <div class="api-section">
        <h3>API Filter Example</h3>
        <p>Use the API endpoint with advanced filtering:</p>
        <code>curl -X POST /admin/api/translations.php -d 'filter=[{"property":"locale","type":"string","value":"en_US"}]'</code>
    </div>

    <div class="info-section">
        <h3>Translation Data</h3>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Locale</th>
                    <th>Key</th>
                    <th>Value</th>
                    <th>Domain</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($translations as $t): ?>
                <tr>
                    <td><?php echo htmlspecialchars($t['id']); ?></td>
                    <td><?php echo htmlspecialchars($t['locale']); ?></td>
                    <td><?php echo htmlspecialchars($t['trans_key']); ?></td>
                    <td><?php echo htmlspecialchars(substr($t['trans_value'], 0, 50)); ?></td>
                    <td><?php echo htmlspecialchars($t['domain']); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
