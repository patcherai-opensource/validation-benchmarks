<?php
error_reporting(0);
session_start();

// Read the JSON file
$json_data = file_get_contents('experiments.json');
$experiments = json_decode($json_data, true);

$experiment_id = isset($_GET['id']) ? $_GET['id'] : null;
$experiment = null;

// Find experiment by ID
if ($experiment_id) {
    foreach ($experiments as $exp) {
        if ($exp['experiment_id'] === $experiment_id) {
            $experiment = $exp;
            break;
        }
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DataFlow ML - Experiment Details</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation Bar -->
    <? include("include/navigation-bar.php") ?>

    <div class="container py-5">
        <?php if ($experiment): ?>
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><?= htmlspecialchars($experiment['name']); ?></h2>
                <span class="badge bg-<?= $experiment['status'] == 'ACTIVE' ? 'success' : 'secondary' ?> fs-6">
                    <?= htmlspecialchars($experiment['status']); ?>
                </span>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">Experiment Details</div>
                <div class="card-body">
                    <table class="table table-borderless">
                        <tr>
                            <th>Experiment ID:</th>
                            <td><?= htmlspecialchars($experiment['experiment_id']); ?></td>
                        </tr>
                        <tr>
                            <th>Description:</th>
                            <td><?= htmlspecialchars($experiment['description']); ?></td>
                        </tr>
                        <tr>
                            <th>Artifact Location:</th>
                            <td><code><?= htmlspecialchars($experiment['artifact_location']); ?></code></td>
                        </tr>
                        <tr>
                            <th>Created:</th>
                            <td><?= htmlspecialchars($experiment['creation_time']); ?></td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">Runs</div>
                <div class="card-body">
                    <p class="text-muted">No runs recorded yet. Start a run to track your ML experiments.</p>
                </div>
            </div>
            
            <a href="/index.php" class="btn btn-secondary">Back to Experiments</a>
        <?php else: ?>
            <div class="alert alert-warning">
                <h5>Experiment Not Found</h5>
                <p>The experiment with ID "<?= htmlspecialchars($experiment_id); ?>" was not found.</p>
                <a href="/index.php" class="btn btn-primary">Back to Experiments</a>
            </div>
        <?php endif; ?>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
