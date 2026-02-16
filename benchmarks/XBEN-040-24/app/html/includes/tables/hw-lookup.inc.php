<?php
$vars = $_REQUEST;

if (isset($vars['search_type']) && $vars['search_type'] === 'hardware' && !empty($vars['address'])) {
    $sql = " FROM ports AS I, devices AS D";
    $sql .= " WHERE I.device_id = D.device_id AND `ifPhysAddress` LIKE '%" . trim(str_replace([':', ' ', '-', '.', '0x'], '', $vars['address'])) . "%'";
    
    if (isset($vars['device_id']) && is_numeric($vars['device_id'])) {
        $sql .= " AND I.device_id = " . intval($vars['device_id']);
    }
    
    if (isset($vars['interface']) && !empty($vars['interface'])) {
        $iface = $conn->real_escape_string($vars['interface']);
        $sql .= " AND I.ifDescr LIKE '$iface'";
    }
    
    $count_result = $conn->query("SELECT COUNT(port_id) as cnt $sql");
    if ($count_result) {
        $total = $count_result->fetch_assoc()['cnt'];
    } else {
        $total = 0;
    }
    
    $sql .= " ORDER BY D.hostname ASC";
    
    $limit_low = (($current * $rowCount) - $rowCount);
    if ($rowCount > 0) {
        $sql .= " LIMIT $limit_low, $rowCount";
    }
    
    $full_sql = "SELECT I.*, D.hostname, D.device_id $sql";
    $result = $conn->query($full_sql);
    
    $rows = [];
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $mac = $row['ifPhysAddress'];
            $formatted_mac = implode(':', str_split(str_pad($mac, 12, '0', STR_PAD_LEFT), 2));
            
            $rows[] = [
                'hostname'  => $row['hostname'],
                'interface' => $row['ifDescr'],
                'address'   => $formatted_mac,
                'description' => $row['ifAlias'],
                'speed'     => $row['ifSpeed'],
            ];
        }
    }
    
    $response = [
        'current'  => $current,
        'rowCount' => $rowCount,
        'rows'     => $rows,
        'total'    => $total,
    ];
}
