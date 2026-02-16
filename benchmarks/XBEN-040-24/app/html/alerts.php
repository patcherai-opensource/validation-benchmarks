<?php
require_once 'includes/auth.php';
require_auth();

$conn = get_db_connection();

$alert_log = $conn->query("SELECT al.*, d.hostname, ar.rule_name, ar.severity FROM alert_log al LEFT JOIN devices d ON al.device_id = d.device_id LEFT JOIN alert_rules ar ON al.rule_id = ar.rule_id WHERE al.state = 1 ORDER BY al.time_logged DESC LIMIT 50");
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMon - Alerts</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app-wrapper">
    <?php include 'includes/nav.php'; ?>
    
    <div class="main-content">
        <h1>Active Alerts</h1>
        
        <div class="panel">
            <div class="panel-heading"><strong>Alert Log</strong></div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Severity</th>
                        <th>Rule</th>
                        <th>Device</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while ($alert = $alert_log->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($alert['time_logged']); ?></td>
                        <td>
                            <span class="severity-<?php echo htmlspecialchars($alert['severity']); ?>">
                                <?php echo htmlspecialchars(ucfirst($alert['severity'])); ?>
                            </span>
                        </td>
                        <td><?php echo htmlspecialchars($alert['rule_name']); ?></td>
                        <td><?php echo htmlspecialchars($alert['hostname']); ?></td>
                        <td><?php echo htmlspecialchars($alert['details']); ?></td>
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