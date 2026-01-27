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
    <meta charset="UTF-8">
    <title>DataFlow ML Tracking Server</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .experiment-card { border-left: 4px solid #6c5ce7; }
        .api-badge { font-size: 0.75rem; }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <!-- Header -->
    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">DataFlow ML Tracking Server</h1>
                <p class="lead mb-0">Machine Learning Experiment Management Platform</p>
                <small class="text-muted">Version 2.9.2</small>
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
                            <h5 class="card-title"><?= htmlspecialchars($experiment['name']); ?></h5>
                            <p class="card-text"><?= htmlspecialchars($experiment['description']); ?></p>
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="badge bg-primary api-badge">Experiment ID: <?= htmlspecialchars($experiment['id']); ?></span>
                                <small class="text-muted">Artifact Location: <?= htmlspecialchars($experiment['artifact_location']); ?></small>
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
