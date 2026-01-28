<?php session_start();?> 
<!DOCTYPE html>
<html>
<head>
    <title>AssetCore - Digital Asset Management</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .nav-links { margin-top: 20px; }
        .nav-links a { display: block; padding: 12px 15px; margin: 8px 0; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        .nav-links a:hover { background: #0056b3; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AssetCore Digital Asset Management</h1>
        <p>Welcome to AssetCore - Your centralized platform for managing digital assets and resources.</p>
        
        <div class="nav-links">
            <a href="/assets.php">Browse Assets</a>
            <a href="/uuid.php">UUID Lookup</a>
            <a href="/api/status.php">System Status</a>
            <a href="/admin/">Admin Panel</a>
        </div>
        
        <div class="footer">
            <p>AssetCore v2.4.1 | &copy; 2024 AssetCore Inc.</p>
        </div>
    </div>
</body>
</html>
