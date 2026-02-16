<?php
require_once 'includes/auth.php';
require_auth();

$conn = get_db_connection();

$where = "1=1";
$params = [];
$types = "";

if (isset($_GET['status']) && $_GET['status'] !== '') {
    $where .= " AND p.ifOperStatus = ?";
    $params[] = $_GET['status'];
    $types .= "s";
}

if (isset($_GET['device_id']) && is_numeric($_GET['device_id'])) {
    $where .= " AND p.device_id = ?";
    $params[] = intval($_GET['device_id']);
    $types .= "i";
}

$sql = "SELECT p.*, d.hostname FROM ports p INNER JOIN devices d ON p.device_id = d.device_id WHERE $where ORDER BY d.hostname, p.ifIndex";
if (!empty($params)) {
    $stmt = $conn->prepare($sql);
    $stmt->bind_param($types, ...$params);
    $stmt->execute();
    $ports = $stmt->get_result();
} else {
    $ports = $conn->query($sql);
}

$device_list = $conn->query("SELECT device_id, hostname FROM devices ORDER BY hostname");
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMon - Ports</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app-wrapper">
    <?php include 'includes/nav.php'; ?>
    
    <div class="main-content">
        <h1>Ports</h1>
        
        <div class="filter-bar">
            <form method="GET" class="inline-form">
                <select name="device_id">
                    <option value="">All Devices</option>
                    <?php while ($d = $device_list->fetch_assoc()): ?>
                    <option value="<?php echo $d['device_id']; ?>" 
                            <?php echo (isset($_GET['device_id']) && $_GET['device_id'] == $d['device_id']) ? 'selected' : ''; ?>>
                        <?php echo htmlspecialchars($d['hostname']); ?>
                    </option>
                    <?php endwhile; ?>
                </select>
                <select name="status">
                    <option value="">All Status</option>
                    <option value="up" <?php echo (isset($_GET['status']) && $_GET['status']==='up') ? 'selected' : ''; ?>>Up</option>
                    <option value="down" <?php echo (isset($_GET['status']) && $_GET['status']==='down') ? 'selected' : ''; ?>>Down</option>
                </select>
                <button type="submit" class="btn-primary">Filter</button>
            </form>
        </div>
        
        <div class="panel">
            <div class="panel-heading"><strong>All Ports</strong></div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Device</th>
                        <th>Interface</th>
                        <th>Alias</th>
                        <th>MAC Address</th>
                        <th>Speed</th>
                        <th>Status</th>
                        <th>In Errors</th>
                        <th>Out Errors</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while ($port = $ports->fetch_assoc()): ?>
                    <tr>
                        <td><a href="device.php?id=<?php echo $port['device_id']; ?>"><?php echo htmlspecialchars($port['hostname']); ?></a></td>
                        <td><?php echo htmlspecialchars($port['ifDescr']); ?></td>
                        <td><?php echo htmlspecialchars($port['ifAlias']); ?></td>
                        <td><?php 
                            $mac = $port['ifPhysAddress'];
                            echo htmlspecialchars(implode(':', str_split(str_pad($mac, 12, '0', STR_PAD_LEFT), 2)));
                        ?></td>
                        <td><?php 
                            $speed = $port['ifSpeed'];
                            if ($speed >= 1000000000) echo ($speed / 1000000000) . ' Gbps';
                            elseif ($speed >= 1000000) echo ($speed / 1000000) . ' Mbps';
                            elseif ($speed > 0) echo ($speed / 1000) . ' Kbps';
                            else echo '-';
                        ?></td>
                        <td>
                            <?php if ($port['ifOperStatus'] === 'up'): ?>
                                <span class="status-badge status-up">Up</span>
                            <?php else: ?>
                                <span class="status-badge status-down">Down</span>
                            <?php endif; ?>
                        </td>
                        <td><?php echo $port['ifInErrors']; ?></td>
                        <td><?php echo $port['ifOutErrors']; ?></td>
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