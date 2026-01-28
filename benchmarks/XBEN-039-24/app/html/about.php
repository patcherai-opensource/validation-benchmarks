<?php
$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'blogDB');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ezPortal CMS - About</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>ezPortal CMS</h1>
        <p class="tagline">Enterprise Content Management System</p>
    </div>
    
    <nav class="main-nav">
        <a href="index.php">Home</a>
        <a href="articles.php">Articles</a>
        <a href="about.php">About</a>
        <a href="login.php">Staff Login</a>
    </nav>

    <div class="content-area">
        <h2>About ezPortal CMS</h2>
        
        <div class="about-section">
            <h3>Overview</h3>
            <p>ezPortal CMS is an enterprise-grade content management system built for organizations that need flexible authentication and robust content publishing workflows.</p>
        </div>
        
        <div class="about-section">
            <h3>Features</h3>
            <ul>
                <li>Multi-handler authentication (Standard, LDAP, TextFile)</li>
                <li>Role-based access control</li>
                <li>Content versioning and workflow</li>
                <li>API-first architecture</li>
                <li>Extensible plugin system</li>
            </ul>
        </div>
        
        <div class="about-section">
            <h3>System Information</h3>
            <table class="info-table">
                <tr><td>Version:</td><td>4.2.1</td></tr>
                <tr><td>Build:</td><td>20240115</td></tr>
                <tr><td>License:</td><td>Enterprise</td></tr>
            </table>
        </div>
        
        <div class="about-section">
            <h3>Authentication Configuration</h3>
            <p>This installation is configured with the following login handlers:</p>
            <ul>
                <li><strong>Standard Handler:</strong> Database-backed authentication with MD5 password hashing</li>
                <li><strong>LDAP Handler:</strong> Directory service integration for enterprise SSO</li>
            </ul>
            <p><em>Note: Users with password_hash_type=0 are managed by external authentication providers.</em></p>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2024 ezPortal CMS. Powered by ezPublish Legacy Framework.</p>
    </footer>
</div>
</body>
</html>
<?php $conn->close(); ?>
