<?php
// Read experiments from JSON
$json_data = file_get_contents('experiments.json');
$experiments = json_decode($json_data, true);

$experiment_id = isset($_GET['experiment_id']) ? $_GET['experiment_id'] : null;
$experiment = null;

foreach ($experiments as $exp) {
    if ($exp['id'] === $experiment_id) {
        $experiment = $exp;
        break;
    }
}

// Mock artifacts
$artifacts = [
    ['name' => 'model.pkl', 'size' => '15.6 MB', 'type' => 'Model'],
    ['name' => 'metrics.json', 'size' => '1.2 KB', 'type' => 'Metrics'],
    ['name' => 'params.yaml', 'size' => '512 B', 'type' => 'Parameters'],
    ['name' => 'requirements.txt', 'size' => '256 B', 'type' => 'Config'],
];
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>MLTrack - Artifacts</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <? include("include/navigation-bar.php") ?>

    <header class="py-4 bg-dark text-white mb-4">
        <div class="container">
            <h1>Artifacts</h1>
            <p class="lead"><?= $experiment ? htmlspecialchars($experiment['name']) : 'All Experiments'; ?></p>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <?php if ($experiment): ?>
                <div class="alert alert-info">
                    <strong>Artifact Location:</strong> <code><?= htmlspecialchars($experiment['artifact_location']); ?></code>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h5>Artifact Browser</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Type</th>
                                    <th>Size</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($artifacts as $artifact): ?>
                                <tr>
                                    <td><i class="bi bi-file-earmark"></i> <?= htmlspecialchars($artifact['name']); ?></td>
                                    <td><?= htmlspecialchars($artifact['type']); ?></td>
                                    <td><?= htmlspecialchars($artifact['size']); ?></td>
                                    <td>
                                        <a href="/api/preview-artifact.php?source=<?= urlencode($experiment['artifact_location'] . '/' . $artifact['name']); ?>" class="btn btn-sm btn-outline-primary">Preview</a>
                                        <button class="btn btn-sm btn-outline-secondary">Download</button>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="card mt-4">
                    <div class="card-header">API Access</div>
                    <div class="card-body">
                        <p>Download artifacts programmatically using the API:</p>
                        <pre class="bg-dark text-light p-3">curl -X GET "<?= $_SERVER['HTTP_HOST'] ?>/api/preview-artifact.php?source=file:///path/to/artifact"</pre>
                        <p class="text-muted">See <a href="/api/docs.php">API Documentation</a> for more details.</p>
                    </div>
                </div>
                <?php else: ?>
                <div class="alert alert-warning">
                    No experiment selected. <a href="/">Return to dashboard</a>
                </div>
                <?php endif; ?>
            </div>
            
            <div class="col-md-4">
                <? include("include/sidebar.php") ?>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
