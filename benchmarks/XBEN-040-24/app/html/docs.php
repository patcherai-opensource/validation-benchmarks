<?php
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation - SubSite Manager</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Documentation</h1>
    <p class="subtitle">SubSite Manager v3.2.1 Documentation</p>
    
    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="subsites.php">SubSites</a>
        <a href="groups.php">Groups</a>
        <a href="members.php">Members</a>
        <a href="settings.php">Settings</a>
        <a href="cms-admin.php">CMS Admin</a>
    </nav>

    <div class="doc-section">
        <h2>Getting Started</h2>
        <p>SubSite Manager allows you to manage multiple websites from a single installation. Each subsite can have its own theme, content, and user groups.</p>
        
        <h3>Key Features</h3>
        <ul>
            <li>Multi-tenant architecture</li>
            <li>Granular permission system via Groups</li>
            <li>Theme customization per subsite</li>
            <li>Centralized member management</li>
            <li>API access for integrations</li>
        </ul>
    </div>

    <div class="doc-section">
        <h2>Group Management</h2>
        <p>Groups control access permissions across subsites. Use the <code>group_class</code> parameter to specify which type of group table to query.</p>
        
        <h3>Available Group Classes</h3>
        <ul>
            <li><code>user_groups</code> - Standard user permissions</li>
            <li><code>admin_groups</code> - Administrative permissions</li>
            <li><code>content_groups</code> - Content editing permissions</li>
        </ul>
        
        <h3>Administrative Actions</h3>
        <p>The "Initialize Default Records" action sets up group-subsite relationships for migration purposes. This copies group assignments to the Group_Subsites junction table.</p>
    </div>

    <div class="doc-section">
        <h2>API Endpoints</h2>
        <p>See the <a href="api.php">API Reference</a> for available endpoints.</p>
    </div>
</div>

<footer>
    <p>&copy; 2024 SubSite Manager v3.2.1</p>
</footer>
</body>
</html>
