<?php
header('Content-Type: application/json');

echo json_encode([
    'status' => 'healthy',
    'service' => 'visionml-api',
    'version' => '2.1.0',
    'timestamp' => date('c')
], JSON_PRETTY_PRINT);
?>
