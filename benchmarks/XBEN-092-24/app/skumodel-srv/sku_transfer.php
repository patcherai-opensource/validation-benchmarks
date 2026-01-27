<?php
header('Content-Type: application/json');

/**
 * Image Optimizer API - Batch processing endpoint
 * Handles batch image optimization jobs
 */

$jobs = [
    ['job_id' => 'BATCH' . rand(1000, 9999), 'images_processed' => rand(1, 100), 'status' => 'completed'],
    ['job_id' => 'BATCH' . rand(1000, 9999), 'images_processed' => rand(1, 50), 'status' => 'in_progress'],
    ['job_id' => 'BATCH' . rand(1000, 9999), 'images_processed' => 0, 'status' => 'queued'],
];

$response = [
    'status' => 'success',
    'batch_jobs' => $jobs
];

echo json_encode($response);
?>
