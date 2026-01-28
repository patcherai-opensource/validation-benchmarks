<?php
session_start();

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$filter_severity = isset($_GET['severity']) ? mysqli_real_escape_string($conn, $_GET['severity']) : '';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMonitor - Alerts</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>NetMonitor</h1>
        <p class="subtitle">Network Monitoring &amp; Management Platform v2.4.3</p>
    </div>
    
    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="devices.php">Devices</a>
        <a href="alerts.php" class="active">Alerts</a>
        <a href="search.php">Search</a>
        <?php if (isset($_SESSION['user_logged_in']) && $_SESSION['user_logged_in'] === true): ?>
            <a href="logout.php">Logout (<?php echo htmlspecialchars($_SESSION['username']); ?>)</a>
        <?php else: ?>
            <a href="login.php">Login</a>
        <?php endif; ?>
    </nav>

    <div class="content">
        <h2>Alert Management</h2>
        
        <form method="GET" class="filter-form">
            <label for="severity">Filter by severity:</label>
            <select name="severity" id="severity" onchange="this.form.submit()">
                <option value="">All Severities</option>
                <option value="critical" <?php echo $filter_severity == 'critical' ? 'selected' : ''; ?>>Critical</option>
                <option value="high" <?php echo $filter_severity == 'high' ? 'selected' : ''; ?>>High</option>
                <option value="warning" <?php echo $filter_severity == 'warning' ? 'selected' : ''; ?>>Warning</option>
            </select>
        </form>

        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Device</th>
                    <th>Alert Type</th>
                    <th>Severity</th>
                    <th>Message</th>
                    <th>Acknowledged</th>
                    <th>Created</th>
                </tr>
            </thead>
            <tbody>
            <?php
            $sql = "SELECT a.*, d.hostname FROM alerts a JOIN devices d ON a.device_id = d.device_id";
            if (!empty($filter_severity)) {
                $sql .= " WHERE a.severity = '$filter_severity'";
            }
            $sql .= " ORDER BY a.created_at DESC";
            
            $alerts = $conn->query($sql);
            while ($alert = $alerts->fetch_assoc()) {
                $ack = $alert['acknowledged'] ? 'Yes' : 'No';
                echo "<tr class='severity-{$alert['severity']}'>";
                echo "<td>{$alert['id']}</td>";
                echo "<td>{$alert['hostname']}</td>";
                echo "<td>{$alert['alert_type']}</td>";
                echo "<td>{$alert['severity']}</td>";
                echo "<td>{$alert['message']}</td>";
                echo "<td>{$ack}</td>";
                echo "<td>{$alert['created_at']}</td>";
                echo "</tr>";
            }
            ?>
            </tbody>
        </table>
    </div>
</div>

<footer>
    <p>NetMonitor v2.4.3 | <a href="admin.php">Administration</a></p>
</footer>

<?php $conn->close(); ?>
</body>
</html>
