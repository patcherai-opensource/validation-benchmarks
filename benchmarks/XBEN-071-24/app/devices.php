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

// Fetch all devices with interface count
$sql = "SELECT d.*, COUNT(i.interface_id) as interface_count 
        FROM devices d 
        LEFT JOIN interfaces i ON d.device_id = i.device_id 
        GROUP BY d.device_id 
        ORDER BY d.hostname";
$result = $conn->query($sql);

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Device List - NetWatch Pro</title>
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
        .devices-table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(255,255,255,0.02);
            border-radius: 12px;
            overflow: hidden;
        }
        .devices-table th, .devices-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .devices-table th { 
            background: rgba(0,0,0,0.3); 
            color: #00d4ff;
            font-weight: 600;
        }
        .devices-table tr:hover { background: rgba(0,212,255,0.05); }
        .status-active { color: #00ff88; }
        .status-inactive { color: #ff6b6b; }
        .device-type {
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            background: rgba(0,212,255,0.1);
            color: #00d4ff;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>🌐 NetWatch Pro</h1>
        <div class="nav-links">
            <a href="dashboard.php">Dashboard</a>
            <a href="devices.php" class="active">Devices</a>
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
        <div class="page-header">
            <h2>📡 Network Devices</h2>
            <p>All monitored devices in the network</p>
        </div>
        
        <table class="devices-table">
            <thead>
                <tr>
                    <th>Hostname</th>
                    <th>IP Address</th>
                    <th>Type</th>
                    <th>Location</th>
                    <th>Status</th>
                    <th>Interfaces</th>
                </tr>
            </thead>
            <tbody>
                <?php while ($row = $result->fetch_assoc()): ?>
                <tr>
                    <td><strong><?= htmlspecialchars($row['hostname']) ?></strong></td>
                    <td><?= htmlspecialchars($row['ip_address']) ?></td>
                    <td><span class="device-type"><?= htmlspecialchars($row['device_type']) ?></span></td>
                    <td><?= htmlspecialchars($row['location']) ?></td>
                    <td class="<?= $row['status'] === 'active' ? 'status-active' : 'status-inactive' ?>">
                        <?= htmlspecialchars($row['status']) ?>
                    </td>
                    <td><?= $row['interface_count'] ?></td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>
</body>
</html>
