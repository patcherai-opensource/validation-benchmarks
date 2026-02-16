<?php
require_once 'includes/auth.php';
require_auth();

$conn = get_db_connection();

// Get device counts for overview
$total_devices = $conn->query("SELECT COUNT(*) as cnt FROM devices")->fetch_assoc()['cnt'];
$up_devices = $conn->query("SELECT COUNT(*) as cnt FROM devices WHERE status = 1")->fetch_assoc()['cnt'];
$down_devices = $conn->query("SELECT COUNT(*) as cnt FROM devices WHERE status = 0")->fetch_assoc()['cnt'];
$total_ports = $conn->query("SELECT COUNT(*) as cnt FROM ports")->fetch_assoc()['cnt'];
$ports_up = $conn->query("SELECT COUNT(*) as cnt FROM ports WHERE ifOperStatus = 'up'")->fetch_assoc()['cnt'];
$active_alerts = $conn->query("SELECT COUNT(*) as cnt FROM alert_log WHERE state = 1")->fetch_assoc()['cnt'];

// Get recent events
$events = $conn->query("SELECT e.*, d.hostname FROM eventlog e LEFT JOIN devices d ON e.device_id = d.device_id ORDER BY e.datetime DESC LIMIT 10");
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMon - Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app-wrapper">
    <?php include 'includes/nav.php'; ?>
    
    <div class="main-content">
        <h1>Dashboard</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value"><?php echo $total_devices; ?></div>
                <div class="stat-label">Total Devices</div>
            </div>
            <div class="stat-card stat-ok">
                <div class="stat-value"><?php echo $up_devices; ?></div>
                <div class="stat-label">Devices Up</div>
            </div>
            <div class="stat-card stat-error">
                <div class="stat-value"><?php echo $down_devices; ?></div>
                <div class="stat-label">Devices Down</div>
            </div>
            <div class="stat-card">
                <div class="stat-value"><?php echo $total_ports; ?></div>
                <div class="stat-label">Total Ports</div>
            </div>
            <div class="stat-card stat-ok">
                <div class="stat-value"><?php echo $ports_up; ?></div>
                <div class="stat-label">Ports Up</div>
            </div>
            <div class="stat-card stat-warning">
                <div class="stat-value"><?php echo $active_alerts; ?></div>
                <div class="stat-label">Active Alerts</div>
            </div>
        </div>
        
        <div class="panel">
            <div class="panel-heading"><strong>Recent Events</strong></div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Device</th>
                        <th>Type</th>
                        <th>Message</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while ($event = $events->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($event['datetime']); ?></td>
                        <td><?php echo htmlspecialchars($event['hostname'] ?? 'N/A'); ?></td>
                        <td><?php echo htmlspecialchars($event['type']); ?></td>
                        <td><?php echo htmlspecialchars($event['message']); ?></td>
                    </tr>
                    <?php endwhile; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>
<?php $conn->close(); ?>
