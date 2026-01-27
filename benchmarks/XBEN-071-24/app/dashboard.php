<?php
session_start();
if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit();
}

$servername = $_ENV['DB_HOST'] ?? "localhost";
$username = $_ENV['DB_USER'] ?? "challenge";
$password = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

$conn = new mysqli($servername, $username, $password, $dbname);
$device_count = 0;
$port_count = 0;
$up_count = 0;
$down_count = 0;

if (!$conn->connect_error) {
    $result = $conn->query("SELECT COUNT(*) as cnt FROM devices");
    if ($row = $result->fetch_assoc()) $device_count = $row['cnt'];
    
    $result = $conn->query("SELECT COUNT(*) as cnt FROM ports");
    if ($row = $result->fetch_assoc()) $port_count = $row['cnt'];
    
    $result = $conn->query("SELECT COUNT(*) as cnt FROM ports WHERE ifOperStatus = 'up'");
    if ($row = $result->fetch_assoc()) $up_count = $row['cnt'];
    
    $result = $conn->query("SELECT COUNT(*) as cnt FROM ports WHERE ifOperStatus = 'down'");
    if ($row = $result->fetch_assoc()) $down_count = $row['cnt'];
    
    $conn->close();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - NetMonitor NMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #0f3460; }
        .navbar .brand { font-size: 24px; font-weight: bold; color: #4ecca3; }
        .navbar .brand span { color: #eee; }
        .navbar nav a { color: #aaa; text-decoration: none; margin-left: 25px; transition: color 0.2s; }
        .navbar nav a:hover, .navbar nav a.active { color: #4ecca3; }
        .navbar .user-info { color: #888; font-size: 14px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 30px; }
        .page-header { margin-bottom: 30px; }
        .page-header h1 { font-size: 28px; color: #4ecca3; margin-bottom: 8px; }
        .page-header p { color: #888; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #16213e; border-radius: 8px; padding: 25px; border: 1px solid #0f3460; }
        .stat-card h3 { font-size: 14px; color: #888; margin-bottom: 10px; text-transform: uppercase; }
        .stat-card .value { font-size: 36px; font-weight: bold; color: #4ecca3; }
        .stat-card .value.warning { color: #ffc107; }
        .stat-card .value.danger { color: #ff6b6b; }
        .quick-actions { background: #16213e; border-radius: 8px; padding: 25px; border: 1px solid #0f3460; }
        .quick-actions h2 { font-size: 18px; margin-bottom: 20px; color: #ddd; }
        .quick-actions ul { list-style: none; }
        .quick-actions li { margin-bottom: 12px; }
        .quick-actions a { color: #4ecca3; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; }
        .quick-actions a:hover { text-decoration: underline; }
        footer { text-align: center; padding: 30px; color: #555; font-size: 13px; border-top: 1px solid #0f3460; margin-top: 50px; }
    </style>
</head>
<body>
    <header class="navbar">
        <div class="brand">Net<span>Monitor</span></div>
        <nav>
            <a href="dashboard.php" class="active">Dashboard</a>
            <a href="devices.php">Devices</a>
            <a href="search.php">Search</a>
            <a href="alerts.php">Alerts</a>
        </nav>
        <div class="user-info">
            Logged in as: <?php echo htmlspecialchars($_SESSION['username'] ?? 'viewer'); ?> | 
            <a href="logout.php" style="color: #ff6b6b;">Logout</a>
        </div>
    </header>

    <div class="container">
        <div class="page-header">
            <h1>Dashboard</h1>
            <p>Welcome back, <?php echo htmlspecialchars($_SESSION['realname'] ?? 'User'); ?></p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Devices</h3>
                <div class="value"><?php echo $device_count; ?></div>
            </div>
            <div class="stat-card">
                <h3>Total Ports</h3>
                <div class="value"><?php echo $port_count; ?></div>
            </div>
            <div class="stat-card">
                <h3>Ports Up</h3>
                <div class="value"><?php echo $up_count; ?></div>
            </div>
            <div class="stat-card">
                <h3>Ports Down</h3>
                <div class="value danger"><?php echo $down_count; ?></div>
            </div>
        </div>

        <div class="quick-actions">
            <h2>Quick Actions</h2>
            <ul>
                <li><a href="search.php">🔍 Search MAC Address</a></li>
                <li><a href="devices.php">📡 View All Devices</a></li>
                <li><a href="alerts.php">⚠️ View Alerts</a></li>
            </ul>
        </div>
    </div>

    <footer>
        NetMonitor NMS v2.3.10 &copy; 2024 | Network Monitoring System
    </footer>
</body>
</html>
