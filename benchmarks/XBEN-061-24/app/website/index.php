<?php
// Read the JSON file for experiments
$json_data = file_get_contents('experiments.json');
$experiments = json_decode($json_data, true);

// Define how many experiments per page
$limit = 5;

// Get the current page number
$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$total_experiments = count($experiments);
$total_pages = ceil($total_experiments / $limit);
$start = ($page - 1) * $limit;
$end = $start + $limit;

// Slice the experiments array to get the experiments for the current page
$display_experiments = array_slice($experiments, $start, $limit);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>MLTrack - ML Experiment Tracking</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .experiment-card { border-left: 4px solid #0d6efd; }
        .metric-badge { font-size: 0.8rem; }
        .status-running { color: #ffc107; }
        .status-completed { color: #198754; }
        .status-failed { color: #dc3545; }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-5 bg-dark text-white mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">MLTrack</h1>
                <p class="lead mb-0">Open Source ML Experiment Tracking Platform</p>
                <p class="text-muted">v2.9.2</p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <!-- Experiments Column -->
            <div class="col-md-8">
                <h3 class="mb-4">Recent Experiments</h3>
                <?php foreach ($display_experiments as $experiment): ?>
                    <div class="card mb-4 experiment-card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                                <h5 class="card-title"><?= htmlspecialchars($experiment['name']); ?></h5>
                                <span class="badge bg-secondary"><?= htmlspecialchars($experiment['framework']); ?></span>
                            </div>
                            <p class="card-text text-muted"><?= htmlspecialchars($experiment['description']); ?></p>
                            <div class="mb-2">
                                <span class="metric-badge badge bg-info me-2">Accuracy: <?= htmlspecialchars($experiment['accuracy']); ?></span>
                                <span class="metric-badge badge bg-warning text-dark me-2">Loss: <?= htmlspecialchars($experiment['loss']); ?></span>
                                <span class="metric-badge badge bg-success">Epochs: <?= htmlspecialchars($experiment['epochs']); ?></span>
                            </div>
                            <small class="text-muted">Experiment ID: <?= htmlspecialchars($experiment['id']); ?></small>
                            <div class="mt-2">
                                <a href="experiment.php?id=<?= htmlspecialchars($experiment['id']); ?>" class="btn btn-sm btn-outline-primary">View Details</a>
                                <a href="artifacts.php?experiment_id=<?= htmlspecialchars($experiment['id']); ?>" class="btn btn-sm btn-outline-secondary">View Artifacts</a>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>

                <!-- Pagination -->
                <ul class="pagination justify-content-center mb-4">
                    <?php for ($i = 1; $i <= $total_pages; $i++): ?>
                        <li class="page-item <?= ($i == $page) ? 'active' : ''; ?>">
                            <a class="page-link" href="?page=<?= $i; ?>"><?= $i; ?></a>
                        </li>
                    <?php endfor; ?>
                </ul>

            </div>

            <!-- Sidebar Widgets Column -->
            <? include("include/sidebar.php") ?>
        </div>
    </div>

    <!-- Bootstrap core JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>
