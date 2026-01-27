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

$devices = [];
$conn = new mysqli($servername, $username, $password, $dbname);
if (!$conn->connect_error) {
    $result = $conn->query("SELECT d.*, (SELECT COUNT(*) FROM ports p WHERE p.device_id = d.device_id) as port_count FROM devices d ORDER BY hostname");
    while ($row = $result->fetch_assoc()) {
        $devices[] = $row;
    }
    $conn->close();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Devices - NetMonitor NMS</title>
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
        .results-table { width: 100%; background: #16213e; border-radius: 8px; overflow: hidden; border: 1px solid #0f3460; }
        .results-table th { background: #0f3460; padding: 15px; text-align: left; font-weight: 600; color: #4ecca3; }
        .results-table td { padding: 12px 15px; border-bottom: 1px solid #0f3460; }
        .results-table tr:last-child td { border-bottom: none; }
        .status-1 { color: #4ecca3; }
        .status-0 { color: #ff6b6b; }
        footer { text-align: center; padding: 30px; color: #555; font-size: 13px; border-top: 1px solid #0f3460; margin-top: 50px; }
    </style>
</head>
<body>
    <header class="navbar">
        <div class="brand">Net<span>Monitor</span></div>
        <nav>
            <a href="dashboard.php">Dashboard</a>
            <a href="devices.php" class="active">Devices</a>
            <a href="search.php">Search</a>
            <a href="alerts.php">Alerts</a>
        </nav>
        <div class="user-info">
            Logged in as: <?php echo htmlspecialchars($_SESSION['username']); ?> | 
            <a href="logout.php" style="color: #ff6b6b;">Logout</a>
        </div>
    </header>

    <div class="container">
        <div class="page-header">
            <h1>Network Devices</h1>
            <p>All monitored network devices</p>
        </div>

        <table class="results-table">
            <thead>
                <tr>
                    <th>Hostname</th>
                    <th>System Name</th>
                    <th>IP Address</th>
                    <th>OS</th>
                    <th>Ports</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($devices as $device): ?>
                <tr>
                    <td><strong><?php echo htmlspecialchars($device['hostname']); ?></strong></td>
                    <td><?php echo htmlspecialchars($device['sysName']); ?></td>
                    <td><?php echo htmlspecialchars($device['ip_address']); ?></td>
                    <td><?php echo htmlspecialchars($device['os']); ?></td>
                    <td><?php echo $device['port_count']; ?></td>
                    <td class="status-<?php echo $device['status']; ?>">
                        <?php echo $device['status'] == 1 ? 'Online' : 'Offline'; ?>
                    </td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>

    <footer>
        NetMonitor NMS v2.3.10 &copy; 2024 | Network Monitoring System
    </footer>
</body>
</html>
