<?php session_start();?> 
<!DOCTYPE html>
<html>
<head>
    <title>Customer Management Framework</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .nav { margin: 20px 0; }
        .nav a { display: inline-block; padding: 10px 20px; margin-right: 10px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
        .nav a:hover { background: #0056b3; }
        .info { background: #e9ecef; padding: 15px; border-radius: 4px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Customer Management Framework</h1>
        <div class="nav">
            <a href="/login.php">Admin Login</a>
            <a href="/search.php">Public Search</a>
        </div>
        <div class="info">
            <p><strong>Welcome to the Customer Management Framework</strong></p>
            <p>This system provides tools for customer segmentation and management.</p>
            <p>Admin users can access the segment assignment interface after logging in.</p>
        </div>
    </div>
</body>
</html>
