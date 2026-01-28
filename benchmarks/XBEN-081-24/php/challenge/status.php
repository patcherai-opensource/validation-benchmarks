<?php
    include 'config.php';
    
    header('Content-Type: application/json');
    
    echo json_encode([
        'status' => 'healthy',
        'service' => 'NoteHub CRM',
        'version' => '5.2.1',
        'timestamp' => date('Y-m-d H:i:s')
    ]);
?>
