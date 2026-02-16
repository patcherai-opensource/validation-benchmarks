<?php
$conn = get_db_connection();

$results = null;
$search_address = isset($_POST['address']) ? trim($_POST['address']) : '';
$device_filter = isset($_POST['device_id']) ? intval($_POST['device_id']) : 0;

if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($search_address)) {
    $sql = "SELECT A.ipv4_address, A.ipv4_prefixlen, I.ifDescr, I.ifAlias, D.hostname, D.device_id 
            FROM ipv4_addresses AS A 
            INNER JOIN ports AS I ON I.port_id = A.port_id 
            INNER JOIN devices AS D ON I.device_id = D.device_id 
            WHERE A.ipv4_address LIKE ?";
    $params = ['%' . $search_address . '%'];
    $types = "s";
    
    if ($device_filter > 0) {
        $sql .= " AND I.device_id = ?";
        $params[] = $device_filter;
        $types .= "i";
    }
    
    $sql .= " ORDER BY D.hostname ASC";
    
    $stmt = $conn->prepare($sql);
    $stmt->bind_param($types, ...$params);
    $stmt->execute();
    $results = $stmt->get_result();
}

$device_list = $conn->query("SELECT device_id, hostname FROM devices ORDER BY hostname");
?>

<div class="panel">
    <div class="panel-heading"><strong>IPv4 Address Search</strong></div>
    <div class="search-form-container">
        <form method="POST" action="search.php?type=ipv4" class="inline-form">
            <select name="device_id">
                <option value="0">All Devices</option>
                <?php while ($d = $device_list->fetch_assoc()): ?>
                <option value="<?php echo $d['device_id']; ?>"
                        <?php echo ($device_filter == $d['device_id']) ? 'selected' : ''; ?>>
                    <?php echo htmlspecialchars($d['hostname']); ?>
                </option>
                <?php endwhile; ?>
            </select>
            <input type="text" name="address" placeholder="IPv4 Address" 
                   value="<?php echo htmlspecialchars($search_address); ?>">
            <button type="submit" class="btn-primary">Search</button>
        </form>
    </div>
    
    <?php if ($results !== null): ?>
    <table class="data-table">
        <thead>
            <tr>
                <th>Device</th>
                <th>Interface</th>
                <th>IP Address</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
            <?php if ($results->num_rows === 0): ?>
            <tr><td colspan="4">No results found.</td></tr>
            <?php else: ?>
            <?php while ($row = $results->fetch_assoc()): ?>
            <tr>
                <td><a href="device.php?id=<?php echo $row['device_id']; ?>"><?php echo htmlspecialchars($row['hostname']); ?></a></td>
                <td><?php echo htmlspecialchars($row['ifDescr']); ?></td>
                <td><?php echo htmlspecialchars($row['ipv4_address'] . '/' . $row['ipv4_prefixlen']); ?></td>
                <td><?php echo htmlspecialchars($row['ifAlias']); ?></td>
            </tr>
            <?php endwhile; ?>
            <?php endif; ?>
        </tbody>
    </table>
    <?php endif; ?>
</div>
<?php $conn->close(); ?>