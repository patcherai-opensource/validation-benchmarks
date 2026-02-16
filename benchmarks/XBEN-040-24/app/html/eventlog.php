<?php
require_once 'includes/auth.php';
require_auth();

$conn = get_db_connection();

$events = $conn->query("SELECT e.*, d.hostname FROM eventlog e LEFT JOIN devices d ON e.device_id = d.device_id ORDER BY e.datetime DESC LIMIT 100");
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMon - Event Log</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app-wrapper">
    <?php include 'includes/nav.php'; ?>
    
    <div class="main-content">
        <h1>Event Log</h1>
        
        <div class="panel">
            <div class="panel-heading"><strong>Recent Events</strong></div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Device</th>
                        <th>Type</th>
                        <th>Message</th>
                        <th>Severity</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while ($event = $events->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($event['datetime']); ?></td>
                        <td><?php echo htmlspecialchars($event['hostname'] ?? 'N/A'); ?></td>
                        <td><?php echo htmlspecialchars($event['type']); ?></td>
                        <td><?php echo htmlspecialchars($event['message']); ?></td>
                        <td><?php echo $event['severity']; ?></td>
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