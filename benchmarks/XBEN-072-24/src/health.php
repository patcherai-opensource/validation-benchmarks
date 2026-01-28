<?php
header('Content-Type: application/json');
echo json_encode([
    'status' => 'healthy',
    'version' => '2.4.1',
    'timestamp' => date('c')
]);
