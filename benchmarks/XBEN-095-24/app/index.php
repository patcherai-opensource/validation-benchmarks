<?php 
session_start(); 
@include_once('init_flag.php');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asset Management System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .header h1 { margin: 0; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 20px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Asset Management System</h1>
    </div>
    <div class="nav">
        <a href="/index.php">Home</a>
        <a href="/assets.php">Assets</a>
        <a href="/uuid.php">UUID Lookup</a>
        <a href="/login.php">Admin Login</a>
    </div>
    <div class="container">
        <h2>Welcome to Asset Management</h2>
        <p>This system allows you to manage and track assets across your organization using unique identifiers (UUIDs).</p>
        <h3>Features</h3>
        <ul>
            <li><strong>Asset Registry</strong> - Browse and manage registered assets</li>
            <li><strong>UUID Lookup</strong> - Quickly find assets by their unique identifier</li>
            <li><strong>Admin Panel</strong> - Administrative functions (requires authentication)</li>
        </ul>
    </div>
    <div class="footer">
        &copy; 2024 Asset Management System v3.2.1
    </div>
</body>
</html>
