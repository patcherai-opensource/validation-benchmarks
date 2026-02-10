<?php
session_start();

// Check if user is logged in
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

// Fetch devices
$result = $conn->query("SELECT * FROM devices ORDER BY hostname");
$devices = [];
while ($row = $result->fetch_assoc()) {
    $devices[] = $row;
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LibreNMS - Devices</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }
        .navbar {
            background: #16213e;
            color: #fff;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .navbar h1 { font-size: 22px; }
        .navbar h1 span { color: #e94560; }
        .navbar .user-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .navbar a {
            color: #fff;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 4px;
            transition: background 0.3s;
        }
        .navbar a:hover { background: rgba(255,255,255,0.1); }
        .navbar .logout { background: #e94560; }
        .navbar .logout:hover { background: #d63450; }
        
        .sidebar {
            position: fixed;
            left: 0;
            top: 60px;
            width: 220px;
            height: calc(100vh - 60px);
            background: #1a1a2e;
            padding: 20px 0;
        }
        .sidebar a {
            display: block;
            color: #aaa;
            text-decoration: none;
            padding: 12px 25px;
            transition: all 0.3s;
            border-left: 3px solid transparent;
        }
        .sidebar a:hover, .sidebar a.active {
            color: #fff;
            background: rgba(255,255,255,0.05);
            border-left-color: #e94560;
        }
        .sidebar .section-title {
            color: #666;
            font-size: 11px;
            text-transform: uppercase;
            padding: 20px 25px 10px;
            letter-spacing: 1px;
        }
        
        .main-content {
            margin-left: 220px;
            padding: 30px;
            margin-top: 60px;
        }
        .card {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            padding: 25px;
            margin-bottom: 20px;
        }
        .card h2 {
            color: #16213e;
            margin-bottom: 20px;
            font-size: 18px;
            border-bottom: 2px solid #e94560;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e1e1e1;
        }
        th {
            background: #16213e;
            color: #fff;
            font-weight: 500;
        }
        tr:hover {
            background: #f9f9f9;
        }
        .status-up { color: #28a745; }
        .status-down { color: #dc3545; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>Libre<span>NMS</span></h1>
        <div class="user-info">
            <span>Welcome, <?php echo htmlspecialchars($_SESSION['realname'] ?? $_SESSION['username']); ?></span>
            <a href="logout.php" class="logout">Logout</a>
        </div>
    </nav>
    
    <div class="sidebar">
        <div class="section-title">Overview</div>
        <a href="index.php">Dashboard</a>
        <a href="devices.php" class="active">Devices</a>
        
        <div class="section-title">Search</div>
        <a href="search.php?type=ipv4">IPv4 Address</a>
        <a href="search.php?type=ipv6">IPv6 Address</a>
        <a href="search.php?type=mac">MAC Address</a>
        <a href="search.php?type=arp">ARP Table</a>
        
        <div class="section-title">Reports</div>
        <a href="#">Alerts</a>
        <a href="#">Eventlog</a>
    </div>
    
    <main class="main-content">
        <div class="card">
            <h2>All Devices</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Hostname</th>
                        <th>sysName</th>
                        <th>IP Address</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($devices as $device): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($device['device_id']); ?></td>
                        <td><?php echo htmlspecialchars($device['hostname']); ?></td>
                        <td><?php echo htmlspecialchars($device['sysName']); ?></td>
                        <td><?php echo htmlspecialchars($device['ip']); ?></td>
                        <td class="<?php echo $device['status'] == 1 ? 'status-up' : 'status-down'; ?>">
                            <?php echo $device['status'] == 1 ? 'Up' : 'Down'; ?>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>
