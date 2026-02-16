<?php
$vars = $_REQUEST;

if (isset($vars['search_type']) && $vars['search_type'] === 'ipv4' && !empty($vars['address'])) {
    $search = '%' . $conn->real_escape_string(trim($vars['address'])) . '%';
    
    $sql = "SELECT A.ipv4_address, A.ipv4_prefixlen, I.ifDescr, I.ifAlias, D.hostname, D.device_id 
            FROM ipv4_addresses AS A 
            INNER JOIN ports AS I ON I.port_id = A.port_id 
            INNER JOIN devices AS D ON I.device_id = D.device_id 
            WHERE A.ipv4_address LIKE ?";
    $types = "s";
    $params = [$search];
    
    if (isset($vars['device_id']) && is_numeric($vars['device_id'])) {
        $sql .= " AND I.device_id = ?";
        $types .= "i";
        $params[] = intval($vars['device_id']);
    }
    
    $sql .= " ORDER BY D.hostname ASC";
    
    $stmt = $conn->prepare($sql);
    $stmt->bind_param($types, ...$params);
    $stmt->execute();
    $result = $stmt->get_result();
    
    $rows = [];
    while ($row = $result->fetch_assoc()) {
        $rows[] = [
            'hostname'  => $row['hostname'],
            'interface' => $row['ifDescr'],
            'address'   => $row['ipv4_address'] . '/' . $row['ipv4_prefixlen'],
            'description' => $row['ifAlias'],
        ];
    }
    
    $response = [
        'current'  => $current,
        'rowCount' => $rowCount,
        'rows'     => $rows,
        'total'    => count($rows),
    ];
    
    $stmt->close();
}
