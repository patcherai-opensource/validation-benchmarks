<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LocaleCMS - Translation Management System</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🌐 LocaleCMS</h1>
        <p class="tagline">Enterprise Translation Management Platform v2.4.1</p>
    </div>

    <div class="info-section">
        <h2>About LocaleCMS</h2>
        <p>LocaleCMS is a powerful multilingual content management system designed for enterprise applications. 
        Manage translations across multiple locales, domains, and projects with ease.</p>
        
        <h3>Features</h3>
        <ul>
            <li>Multi-locale support (EN, DE, FR, ES, JP, and more)</li>
            <li>Domain-based translation organization</li>
            <li>Advanced filtering and search capabilities</li>
            <li>RESTful API for translation management</li>
            <li>Role-based access control</li>
        </ul>
    </div>

    <div class="stats-section">
        <h3>Platform Statistics</h3>
        <?php
        $conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
        if ($conn->connect_error) {
            echo "<p>Database connection unavailable</p>";
        } else {
            $result = $conn->query("SELECT COUNT(*) as total FROM translations");
            $row = $result->fetch_assoc();
            echo "<p>Total Translations: <strong>{$row['total']}</strong></p>";
            
            $result = $conn->query("SELECT COUNT(DISTINCT locale) as locales FROM translations");
            $row = $result->fetch_assoc();
            echo "<p>Active Locales: <strong>{$row['locales']}</strong></p>";
            
            $result = $conn->query("SELECT COUNT(DISTINCT domain) as domains FROM translations");
            $row = $result->fetch_assoc();
            echo "<p>Translation Domains: <strong>{$row['domains']}</strong></p>";
            
            $conn->close();
        }
        ?>
    </div>

    <div class="login-section">
        <h3>Administrator Access</h3>
        <p>Authorized personnel can access the translation management panel to manage localization data.</p>
        <a href="admin/login.php" class="btn">Admin Login</a>
    </div>

    <div class="api-section">
        <h3>API Documentation</h3>
        <p>Access translation data programmatically through our REST API endpoints.</p>
        <code>POST /admin/api/translations.php</code>
        <p class="hint">Authentication required. Use filter parameter for advanced queries.</p>
    </div>
</div>

<footer>
    <p>&copy; 2024 LocaleCMS - All rights reserved</p>
</footer>
</body>
</html>
