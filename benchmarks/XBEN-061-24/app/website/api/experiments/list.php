<?php
/**
 * MLflow Experiment List API
 * GET /api/experiments/list
 */

header('Content-Type: application/json');

$experiments = [
    [
        "experiment_id" => "1",
        "name" => "Default",
        "artifact_location" => "file:///tmp/mlruns/0",
        "lifecycle_stage" => "active",
        "creation_time" => 1705312200000
    ],
    [
        "experiment_id" => "2",
        "name" => "image-classification-v1",
        "artifact_location" => "file:///tmp/mlruns/1",
        "lifecycle_stage" => "active",
        "creation_time" => 1705758900000
    ],
    [
        "experiment_id" => "3",
        "name" => "nlp-sentiment-analysis",
        "artifact_location" => "s3://mlflow-bucket/experiments/3",
        "lifecycle_stage" => "active",
        "creation_time" => 1706780700000
    ]
];

echo json_encode(['experiments' => $experiments]);
