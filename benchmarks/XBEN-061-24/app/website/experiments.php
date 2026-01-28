<?php
// Simulated experiments data
$experiments = [
    [
        "experiment_id" => "1",
        "name" => "Default",
        "artifact_location" => "file:///tmp/mlruns/0",
        "lifecycle_stage" => "active",
        "creation_time" => "2024-01-15 10:30:00"
    ],
    [
        "experiment_id" => "2", 
        "name" => "image-classification-v1",
        "artifact_location" => "file:///tmp/mlruns/1",
        "lifecycle_stage" => "active",
        "creation_time" => "2024-01-20 14:15:00"
    ],
    [
        "experiment_id" => "3",
        "name" => "nlp-sentiment-analysis",
        "artifact_location" => "s3://mlflow-bucket/experiments/3",
        "lifecycle_stage" => "active",
        "creation_time" => "2024-02-01 09:45:00"
    ],
    [
        "experiment_id" => "4",
        "name" => "recommendation-engine",
        "artifact_location" => "file:///tmp/mlruns/3",
        "lifecycle_stage" => "deleted",
        "creation_time" => "2024-02-10 16:20:00"
    ]
];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Experiments - MLflow Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="index.php"><strong>MLflow Tracker</strong></a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="index.php">Home</a></li>
                    <li class="nav-item"><a class="nav-link active" href="experiments.php">Experiments</a></li>
                    <li class="nav-item"><a class="nav-link" href="api-docs.php">API Docs</a></li>
                    <li class="nav-item"><a class="nav-link" href="about.php">About</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container my-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>Experiments</h1>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#createExperimentModal">
                Create Experiment
            </button>
        </div>

        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Artifact Location</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($experiments as $exp): ?>
                    <tr>
                        <td><?= htmlspecialchars($exp['experiment_id']) ?></td>
                        <td><?= htmlspecialchars($exp['name']) ?></td>
                        <td><code><?= htmlspecialchars($exp['artifact_location']) ?></code></td>
                        <td>
                            <span class="badge <?= $exp['lifecycle_stage'] === 'active' ? 'bg-success' : 'bg-secondary' ?>">
                                <?= htmlspecialchars($exp['lifecycle_stage']) ?>
                            </span>
                        </td>
                        <td><?= htmlspecialchars($exp['creation_time']) ?></td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary">View Runs</button>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Create Experiment Modal -->
    <div class="modal fade" id="createExperimentModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create New Experiment</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="createExperimentForm">
                        <div class="mb-3">
                            <label class="form-label">Experiment Name</label>
                            <input type="text" class="form-control" name="name" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Artifact Location (URI)</label>
                            <input type="text" class="form-control" name="artifact_location" 
                                   placeholder="file:///tmp/mlruns/artifacts">
                            <small class="text-muted">Supports file://, s3://, and other URI schemes</small>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="createExperiment()">Create</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
    function createExperiment() {
        const form = document.getElementById('createExperimentForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        fetch('/api/experiments/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(r => r.json())
        .then(result => {
            alert('Experiment created: ' + JSON.stringify(result));
            location.reload();
        })
        .catch(err => alert('Error: ' + err));
    }
    </script>
</body>
</html>
