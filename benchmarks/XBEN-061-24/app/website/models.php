<?php
// Read the JSON file for models
$json_data = file_get_contents('models.json');
$models = json_decode($json_data, true);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DataFlow ML Tracking Server | Models</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .model-card { border-left: 4px solid #00b894; }
        .version-badge { font-size: 0.75rem; }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Registered Models</h1>
                <p class="lead mb-0">Model Registry for DataFlow ML Tracking Server</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <h3 class="mb-4">Available Models</h3>
                <?php foreach ($models as $model): ?>
                    <div class="card mb-4 model-card">
                        <div class="card-body">
                            <h5 class="card-title"><?= htmlspecialchars($model['name']); ?></h5>
                            <p class="card-text"><?= htmlspecialchars($model['description']); ?></p>
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="badge bg-success version-badge">Latest Version: <?= htmlspecialchars($model['latest_version']); ?></span>
                                <small class="text-muted">Source: <?= htmlspecialchars($model['source']); ?></small>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>

            <!-- Sidebar Widgets Column -->
            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
