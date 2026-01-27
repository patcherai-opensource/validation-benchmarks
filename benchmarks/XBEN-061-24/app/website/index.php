<?php
// Read the JSON file
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
    <meta charset="UTF-8">
    <title>DataFlow ML - Experiment Tracking</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .navbar-brand { font-weight: bold; color: #0d6efd !important; }
        .experiment-card { transition: transform 0.2s; }
        .experiment-card:hover { transform: translateY(-5px); }
        .status-active { color: #28a745; }
        .status-completed { color: #6c757d; }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-5 bg-primary text-white mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">DataFlow ML Platform</h1>
                <p class="lead mb-0">Open Source Machine Learning Lifecycle Management</p>
                <p class="mt-2"><small>Version 2.11.2</small></p>
            </div>
        </div>
    </header>

    <!-- Main Content Section -->
    <div class="container">
        <div class="row">
            <!-- Experiments Column -->
            <div class="col-md-8">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h3>Experiments</h3>
                    <a href="api/experiments/create" class="btn btn-success">+ New Experiment</a>
                </div>
                
                <?php foreach ($display_experiments as $exp): ?>
                    <div class="card mb-4 experiment-card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h5 class="card-title"><?= htmlspecialchars($exp['name']); ?></h5>
                                    <p class="card-text text-muted"><?= htmlspecialchars($exp['description']); ?></p>
                                </div>
                                <span class="badge bg-<?= $exp['status'] == 'ACTIVE' ? 'success' : 'secondary' ?>"><?= htmlspecialchars($exp['status']); ?></span>
                            </div>
                            <div class="mt-3">
                                <small class="text-muted">
                                    <strong>Experiment ID:</strong> <?= htmlspecialchars($exp['experiment_id']); ?><br>
                                    <strong>Artifact Location:</strong> <code><?= htmlspecialchars($exp['artifact_location']); ?></code><br>
                                    <strong>Created:</strong> <?= htmlspecialchars($exp['creation_time']); ?>
                                </small>
                            </div>
                            <div class="mt-3">
                                <a href="experiment.php?id=<?= htmlspecialchars($exp['experiment_id']); ?>" class="btn btn-outline-primary btn-sm">View Runs</a>
                                <a href="api/artifacts/list?experiment_id=<?= htmlspecialchars($exp['experiment_id']); ?>" class="btn btn-outline-secondary btn-sm">List Artifacts</a>
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
