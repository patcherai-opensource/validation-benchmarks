<?php
require_once 'includes/auth.php';
require_auth();

$conn = get_db_connection();

$where = "1=1";
$params = [];
$types = "";

if (isset($_GET['status']) && $_GET['status'] !== '') {
    $where .= " AND status = ?";
    $params[] = intval($_GET['status']);
    $types .= "i";
}

if (isset($_GET['os']) && $_GET['os'] !== '') {
    $where .= " AND os = ?";
    $params[] = $_GET['os'];
    $types .= "s";
}

$sql = "SELECT * FROM devices WHERE $where ORDER BY hostname ASC";
if (!empty($params)) {
    $stmt = $conn->prepare($sql);
    $stmt->bind_param($types, ...$params);
    $stmt->execute();
    $devices = $stmt->get_result();
} else {
    $devices = $conn->query($sql);
}

$os_list = $conn->query("SELECT DISTINCT os FROM devices ORDER BY os");
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMon - Devices</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app-wrapper">
    <?php include 'includes/nav.php'; ?>
    
    <div class="main-content">
        <h1>Devices</h1>
        
        <div class="filter-bar">
            <form method="GET" class="inline-form">
                <select name="status">
                    <option value="">All Status</option>
                    <option value="1" <?php echo (isset($_GET['status']) && $_GET['status']==='1') ? 'selected' : ''; ?>>Up</option>
                    <option value="0" <?php echo (isset($_GET['status']) && $_GET['status']==='0') ? 'selected' : ''; ?>>Down</option>
                </select>
                <select name="os">
                    <option value="">All OS</option>
                    <?php while ($os_row = $os_list->fetch_assoc()): ?>
                    <option value="<?php echo htmlspecialchars($os_row['os']); ?>" 
                            <?php echo (isset($_GET['os']) && $_GET['os'] === $os_row['os']) ? 'selected' : ''; ?>>
                        <?php echo htmlspecialchars($os_row['os']); ?>
                    </option>
                    <?php endwhile; ?>
                </select>
                <button type="submit" class="btn-primary">Filter</button>
            </form>
        </div>
        
        <div class="panel">
            <div class="panel-heading"><strong>Monitored Devices</strong></div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Hostname</th>
                        <th>sysName</th>
                        <th>OS</th>
                        <th>Hardware</th>
                        <th>Version</th>
                        <th>IP</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while ($device = $devices->fetch_assoc()): ?>
                    <tr>
                        <td>
                            <?php if ($device['status'] == 1): ?>
                                <span class="status-badge status-up">Up</span>
                            <?php else: ?>
                                <span class="status-badge status-down">Down</span>
                            <?php endif; ?>
                        </td>
                        <td><a href="device.php?id=<?php echo $device['device_id']; ?>"><?php echo htmlspecialchars($device['hostname']); ?></a></td>
                        <td><?php echo htmlspecialchars($device['sysName']); ?></td>
                        <td><?php echo htmlspecialchars($device['os']); ?></td>
                        <td><?php echo htmlspecialchars($device['hardware']); ?></td>
                        <td><?php echo htmlspecialchars($device['version']); ?></td>
                        <td><?php echo htmlspecialchars($device['ip']); ?></td>
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