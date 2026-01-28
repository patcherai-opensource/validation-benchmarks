<?php
// DeepVision Datasets API
header('Content-Type: application/json');

$datasets = [
    [
        "id" => "imagenet-mini",
        "name" => "ImageNet Mini",
        "size_gb" => 2.3,
        "images" => 50000,
        "format" => "imagefolder"
    ],
    [
        "id" => "coco-2017",
        "name" => "COCO 2017",
        "size_gb" => 18,
        "images" => 118287,
        "format" => "coco"
    ],
    [
        "id" => "cifar-100",
        "name" => "CIFAR-100",
        "size_gb" => 0.161,
        "images" => 60000,
        "format" => "pickle"
    ]
];

echo json_encode([
    "status" => "success",
    "count" => count($datasets),
    "datasets" => $datasets
], JSON_PRETTY_PRINT);
?>
