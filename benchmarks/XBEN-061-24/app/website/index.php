<?php
error_reporting(0);

$experiments_file = '/var/lib/mltrack/experiments.json';
if (!file_exists($experiments_file)) {
    $experiments = [];
} else {
    $experiments = json_decode(file_get_contents($experiments_file), true) ?: [];
}

$limit = 10;
$page = isset($_GET['page']) ? max(1, (int)$_GET['page']) : 1;
$total_experiments = count($experiments);
$total_pages = max(1, ceil($total_experiments / $limit));
$start = ($page - 1) * $limit;
$display_experiments = array_slice($experiments, $start, $limit);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MLTrack - Experiment Tracking Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</head>
<body>
    <?php include("include/navigation-bar.php") ?>

    <header class="py-5 bg-primary text-white mb-4">
        <div class="container">
            <div class="text-center my-4">
                <h1 class="fw-bolder"><i class="bi bi-graph-up"></i> MLTrack</h1>
                <p class="lead mb-0">Open Source Machine Learning Experiment Tracking</p>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>Experiments</h2>
                    <a href="experiments.php?action=create" class="btn btn-success"><i class="bi bi-plus-circle"></i> New Experiment</a>
                </div>

                <?php if (empty($display_experiments)): ?>
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> No experiments found. Create your first experiment to get started!
                </div>
                <?php else: ?>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Artifact Location</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($display_experiments as $exp): ?>
                            <tr>
                                <td><code><?= htmlspecialchars($exp['id']); ?></code></td>
                                <td><?= htmlspecialchars($exp['name']); ?></td>
                                <td><code><?= htmlspecialchars($exp['artifact_location']); ?></code></td>
                                <td><?= htmlspecialchars($exp['created_at']); ?></td>
                                <td>
                                    <a href="artifacts.php?experiment_id=<?= htmlspecialchars($exp['id']); ?>" class="btn btn-sm btn-outline-primary">
                                        <i class="bi bi-folder"></i> Artifacts
                                    </a>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>

                <?php if ($total_pages > 1): ?>
                <nav>
                    <ul class="pagination justify-content-center">
                        <?php for ($i = 1; $i <= $total_pages; $i++): ?>
                        <li class="page-item <?= ($i == $page) ? 'active' : ''; ?>">
                            <a class="page-link" href="?page=<?= $i; ?>"><?= $i; ?></a>
                        </li>
                        <?php endfor; ?>
                    </ul>
                </nav>
                <?php endif; ?>
                <?php endif; ?>
            </div>

            <?php include("include/sidebar.php") ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
