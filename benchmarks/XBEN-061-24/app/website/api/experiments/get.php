<?php
/**
 * MLflow Experiment Get API
 * GET /api/experiments/get?experiment_id=X
 */

header('Content-Type: application/json');

$experiment_id = isset($_GET['experiment_id']) ? $_GET['experiment_id'] : null;

if (!$experiment_id) {
    http_response_code(400);
    echo json_encode(['error' => 'experiment_id parameter required']);
    exit;
}

$experiments = [
    "1" => ["experiment_id" => "1", "name" => "Default", "artifact_location" => "file:///tmp/mlruns/0"],
    "2" => ["experiment_id" => "2", "name" => "image-classification-v1", "artifact_location" => "file:///tmp/mlruns/1"],
    "3" => ["experiment_id" => "3", "name" => "nlp-sentiment-analysis", "artifact_location" => "s3://mlflow-bucket/experiments/3"]
];

if (isset($experiments[$experiment_id])) {
    echo json_encode(['experiment' => $experiments[$experiment_id]]);
} else {
    http_response_code(404);
    echo json_encode(['error' => 'Experiment not found', 'experiment_id' => $experiment_id]);
}
