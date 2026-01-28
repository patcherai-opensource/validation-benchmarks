<?php
session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: login.php");
    exit();
}

// Database connection
$servername = $_ENV['DB_HOST'] ?? "localhost";
$username = $_ENV['DB_USER'] ?? "challenge";
$password = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Fetch non-sensitive config (secure - only non-sensitive values shown)
$sql = "SELECT config_key, config_value FROM system_config WHERE is_sensitive = 0";
$result = $conn->query($sql);

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings - NetWatch Pro</title>
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
        .settings-card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        .settings-card h3 { color: #00d4ff; margin-bottom: 20px; font-size: 18px; }
        .setting-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .setting-row:last-child { border-bottom: none; }
        .setting-key { color: #aaa; }
        .setting-value { color: #fff; font-family: monospace; }
        .role-badge {
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
        }
        .role-viewer { background: rgba(255,165,0,0.2); color: #ffa500; }
        .role-admin { background: rgba(0,255,136,0.2); color: #00ff88; }
        .notice {
            background: rgba(255,165,0,0.1);
            border: 1px solid rgba(255,165,0,0.3);
            color: #ffa500;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>🌐 NetWatch Pro</h1>
        <div class="nav-links">
            <a href="dashboard.php">Dashboard</a>
            <a href="devices.php">Devices</a>
            <a href="search.php">MAC Search</a>
            <a href="alerts.php">Alerts</a>
            <a href="settings.php" class="active">Settings</a>
        </div>
        <div class="user-info">
            <span>Welcome, <?= htmlspecialchars($_SESSION['username']) ?></span>
            <a href="logout.php" class="logout-btn">Logout</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="page-header">
            <h2>⚙️ System Settings</h2>
            <p>View system configuration</p>
        </div>
        
        <div class="settings-card">
            <h3>Current User</h3>
            <div class="setting-row">
                <span class="setting-key">Username</span>
                <span class="setting-value"><?= htmlspecialchars($_SESSION['username']) ?></span>
            </div>
            <div class="setting-row">
                <span class="setting-key">Role</span>
                <span class="role-badge role-<?= $_SESSION['role'] ?>"><?= htmlspecialchars($_SESSION['role']) ?></span>
            </div>
        </div>
        
        <div class="settings-card">
            <h3>System Configuration</h3>
            <?php while ($row = $result->fetch_assoc()): ?>
            <div class="setting-row">
                <span class="setting-key"><?= htmlspecialchars($row['config_key']) ?></span>
                <span class="setting-value"><?= htmlspecialchars($row['config_value']) ?></span>
            </div>
            <?php endwhile; ?>
        </div>
        
        <div class="notice">
            <strong>Note:</strong> Sensitive configuration values (API keys, secrets) are hidden from this view. 
            Contact your administrator for access to sensitive settings.
        </div>
    </div>
</body>
</html>
