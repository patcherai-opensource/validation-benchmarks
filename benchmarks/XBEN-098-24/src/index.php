<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DBAdmin - Database Administration Tool</title>
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
        <h1>Welcome to DBAdmin</h1>
        <h2>Lightweight Database Administration</h2>
        <p>
        DBAdmin is a powerful, lightweight database administration tool designed for developers and database administrators who need quick and easy access to their MySQL databases. With its intuitive web-based interface, DBAdmin allows you to connect to any MySQL server, browse databases, execute queries, and manage your data efficiently.
        </p>
        <h3>Key Features</h3>
        <ul style="color: #ccc; line-height: 1.8;">
            <li>Connect to any MySQL server with custom host and port settings</li>
            <li>Browse databases, tables, and view table structures</li>
            <li>Execute SQL queries directly from your browser</li>
            <li>Import and export data with ease</li>
            <li>Lightweight and fast - no heavy dependencies</li>
            <li>Works with MySQL 5.x and 8.x servers</li>
        </ul>
        <p>
        Whether you're managing a local development database or connecting to remote production servers, DBAdmin provides the flexibility and power you need. Simply navigate to the <a href="/connect.php" style="color: #C7FF6D;">Connect</a> page to get started.
        </p>
        <h3>Getting Started</h3>
        <p>
        To connect to a database server, you'll need the following information:
        </p>
        <ul style="color: #ccc; line-height: 1.8;">
            <li><strong>Server:</strong> The hostname or IP address of your MySQL server</li>
            <li><strong>Port:</strong> The port number (default: 3306)</li>
            <li><strong>Username:</strong> Your MySQL username</li>
            <li><strong>Password:</strong> Your MySQL password</li>
        </ul>
        <p>
        DBAdmin supports connecting to both local and remote MySQL servers. For security, we recommend using strong passwords and limiting network access to your database servers.
        </p>
    </div>
</body>
</html>
