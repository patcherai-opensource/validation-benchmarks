<?php
header('Content-Type: application/json');

// DataSync Export API - Returns sample exported data
$exports = [
    ['id' => 'EXP-001', 'name' => 'Configuration Export', 'timestamp' => date('Y-m-d H:i:s')],
    ['id' => 'EXP-002', 'name' => 'Data Backup', 'timestamp' => date('Y-m-d H:i:s', strtotime('-1 hour'))],
    ['id' => 'EXP-003', 'name' => 'Audit Log', 'timestamp' => date('Y-m-d H:i:s', strtotime('-2 hours'))],
];

$response = [
    'status' => 'success',
    'service' => 'DataSync Export',
    'exports' => $exports
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
