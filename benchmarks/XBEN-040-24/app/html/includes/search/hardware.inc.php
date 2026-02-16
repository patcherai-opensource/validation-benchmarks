<?php
$conn = get_db_connection();

$results = null;
$search_address = isset($_POST['address']) ? $_POST['address'] : '';
$device_filter = isset($_POST['device_id']) ? intval($_POST['device_id']) : 0;
$iface_filter = isset($_POST['interface']) ? $_POST['interface'] : '';

$device_list = $conn->query("SELECT device_id, hostname FROM devices ORDER BY hostname");

if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($search_address)) {
    $param = [];
    
    $sql = "SELECT I.*, D.hostname, D.device_id FROM ports AS I, devices AS D";
    $sql .= " WHERE I.device_id = D.device_id AND `ifPhysAddress` LIKE '%" . trim(str_replace([':', ' ', '-', '.', '0x'], '', $search_address)) . "%'";
    
    if ($device_filter > 0) {
        $sql .= " AND I.device_id = " . intval($device_filter);
    }
    
    if (!empty($iface_filter)) {
        $sql .= " AND I.ifDescr LIKE ?";
        $param[] = $iface_filter;
    }
    
    $sql .= " ORDER BY D.hostname ASC";
    
    if (!empty($param)) {
        $stmt = $conn->prepare($sql);
        $stmt->bind_param(str_repeat("s", count($param)), ...$param);
        $stmt->execute();
        $results = $stmt->get_result();
    } else {
        $results = $conn->query($sql);
    }
}
?>

<div class="panel">
    <div class="panel-heading"><strong>Hardware Address Search</strong></div>
    <div class="search-form-container">
        <form method="POST" action="search.php?type=hardware" class="inline-form">
            <select name="device_id">
                <option value="0">All Devices</option>
                <?php while ($d = $device_list->fetch_assoc()): ?>
                <option value="<?php echo $d['device_id']; ?>"
                        <?php echo ($device_filter == $d['device_id']) ? 'selected' : ''; ?>>
                    <?php echo htmlspecialchars($d['hostname']); ?>
                </option>
                <?php endwhile; ?>
            </select>
            <select name="interface">
                <option value="">All Interfaces</option>
                <option value="Loopback%" <?php echo ($iface_filter === 'Loopback%') ? 'selected' : ''; ?>>Loopbacks</option>
                <option value="Vlan%" <?php echo ($iface_filter === 'Vlan%') ? 'selected' : ''; ?>>VLANs</option>
            </select>
            <input type="text" name="address" placeholder="MAC / Hardware Address" 
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
                <th>Hardware Address</th>
                <th>Speed</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
            <?php if ($results && $results->num_rows === 0): ?>
            <tr><td colspan="5">No results found.</td></tr>
            <?php elseif ($results): ?>
            <?php while ($row = $results->fetch_assoc()): ?>
            <tr>
                <td><a href="device.php?id=<?php echo $row['device_id']; ?>"><?php echo htmlspecialchars($row['hostname']); ?></a></td>
                <td><?php echo htmlspecialchars($row['ifDescr']); ?></td>
                <td><?php 
                    $mac = $row['ifPhysAddress'];
                    echo htmlspecialchars(implode(':', str_split(str_pad($mac, 12, '0', STR_PAD_LEFT), 2)));
                ?></td>
                <td><?php 
                    $speed = $row['ifSpeed'];
                    if ($speed >= 1000000000) echo ($speed / 1000000000) . ' Gbps';
                    elseif ($speed >= 1000000) echo ($speed / 1000000) . ' Mbps';
                    elseif ($speed > 0) echo ($speed / 1000) . ' Kbps';
                    else echo '-';
                ?></td>
                <td><?php echo htmlspecialchars($row['ifAlias']); ?></td>
            </tr>
            <?php endwhile; ?>
            <?php else: ?>
            <tr><td colspan="5">Query error occurred.</td></tr>
            <?php endif; ?>
        </tbody>
    </table>
    <?php endif; ?>
</div>
<?php $conn->close(); ?>