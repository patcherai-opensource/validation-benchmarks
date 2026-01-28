<?php
// Read models data
$models = [
    [
        'name' => 'bert-sentiment-v2',
        'latest_version' => '3',
        'description' => 'BERT-based sentiment analysis model',
        'tags' => ['nlp', 'production'],
        'source' => 'file:///var/mltrack/models/bert-sentiment-v2'
    ],
    [
        'name' => 'resnet50-classifier',
        'latest_version' => '5',
        'description' => 'Image classification model based on ResNet-50',
        'tags' => ['computer-vision', 'staging'],
        'source' => 'file:///var/mltrack/models/resnet50-classifier'
    ],
    [
        'name' => 'fraud-detector-xgb',
        'latest_version' => '2',
        'description' => 'XGBoost model for fraud detection',
        'tags' => ['tabular', 'production'],
        'source' => 'file:///var/mltrack/models/fraud-detector-xgb'
    ],
    [
        'name' => 'time-series-lstm',
        'latest_version' => '1',
        'description' => 'LSTM network for time series forecasting',
        'tags' => ['forecasting', 'development'],
        'source' => 'file:///var/mltrack/models/time-series-lstm'
    ]
];
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>MLTrack - Model Registry</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .model-card { border-left: 4px solid #198754; }
        .tag-production { background-color: #198754; }
        .tag-staging { background-color: #ffc107; color: #000; }
        .tag-development { background-color: #0dcaf0; }
    </style>
</head>
<body>
    <? include("include/navigation-bar.php") ?>

    <header class="py-4 bg-dark text-white mb-4">
        <div class="container">
            <h1>Model Registry</h1>
            <p class="lead">Manage and deploy your ML models</p>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <h3 class="mb-4">Registered Models</h3>
                
                <?php foreach ($models as $model): ?>
                <div class="card mb-3 model-card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <h5 class="card-title"><?= htmlspecialchars($model['name']); ?></h5>
                            <span class="badge bg-secondary">v<?= htmlspecialchars($model['latest_version']); ?></span>
                        </div>
                        <p class="card-text"><?= htmlspecialchars($model['description']); ?></p>
                        <div class="mb-2">
                            <?php foreach ($model['tags'] as $tag): ?>
                                <span class="badge tag-<?= htmlspecialchars($tag); ?> me-1"><?= htmlspecialchars($tag); ?></span>
                            <?php endforeach; ?>
                        </div>
                        <small class="text-muted">Source: <?= htmlspecialchars($model['source']); ?></small>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-primary">View Versions</button>
                            <button class="btn btn-sm btn-outline-secondary">Download</button>
                        </div>
                    </div>
                </div>
                <?php endforeach; ?>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">Quick Actions</div>
                    <div class="card-body">
                        <ul class="list-unstyled">
                            <li class="mb-2"><a href="/api/docs.php">API Documentation</a></li>
                            <li class="mb-2"><a href="/api/2.0/mltrack/experiments/list.php">List Experiments</a></li>
                            <li class="mb-2"><a href="/health">Health Check</a></li>
                        </ul>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">Statistics</div>
                    <div class="card-body">
                        <p>Total Models: <strong><?= count($models); ?></strong></p>
                        <p>Production Models: <strong>2</strong></p>
                        <p>Active Experiments: <strong>6</strong></p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
