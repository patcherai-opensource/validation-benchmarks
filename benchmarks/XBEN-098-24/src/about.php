<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - DBAdmin</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
        <img src="images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about.php">About</a></li>
            <li><a href="/contact.php">Contact</a></li>
            <li><a href="/connect.php">Connect</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>About DBAdmin</h1>
        <p>
        DBAdmin is a lightweight, web-based database administration tool designed for developers, database administrators, and DevOps engineers who need quick and efficient access to MySQL databases. Built with simplicity and performance in mind, DBAdmin provides essential database management functionality without the overhead of larger enterprise tools.
        </p>
        
        <h3>Why DBAdmin?</h3>
        <p>
        Managing databases across multiple environments can be challenging. Whether you're working with local development databases, staging servers, or production systems, DBAdmin provides a unified interface for all your database management needs. Simply point it to any MySQL-compatible server and start working immediately.
        <br/><br/>
        Unlike desktop-based tools, DBAdmin runs in your browser, making it accessible from anywhere. This is particularly useful for managing databases on remote servers or in cloud environments where installing local tools isn't practical.
        </p>
        
        <h3>Features</h3>
        <ul style="color: #ccc; line-height: 1.8;">
            <li>Connect to any MySQL server (local, remote, cloud-hosted)</li>
            <li>Browse and manage databases and tables</li>
            <li>Execute SQL queries with syntax highlighting</li>
            <li>Import and export data in multiple formats</li>
            <li>View and edit table data directly</li>
            <li>Manage user permissions and privileges</li>
        </ul>
        
        <h3>System Requirements</h3>
        <p>
        DBAdmin requires PHP 7.0 or later with the mysqli extension enabled. It works with MySQL 5.6 and later, including MariaDB and other MySQL-compatible databases.
        </p>
        
        <h3>Security</h3>
        <p>
        DBAdmin is designed for internal use within trusted networks. When deploying in production environments, ensure proper network security measures are in place, including firewalls and access controls. Never expose DBAdmin directly to the public internet without proper authentication.
        </p>
    </div>
</body>
</html>

