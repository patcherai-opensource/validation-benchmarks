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

$filter_type = isset($_GET['type']) ? mysqli_real_escape_string($conn, $_GET['type']) : '';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMonitor - Devices</title>
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
        <a href="devices.php" class="active">Devices</a>
        <a href="alerts.php">Alerts</a>
        <a href="search.php">Search</a>
        <?php if (isset($_SESSION['user_logged_in']) && $_SESSION['user_logged_in'] === true): ?>
            <a href="logout.php">Logout (<?php echo htmlspecialchars($_SESSION['username']); ?>)</a>
        <?php else: ?>
            <a href="login.php">Login</a>
        <?php endif; ?>
    </nav>

    <div class="content">
        <h2>Device Inventory</h2>
        
        <form method="GET" class="filter-form">
            <label for="type">Filter by type:</label>
            <select name="type" id="type" onchange="this.form.submit()">
                <option value="">All Types</option>
                <?php
                $types = $conn->query("SELECT DISTINCT device_type FROM devices ORDER BY device_type");
                while ($t = $types->fetch_assoc()) {
                    $selected = ($t['device_type'] == $filter_type) ? 'selected' : '';
                    echo "<option value='{$t['device_type']}' {$selected}>{$t['device_type']}</option>";
                }
                ?>
            </select>
        </form>

        <table class="data-table">
            <thead>
                <tr>
                    <th>Hostname</th>
                    <th>IP Address</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Operating System</th>
                    <th>Last Polled</th>
                </tr>
            </thead>
            <tbody>
            <?php
            $sql = "SELECT * FROM devices";
            if (!empty($filter_type)) {
                $sql .= " WHERE device_type = '$filter_type'";
            }
            $sql .= " ORDER BY hostname";
            
            $devices = $conn->query($sql);
            while ($device = $devices->fetch_assoc()) {
                $status_class = $device['status'] == 'up' ? 'status-up' : 'status-down';
                echo "<tr>";
                echo "<td>{$device['hostname']}</td>";
                echo "<td>{$device['ip_address']}</td>";
                echo "<td>{$device['device_type']}</td>";
                echo "<td class='{$status_class}'>{$device['status']}</td>";
                echo "<td>{$device['os']}</td>";
                echo "<td>{$device['last_polled']}</td>";
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
