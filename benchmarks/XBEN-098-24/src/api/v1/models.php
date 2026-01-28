<?php
// DeepVision Models API
header('Content-Type: application/json');

$models = [
    [
        "id" => "resnet50-v2",
        "name" => "ResNet-50 V2",
        "type" => "classification",
        "version" => "2.1.0",
        "status" => "active"
    ],
    [
        "id" => "yolov5-large", 
        "name" => "YOLOv5 Large",
        "type" => "detection",
        "version" => "5.0.0",
        "status" => "active"
    ],
    [
        "id" => "unet-seg",
        "name" => "U-Net Segmentation",
        "type" => "segmentation", 
        "version" => "1.2.0",
        "status" => "active"
    ],
    [
        "id" => "efficientnet-b7",
        "name" => "EfficientNet B7",
        "type" => "classification",
        "version" => "3.0.0",
        "status" => "active"
    ]
];

echo json_encode([
    "status" => "success",
    "count" => count($models),
    "models" => $models
], JSON_PRETTY_PRINT);
?>
