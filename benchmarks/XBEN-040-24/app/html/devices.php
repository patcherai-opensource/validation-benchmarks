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

$devices = [];
$result = $conn->query("SELECT * FROM devices ORDER BY hostname");
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $devices[] = $row;
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Devices - NetMon</title>
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
            <h1>Devices</h1>
        </header>
        
        <section class="content-section">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Hostname</th>
                        <th>IP Address</th>
                        <th>OS</th>
                        <th>Version</th>
                        <th>Status</th>
                        <th>Last Polled</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($devices as $device): ?>
                    <tr>
                        <td><a href="device.php?id=<?php echo $device['device_id']; ?>"><?php echo htmlspecialchars($device['hostname']); ?></a></td>
                        <td><?php echo htmlspecialchars($device['ip_address']); ?></td>
                        <td><?php echo htmlspecialchars($device['os']); ?></td>
                        <td><?php echo htmlspecialchars($device['version']); ?></td>
                        <td><span class="badge <?php echo $device['status'] ? 'up' : 'down'; ?>"><?php echo $device['status'] ? 'Up' : 'Down'; ?></span></td>
                        <td><?php echo $device['last_polled']; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </section>
    </main>
</div>
</body>
</html>
