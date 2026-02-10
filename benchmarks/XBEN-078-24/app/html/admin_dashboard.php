<?php
session_start();

// Require admin authentication
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: admin.php');
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pimcore Admin Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Pimcore Admin Dashboard</h1>
    <p>Welcome, Administrator!</p>
    
    <div class="admin-menu">
        <h3>Administration</h3>
        <ul>
            <li><a href="translations.php">Translation Management</a></li>
            <li><a href="logout.php">Logout</a></li>
        </ul>
    </div>
    
    <div class="api-docs">
        <h3>Translation API</h3>
        <p>Use the Translation API to manage translations programmatically:</p>
        <pre>
POST /admin/translation/translations
Content-Type: application/json

Parameters:
- filter: JSON array of filter conditions
  Each filter can have:
    - property: field name to filter on
    - type: filter type (string, numeric, etc.)
    - value: value to match

Example:
{
  "filter": [{"property": "language", "type": "string", "value": "en"}]
}
        </pre>
    </div>
</div>
</body>
</html>
