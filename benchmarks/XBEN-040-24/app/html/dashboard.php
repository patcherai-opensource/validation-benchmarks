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

$device_count = 0;
$alert_count = 0;
$package_count = 0;

$result = $conn->query("SELECT COUNT(*) as cnt FROM devices WHERE status = 1");
if ($result) {
    $row = $result->fetch_assoc();
    $device_count = $row['cnt'];
}

$result = $conn->query("SELECT COUNT(*) as cnt FROM alerts WHERE state = 1");
if ($result) {
    $row = $result->fetch_assoc();
    $alert_count = $row['cnt'];
}

$result = $conn->query("SELECT COUNT(*) as cnt FROM packages");
if ($result) {
    $row = $result->fetch_assoc();
    $package_count = $row['cnt'];
}

$recent_alerts = [];
$result = $conn->query("SELECT a.*, d.hostname FROM alerts a JOIN devices d ON a.device_id = d.device_id WHERE a.state = 1 ORDER BY a.timestamp DESC LIMIT 5");
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $recent_alerts[] = $row;
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - NetMon</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app-container">
    <nav class="sidebar">
        <div class="sidebar-header">
            <h2>NetMon</h2>
        </div>
        <ul class="nav-menu">
            <li class="nav-item active"><a href="dashboard.php">Dashboard</a></li>
            <li class="nav-item"><a href="devices.php">Devices</a></li>
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
            <h1>Dashboard</h1>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Devices Online</h3>
                <span class="stat-value"><?php echo $device_count; ?></span>
            </div>
            <div class="stat-card alert">
                <h3>Active Alerts</h3>
                <span class="stat-value"><?php echo $alert_count; ?></span>
            </div>
            <div class="stat-card">
                <h3>Packages Tracked</h3>
                <span class="stat-value"><?php echo $package_count; ?></span>
            </div>
        </div>
        
        <section class="content-section">
            <h2>Recent Alerts</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Device</th>
                        <th>Rule</th>
                        <th>Severity</th>
                        <th>Message</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($recent_alerts as $alert): ?>
                    <tr class="severity-<?php echo $alert['severity']; ?>">
                        <td><?php echo htmlspecialchars($alert['hostname']); ?></td>
                        <td><?php echo htmlspecialchars($alert['rule']); ?></td>
                        <td><span class="badge <?php echo $alert['severity']; ?>"><?php echo $alert['severity']; ?></span></td>
                        <td><?php echo htmlspecialchars($alert['message']); ?></td>
                        <td><?php echo $alert['timestamp']; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </section>
    </main>
</div>
</body>
</html>
