<?php session_start();?> 
<!DOCTYPE html>
<html>
<head>
    <title>AssetCore Manager - Digital Asset Management</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; }
        h3 { color: #34495e; margin-top: 30px; }
        .nav-link { display: block; padding: 10px 15px; margin: 5px 0; background: #3498db; color: white; text-decoration: none; border-radius: 4px; }
        .nav-link:hover { background: #2980b9; }
        .info-box { background: #ecf0f1; padding: 15px; border-radius: 4px; margin-top: 20px; }
        code { background: #e8e8e8; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗄️ AssetCore Manager</h1>
        <p>Enterprise Digital Asset Management System v3.2.1</p>
        
        <h3>Asset Operations</h3>
        <a class="nav-link" href="/api/uuid.php">UUID Asset Lookup</a>
        <a class="nav-link" href="/assets.php">Browse Assets</a>
        
        <div class="info-box">
            <strong>API Documentation:</strong><br>
            Use the UUID Lookup API to retrieve asset details by their unique identifier.<br>
            Example: <code>GET /api/uuid.php?uuid=YOUR-ASSET-UUID</code>
        </div>
    </div>
</body>
</html>
