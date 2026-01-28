<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - DataLabel Studio</title>
    <link rel="stylesheet" href="../style.css">
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
        <img src="../images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/projects.php">Projects</a></li>
            <li><a href="/tasks.php">Tasks</a></li>
            <li><a href="/export.php">Export</a></li>
            <li><a href="/about.php">About</a></li>
            <li><a href="/login.php">Login</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>Admin Panel</h1>
        <p class="error">Access Denied. Administrator privileges required.</p>
        <p>Please <a href="/login.php">sign in</a> with an admin account.</p>
    </div>
</body>
</html>
