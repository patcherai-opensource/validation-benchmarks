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

$alerts = [];
$result = $conn->query("SELECT a.*, d.hostname FROM alerts a JOIN devices d ON a.device_id = d.device_id ORDER BY a.timestamp DESC");
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $alerts[] = $row;
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alerts - NetMon</title>
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
            <li class="nav-item"><a href="devices.php">Devices</a></li>
            <li class="nav-item active"><a href="alerts.php">Alerts</a></li>
            <li class="nav-item"><a href="search.php">Search</a></li>
            <li class="nav-item"><a href="index.php?logout=1">Logout</a></li>
        </ul>
        <div class="sidebar-footer">
            <p>Logged in as: <?php echo htmlspecialchars($_SESSION['username']); ?></p>
        </div>
    </nav>
    
    <main class="main-content">
        <header class="page-header">
            <h1>Alert Log</h1>
        </header>
        
        <section class="content-section">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Device</th>
                        <th>Rule</th>
                        <th>Severity</th>
                        <th>Message</th>
                        <th>State</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($alerts as $alert): ?>
                    <tr class="severity-<?php echo $alert['severity']; ?>">
                        <td><?php echo $alert['id']; ?></td>
                        <td><?php echo htmlspecialchars($alert['hostname']); ?></td>
                        <td><?php echo htmlspecialchars($alert['rule']); ?></td>
                        <td><span class="badge <?php echo $alert['severity']; ?>"><?php echo $alert['severity']; ?></span></td>
                        <td><?php echo htmlspecialchars($alert['message']); ?></td>
                        <td><span class="badge <?php echo $alert['state'] ? 'active' : 'resolved'; ?>"><?php echo $alert['state'] ? 'Active' : 'Resolved'; ?></span></td>
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
