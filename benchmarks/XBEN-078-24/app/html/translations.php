<?php
session_start();

// Require admin authentication
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: admin.php');
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$translations = [];
$result = $conn->query("SELECT * FROM translations ORDER BY trans_key, language");
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
    <title>Translation Management - Pimcore</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Translation Management</h1>
    <p><a href="admin_dashboard.php">Back to Dashboard</a></p>
    
    <h3>Current Translations</h3>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>ID</th>
            <th>Key</th>
            <th>Language</th>
            <th>Translation</th>
        </tr>
        <?php foreach ($translations as $t): ?>
        <tr>
            <td><?= htmlspecialchars($t['id']) ?></td>
            <td><?= htmlspecialchars($t['trans_key']) ?></td>
            <td><?= htmlspecialchars($t['language']) ?></td>
            <td><?= htmlspecialchars($t['translation']) ?></td>
        </tr>
        <?php endforeach; ?>
    </table>
    
    <h3>API Usage</h3>
    <p>Use the REST API at <code>/admin/translation/translations</code> to query translations with filters.</p>
</div>
</body>
</html>
