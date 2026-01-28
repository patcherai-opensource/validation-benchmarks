<?php
session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: login.php");
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alerts - NetWatch Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f1a;
            color: #fff;
            min-height: 100vh;
        }
        .navbar {
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .navbar h1 { color: #00d4ff; font-size: 22px; }
        .nav-links { display: flex; gap: 20px; align-items: center; }
        .nav-links a { color: #aaa; text-decoration: none; padding: 8px 16px; border-radius: 6px; transition: all 0.3s; }
        .nav-links a:hover, .nav-links a.active { background: rgba(0,212,255,0.1); color: #00d4ff; }
        .user-info { display: flex; align-items: center; gap: 15px; }
        .user-info span { color: #888; }
        .logout-btn { 
            background: rgba(255,0,0,0.1); 
            color: #ff6b6b; 
            padding: 8px 16px; 
            border-radius: 6px; 
            text-decoration: none;
        }
        .container { padding: 30px; max-width: 1400px; margin: 0 auto; }
        .page-header { margin-bottom: 30px; }
        .page-header h2 { font-size: 24px; margin-bottom: 10px; }
        .page-header p { color: #888; }
        .empty-state {
            text-align: center;
            padding: 80px 40px;
            background: rgba(255,255,255,0.02);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .empty-state h3 { color: #00ff88; margin-bottom: 15px; font-size: 20px; }
        .empty-state p { color: #888; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>🌐 NetWatch Pro</h1>
        <div class="nav-links">
            <a href="dashboard.php">Dashboard</a>
            <a href="devices.php">Devices</a>
            <a href="search.php">MAC Search</a>
            <a href="alerts.php" class="active">Alerts</a>
            <a href="settings.php">Settings</a>
        </div>
        <div class="user-info">
            <span>Welcome, <?= htmlspecialchars($_SESSION['username']) ?></span>
            <a href="logout.php" class="logout-btn">Logout</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="page-header">
            <h2>⚠️ Alert History</h2>
            <p>Recent network alerts and notifications</p>
        </div>
        
        <div class="empty-state">
            <h3>✓ All Systems Operational</h3>
            <p>No alerts have been triggered in the last 24 hours.</p>
        </div>
    </div>
</body>
</html>
