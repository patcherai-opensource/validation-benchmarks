<?php
session_start();

if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: index.php");
    exit;
}

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'netmonDB';

$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    http_response_code(500);
    die("Service temporarily unavailable");
}

$device_id = isset($_GET['id']) ? intval($_GET['id']) : 0;
$device = null;
$packages = [];

if ($device_id > 0) {
    $stmt = $conn->prepare("SELECT * FROM devices WHERE device_id = ?");
    $stmt->bind_param("i", $device_id);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($result && $result->num_rows == 1) {
        $device = $result->fetch_assoc();
    }
    $stmt->close();
    
    if ($device) {
        $stmt = $conn->prepare("SELECT * FROM packages WHERE device_id = ? ORDER BY name");
        $stmt->bind_param("i", $device_id);
        $stmt->execute();
        $result = $stmt->get_result();
        while ($row = $result->fetch_assoc()) {
            $packages[] = $row;
        }
        $stmt->close();
    }
}

$conn->close();

if (!$device) {
    header("Location: devices.php");
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($device['hostname']); ?> - NetMon</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app-container">
    <nav class="sidebar">
        <div class="sidebar-header">
            <h2>NetMon</h2>
        </div>
        <ul class="nav-menu">
            <li class="nav-item"><a href="dashboard.php">Dashboard</a></li>
            <li class="nav-item active"><a href="devices.php">Devices</a></li>
            <li class="nav-item"><a href="alerts.php">Alerts</a></li>
            <li class="nav-item"><a href="search.php">Search</a></li>
            <li class="nav-item"><a href="index.php?logout=1">Logout</a></li>
        </ul>
        <div class="sidebar-footer">
            <p>Logged in as: <?php echo htmlspecialchars($_SESSION['username']); ?></p>
        </div>
    </nav>
    
    <main class="main-content">
        <header class="page-header">
            <h1><?php echo htmlspecialchars($device['hostname']); ?></h1>
            <p><a href="devices.php">&laquo; Back to Devices</a></p>
        </header>
        
        <section class="content-section">
            <h2>Device Information</h2>
            <table class="data-table">
                <tr><th>Hostname</th><td><?php echo htmlspecialchars($device['hostname']); ?></td></tr>
                <tr><th>System Name</th><td><?php echo htmlspecialchars($device['sysName']); ?></td></tr>
                <tr><th>IP Address</th><td><?php echo htmlspecialchars($device['ip_address']); ?></td></tr>
                <tr><th>Operating System</th><td><?php echo htmlspecialchars($device['os']); ?></td></tr>
                <tr><th>Version</th><td><?php echo htmlspecialchars($device['version']); ?></td></tr>
                <tr><th>Status</th><td><span class="badge <?php echo $device['status'] ? 'up' : 'down'; ?>"><?php echo $device['status'] ? 'Up' : 'Down'; ?></span></td></tr>
                <tr><th>Last Polled</th><td><?php echo $device['last_polled']; ?></td></tr>
            </table>
        </section>
        
        <?php if (count($packages) > 0): ?>
        <section class="content-section">
            <h2>Installed Packages</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Package</th>
                        <th>Version</th>
                        <th>Architecture</th>
                        <th>Build</th>
                        <th>Size</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($packages as $pkg): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($pkg['name']); ?></td>
                        <td><?php echo htmlspecialchars($pkg['version']); ?></td>
                        <td><?php echo htmlspecialchars($pkg['arch']); ?></td>
                        <td><?php echo htmlspecialchars($pkg['build']); ?></td>
                        <td><?php echo number_format($pkg['size']); ?> bytes</td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </section>
        <?php endif; ?>
    </main>
</div>
</body>
</html>
