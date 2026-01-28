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

// Get device count
$deviceCount = $conn->query("SELECT COUNT(*) as cnt FROM devices")->fetch_assoc()['cnt'];
$interfaceCount = $conn->query("SELECT COUNT(*) as cnt FROM interfaces")->fetch_assoc()['cnt'];
$activeDevices = $conn->query("SELECT COUNT(*) as cnt FROM devices WHERE status = 'active'")->fetch_assoc()['cnt'];

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - NetWatch Pro</title>
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
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .stat-card h3 { color: #888; font-size: 14px; margin-bottom: 10px; }
        .stat-card .value { font-size: 36px; font-weight: 700; color: #00d4ff; }
        .section-title { font-size: 20px; margin-bottom: 20px; color: #fff; }
        .quick-links { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .quick-link {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 20px;
            text-decoration: none;
            color: #fff;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s;
        }
        .quick-link:hover { background: rgba(0,212,255,0.1); border-color: #00d4ff; }
        .quick-link h4 { margin-bottom: 8px; }
        .quick-link p { color: #888; font-size: 13px; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>🌐 NetWatch Pro</h1>
        <div class="nav-links">
            <a href="dashboard.php" class="active">Dashboard</a>
            <a href="devices.php">Devices</a>
            <a href="search.php">MAC Search</a>
            <a href="alerts.php">Alerts</a>
            <a href="settings.php">Settings</a>
        </div>
        <div class="user-info">
            <span>Welcome, <?= htmlspecialchars($_SESSION['username']) ?></span>
            <a href="logout.php" class="logout-btn">Logout</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Devices</h3>
                <div class="value"><?= $deviceCount ?></div>
            </div>
            <div class="stat-card">
                <h3>Active Devices</h3>
                <div class="value"><?= $activeDevices ?></div>
            </div>
            <div class="stat-card">
                <h3>Network Interfaces</h3>
                <div class="value"><?= $interfaceCount ?></div>
            </div>
            <div class="stat-card">
                <h3>System Status</h3>
                <div class="value" style="color: #00ff88;">Online</div>
            </div>
        </div>
        
        <h2 class="section-title">Quick Actions</h2>
        <div class="quick-links">
            <a href="devices.php" class="quick-link">
                <h4>📡 Device List</h4>
                <p>View all monitored network devices</p>
            </a>
            <a href="search.php" class="quick-link">
                <h4>🔍 MAC Address Search</h4>
                <p>Search interfaces by MAC address</p>
            </a>
            <a href="alerts.php" class="quick-link">
                <h4>⚠️ Alert History</h4>
                <p>View recent network alerts</p>
            </a>
            <a href="settings.php" class="quick-link">
                <h4>⚙️ System Settings</h4>
                <p>Configure monitoring parameters</p>
            </a>
        </div>
    </div>
</body>
</html>
