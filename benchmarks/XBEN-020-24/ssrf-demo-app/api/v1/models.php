<?php
header('Content-Type: application/json');
echo json_encode([
    'models' => [
        [
            'id' => 'image_classifier',
            'name' => 'ResNet50 Image Classifier',
            'type' => 'image',
            'version' => '1.2.0',
            'input_types' => ['image/jpeg', 'image/png', 'url'],
            'status' => 'active'
        ],
        [
            'id' => 'text_sentiment',
            'name' => 'BERT Sentiment Analyzer',
            'type' => 'text',
            'version' => '2.0.3',
            'input_types' => ['text/plain', 'application/json'],
            'status' => 'active'
        ],
        [
            'id' => 'object_detector',
            'name' => 'YOLO Object Detection',
            'type' => 'image',
            'version' => '3.1.0',
            'input_types' => ['image/jpeg', 'image/png', 'url'],
            'status' => 'maintenance'
        ]
    ],
    'total' => 3
]);
?>
