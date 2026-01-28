<?php
header('Content-Type: application/json');
echo json_encode([
    'status' => 'healthy',
    'service' => 'predictml-inference',
    'version' => '2.4.1',
    'uptime' => rand(100000, 999999),
    'timestamp' => date('c')
]);
?>
