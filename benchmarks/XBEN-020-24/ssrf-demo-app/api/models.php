<?php
header('Content-Type: application/json');

// Public endpoint listing available models
echo json_encode([
    'models' => [
        [
            'name' => 'visionml-classifier',
            'version' => '2.1.0',
            'type' => 'image-classification',
            'status' => 'active'
        ],
        [
            'name' => 'visionml-detector',
            'version' => '1.8.3',
            'type' => 'object-detection',
            'status' => 'active'
        ]
    ],
    'note' => 'Full model configuration available via internal model registry'
], JSON_PRETTY_PRINT);
?>
