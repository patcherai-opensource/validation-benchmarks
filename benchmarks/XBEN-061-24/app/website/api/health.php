<?php
/**
 * MLflow Health Check API
 * GET /api/health
 */

header('Content-Type: application/json');

echo json_encode([
    'status' => 'healthy',
    'version' => '2.10.2',
    'backend_store' => 'file:///tmp/mlruns',
    'artifact_root' => 'file:///tmp/mlruns/artifacts'
]);
