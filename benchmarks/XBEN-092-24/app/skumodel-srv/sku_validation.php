<?php
header('Content-Type: application/json');

/**
 * Image Optimizer API - Status endpoint
 * Returns current optimization queue status
 */

$queue = [
    ['job_id' => 'IMG' . rand(1000, 9999), 'status' => 'completed', 'size_reduction' => rand(10, 50) . '%'],
    ['job_id' => 'IMG' . rand(1000, 9999), 'status' => 'processing', 'size_reduction' => 'pending'],
    ['job_id' => 'IMG' . rand(1000, 9999), 'status' => 'queued', 'size_reduction' => 'pending'],
];

$response = [
    'status' => 'success',
    'service' => 'image-optimizer',
    'version' => '1.7.2',
    'queue' => $queue
];

echo json_encode($response);
?>
