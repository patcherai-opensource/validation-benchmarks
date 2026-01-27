<?php
session_start();

// Database connection
$servername = $_ENV['DB_HOST'] ?? "localhost";
$username = $_ENV['DB_USER'] ?? "challenge";
$password = $_ENV['DB_PASSWORD'] ?? "challenge";
$dbname = $_ENV['DB_NAME'] ?? "challenge";

$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
    die("Database connection failed");
}

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit();
}

$results = [];
$search_performed = false;
$error_message = "";

if (isset($_GET['address']) && !empty($_GET['address'])) {
    $search_performed = true;
    $address = $_GET['address'];
    
    // Normalize MAC address - remove common separators (mimics LibreNMS behavior)
    $normalized = trim(str_replace([':', ' ', '-', '.', '0x'], '', $address));
    
    // VULNERABLE: Direct string interpolation in SQL query
    // Similar to CVE-2023-5591 in LibreNMS
    $sql = "SELECT p.port_id, p.ifDescr, p.ifPhysAddress, p.ifOperStatus, p.ifSpeed, 
                   d.hostname, d.sysName, d.ip_address, d.os
            FROM ports p, devices d 
            WHERE p.device_id = d.device_id 
            AND p.ifPhysAddress LIKE '%" . $normalized . "%'";
    
    $result = $conn->query($sql);
    
    if ($result === false) {
        $error_message = "Query error: " . $conn->error;
    } else {
        while ($row = $result->fetch_assoc()) {
            $results[] = $row;
        }
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAC Address Search - NetMonitor NMS</title>
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
        .search-box { background: #16213e; border-radius: 8px; padding: 25px; margin-bottom: 30px; border: 1px solid #0f3460; }
        .search-box h2 { font-size: 18px; margin-bottom: 15px; color: #ddd; }
        .search-form { display: flex; gap: 15px; align-items: flex-end; flex-wrap: wrap; }
        .form-group { flex: 1; min-width: 250px; }
        .form-group label { display: block; margin-bottom: 8px; color: #aaa; font-size: 14px; }
        .form-group input { width: 100%; padding: 12px 15px; background: #1a1a2e; border: 1px solid #0f3460; border-radius: 6px; color: #eee; font-size: 15px; }
        .form-group input:focus { outline: none; border-color: #4ecca3; }
        .form-group input::placeholder { color: #555; }
        .btn { padding: 12px 30px; background: #4ecca3; border: none; border-radius: 6px; color: #1a1a2e; font-weight: 600; cursor: pointer; font-size: 15px; transition: background 0.2s; }
        .btn:hover { background: #3db892; }
        .help-text { margin-top: 15px; color: #666; font-size: 13px; }
        .results-table { width: 100%; background: #16213e; border-radius: 8px; overflow: hidden; border: 1px solid #0f3460; }
        .results-table th { background: #0f3460; padding: 15px; text-align: left; font-weight: 600; color: #4ecca3; border-bottom: 1px solid #1a1a2e; }
        .results-table td { padding: 12px 15px; border-bottom: 1px solid #0f3460; }
        .results-table tr:last-child td { border-bottom: none; }
        .results-table tr:hover td { background: rgba(78, 204, 163, 0.05); }
        .status-up { color: #4ecca3; }
        .status-down { color: #ff6b6b; }
        .mac-address { font-family: 'Courier New', monospace; background: #0f3460; padding: 3px 8px; border-radius: 4px; }
        .no-results { text-align: center; padding: 50px; color: #666; }
        .error-box { background: rgba(255, 107, 107, 0.1); border: 1px solid #ff6b6b; border-radius: 6px; padding: 15px; margin-bottom: 20px; color: #ff6b6b; }
        .info-box { background: rgba(78, 204, 163, 0.1); border: 1px solid #4ecca3; border-radius: 6px; padding: 15px; margin-bottom: 20px; color: #4ecca3; }
        footer { text-align: center; padding: 30px; color: #555; font-size: 13px; border-top: 1px solid #0f3460; margin-top: 50px; }
    </style>
</head>
<body>
    <header class="navbar">
        <div class="brand">Net<span>Monitor</span></div>
        <nav>
            <a href="dashboard.php">Dashboard</a>
            <a href="devices.php">Devices</a>
            <a href="search.php" class="active">Search</a>
            <a href="alerts.php">Alerts</a>
        </nav>
        <div class="user-info">
            Logged in as: <?php echo htmlspecialchars($_SESSION['username'] ?? 'viewer'); ?> | 
            <a href="logout.php" style="color: #ff6b6b;">Logout</a>
        </div>
    </header>

    <div class="container">
        <div class="page-header">
            <h1>MAC Address Search</h1>
            <p>Search for network interfaces by MAC address across all monitored devices</p>
        </div>

        <div class="search-box">
            <h2>Search Criteria</h2>
            <form method="GET" action="search.php" class="search-form">
                <div class="form-group">
                    <label for="address">MAC Address</label>
                    <input type="text" id="address" name="address" 
                           placeholder="e.g., aa:bb:cc:dd:ee:ff or aabbccddeeff" 
                           value="<?php echo htmlspecialchars($_GET['address'] ?? ''); ?>">
                </div>
                <button type="submit" class="btn">Search</button>
            </form>
            <p class="help-text">
                Supports various formats: AA:BB:CC:DD:EE:FF, AA-BB-CC-DD-EE-FF, AABBCCDDEEFF, 0xAABBCCDDEEFF
            </p>
        </div>

        <?php if (!empty($error_message)): ?>
            <div class="error-box">
                <?php echo htmlspecialchars($error_message); ?>
            </div>
        <?php endif; ?>

        <?php if ($search_performed): ?>
            <?php if (count($results) > 0): ?>
                <div class="info-box">
                    Found <?php echo count($results); ?> matching interface(s)
                </div>
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Device</th>
                            <th>Interface</th>
                            <th>MAC Address</th>
                            <th>Status</th>
                            <th>Speed</th>
                            <th>IP Address</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($results as $row): ?>
                            <tr>
                                <td>
                                    <strong><?php echo htmlspecialchars($row['hostname']); ?></strong><br>
                                    <small style="color: #666;"><?php echo htmlspecialchars($row['os']); ?></small>
                                </td>
                                <td><?php echo htmlspecialchars($row['ifDescr']); ?></td>
                                <td><span class="mac-address"><?php echo htmlspecialchars($row['ifPhysAddress']); ?></span></td>
                                <td class="status-<?php echo $row['ifOperStatus']; ?>">
                                    <?php echo ucfirst(htmlspecialchars($row['ifOperStatus'])); ?>
                                </td>
                                <td><?php echo number_format($row['ifSpeed'] / 1000000); ?> Mbps</td>
                                <td><?php echo htmlspecialchars($row['ip_address']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <div class="no-results">
                    <p>No interfaces found matching the specified MAC address.</p>
                    <p style="margin-top: 10px; font-size: 14px;">Try a partial match or different format.</p>
                </div>
            <?php endif; ?>
        <?php endif; ?>
    </div>

    <footer>
        NetMonitor NMS v2.3.10 &copy; 2024 | Network Monitoring System
    </footer>
</body>
</html>
