<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'netmonDB';
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMon - Network Monitoring System</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>NetMon - Network Monitoring Dashboard</h1>
    <p class="subtitle">Monitor your network devices and installed packages</p>

    <div class="nav-links">
        <a href="index.php">Dashboard</a> |
        <a href="search.php">Package Search</a> |
        <a href="admin.php">Admin Panel</a>
    </div>

    <h2>Device Overview</h2>
    <?php
    $sql = "SELECT d.id, d.hostname, d.ip_address, d.status, d.os_version, COUNT(p.id) as package_count 
            FROM devices d 
            LEFT JOIN packages p ON d.id = p.device_id 
            GROUP BY d.id 
            ORDER BY d.hostname";
    $result = $conn->query($sql);

    if ($result === false) {
        die("Error loading devices: " . $conn->error);
    }

    if ($result->num_rows > 0) {
        echo "<table class='device-table'>";
        echo "<tr><th>Hostname</th><th>IP Address</th><th>Status</th><th>OS</th><th>Packages</th></tr>";
        while($row = $result->fetch_assoc()) {
            $statusClass = $row['status'] == 'active' ? 'status-active' : 'status-inactive';
            echo "<tr>";
            echo "<td>{$row['hostname']}</td>";
            echo "<td>{$row['ip_address']}</td>";
            echo "<td class='{$statusClass}'>{$row['status']}</td>";
            echo "<td>{$row['os_version']}</td>";
            echo "<td>{$row['package_count']}</td>";
            echo "</tr>";
        }
        echo "</table>";
    } else {
        echo "<p>No devices found in the monitoring system.</p>";
    }
    $conn->close();
    ?>
</div>
</body>
</html>
