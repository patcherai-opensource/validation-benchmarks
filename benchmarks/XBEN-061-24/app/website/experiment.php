<?php
// Read experiments from JSON
$json_data = file_get_contents('experiments.json');
$experiments = json_decode($json_data, true);

$experiment_id = isset($_GET['id']) ? $_GET['id'] : null;
$experiment = null;

foreach ($experiments as $exp) {
    if ($exp['id'] === $experiment_id) {
        $experiment = $exp;
        break;
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>MLTrack - Experiment Details</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <? include("include/navigation-bar.php") ?>

    <header class="py-4 bg-dark text-white mb-4">
        <div class="container">
            <h1>Experiment Details</h1>
            <p class="lead"><?= $experiment ? htmlspecialchars($experiment['name']) : 'Not Found'; ?></p>
        </div>
    </header>

    <div class="container">
        <?php if ($experiment): ?>
        <div class="row">
            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Experiment: <?= htmlspecialchars($experiment['id']); ?></h5>
                    </div>
                    <div class="card-body">
                        <table class="table">
                            <tr>
                                <th>Name</th>
                                <td><?= htmlspecialchars($experiment['name']); ?></td>
                            </tr>
                            <tr>
                                <th>Description</th>
                                <td><?= htmlspecialchars($experiment['description']); ?></td>
                            </tr>
                            <tr>
                                <th>Framework</th>
                                <td><?= htmlspecialchars($experiment['framework']); ?></td>
                            </tr>
                            <tr>
                                <th>Accuracy</th>
                                <td><?= htmlspecialchars($experiment['accuracy']); ?></td>
                            </tr>
                            <tr>
                                <th>Loss</th>
                                <td><?= htmlspecialchars($experiment['loss']); ?></td>
                            </tr>
                            <tr>
                                <th>Epochs</th>
                                <td><?= htmlspecialchars($experiment['epochs']); ?></td>
                            </tr>
                            <tr>
                                <th>Artifact Location</th>
                                <td><code><?= htmlspecialchars($experiment['artifact_location']); ?></code></td>
                            </tr>
                        </table>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">Runs</div>
                    <div class="card-body">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Run ID</th>
                                    <th>Status</th>
                                    <th>Start Time</th>
                                    <th>Duration</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>run-<?= substr(md5($experiment['id'] . '1'), 0, 8); ?></td>
                                    <td><span class="badge bg-success">FINISHED</span></td>
                                    <td>2024-01-15 14:32:00</td>
                                    <td>2h 15m</td>
                                </tr>
                                <tr>
                                    <td>run-<?= substr(md5($experiment['id'] . '2'), 0, 8); ?></td>
                                    <td><span class="badge bg-success">FINISHED</span></td>
                                    <td>2024-01-14 09:15:00</td>
                                    <td>1h 45m</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <? include("include/sidebar.php") ?>
            </div>
        </div>
        <?php else: ?>
        <div class="alert alert-warning">
            Experiment not found. <a href="/">Return to dashboard</a>
        </div>
        <?php endif; ?>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
