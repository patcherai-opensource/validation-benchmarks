<?php
require_once 'includes/auth.php';
require_auth();

$conn = get_db_connection();

$device_id = intval($_GET['id'] ?? 0);
if ($device_id <= 0) {
    header('Location: devices.php');
    exit;
}

$stmt = $conn->prepare("SELECT * FROM devices WHERE device_id = ?");
$stmt->bind_param("i", $device_id);
$stmt->execute();
$device = $stmt->get_result()->fetch_assoc();

if (!$device) {
    echo "Device not found.";
    exit;
}

$ports = $conn->query("SELECT p.*, GROUP_CONCAT(a.ipv4_address, '/', a.ipv4_prefixlen) as ip_addresses FROM ports p LEFT JOIN ipv4_addresses a ON p.port_id = a.port_id WHERE p.device_id = $device_id GROUP BY p.port_id ORDER BY p.ifIndex");
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMon - <?php echo htmlspecialchars($device['hostname']); ?></title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app-wrapper">
    <?php include 'includes/nav.php'; ?>
    
    <div class="main-content">
        <h1><?php echo htmlspecialchars($device['hostname']); ?></h1>
        
        <div class="panel">
            <div class="panel-heading"><strong>Device Information</strong></div>
            <table class="detail-table">
                <tr><th>Hostname</th><td><?php echo htmlspecialchars($device['hostname']); ?></td></tr>
                <tr><th>sysName</th><td><?php echo htmlspecialchars($device['sysName']); ?></td></tr>
                <tr><th>sysDescr</th><td><?php echo htmlspecialchars($device['sysDescr']); ?></td></tr>
                <tr><th>OS</th><td><?php echo htmlspecialchars($device['os']); ?></td></tr>
                <tr><th>Hardware</th><td><?php echo htmlspecialchars($device['hardware']); ?></td></tr>
                <tr><th>Version</th><td><?php echo htmlspecialchars($device['version']); ?></td></tr>
                <tr><th>IP</th><td><?php echo htmlspecialchars($device['ip']); ?></td></tr>
                <tr><th>Status</th><td><?php echo $device['status'] ? '<span class="status-badge status-up">Up</span>' : '<span class="status-badge status-down">Down</span>'; ?></td></tr>
            </table>
        </div>
        
        <div class="panel">
            <div class="panel-heading"><strong>Interfaces</strong></div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ifIndex</th>
                        <th>Interface</th>
                        <th>Alias</th>
                        <th>Type</th>
                        <th>MAC Address</th>
                        <th>Speed</th>
                        <th>Status</th>
                        <th>IP Addresses</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while ($port = $ports->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($port['ifIndex']); ?></td>
                        <td><?php echo htmlspecialchars($port['ifDescr']); ?></td>
                        <td><?php echo htmlspecialchars($port['ifAlias']); ?></td>
                        <td><?php echo htmlspecialchars($port['ifType']); ?></td>
                        <td><?php 
                            $mac = $port['ifPhysAddress'];
                            echo htmlspecialchars(implode(':', str_split(str_pad($mac, 12, '0', STR_PAD_LEFT), 2)));
                        ?></td>
                        <td><?php 
                            $speed = $port['ifSpeed'];
                            if ($speed >= 1000000000) {
                                echo ($speed / 1000000000) . ' Gbps';
                            } elseif ($speed >= 1000000) {
                                echo ($speed / 1000000) . ' Mbps';
                            } elseif ($speed > 0) {
                                echo ($speed / 1000) . ' Kbps';
                            } else {
                                echo '-';
                            }
                        ?></td>
                        <td>
                            <?php if ($port['ifOperStatus'] === 'up'): ?>
                                <span class="status-badge status-up">Up</span>
                            <?php else: ?>
                                <span class="status-badge status-down">Down</span>
                            <?php endif; ?>
                        </td>
                        <td><?php echo htmlspecialchars($port['ip_addresses'] ?? '-'); ?></td>
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