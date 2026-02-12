<?php
    header('Content-Type: application/json');
    echo json_encode([
        'name' => 'Open WebUI',
        'version' => '0.3.8',
        'build' => 'stable'
    ]);
